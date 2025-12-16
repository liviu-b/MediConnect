from fastapi import APIRouter, HTTPException, Response, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import httpx
import secrets
import os
import logging
import re

from passlib.context import CryptContext

from app.core.database import db
from app.services.email import send_password_reset_email
from app.api import deps

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)


class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class ClinicRegistration(BaseModel):
    cui: str
    admin_name: str
    admin_email: str
    admin_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_session(user_id: str, response: Response) -> str:
    session_token = f"session_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.delete_many({"user_id": user_id})
    session_doc = {
        "session_token": session_token,
        "user_id": user_id,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.user_sessions.insert_one(session_doc)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60,
    )
    return session_token


@router.post("/register")
async def register_user(data: UserRegister, response: Response):
    try:
        if len(data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        existing = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": data.email.lower(),
            "name": data.name,
            "phone": data.phone,
            "password_hash": hash_password(data.password),
            "auth_provider": "email",
            "role": "USER",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user_doc)
        session_token = await create_session(user_id, response)
        user_data = {k: v for k, v in user_doc.items() if k != 'password_hash'}
        return {"user": user_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@router.post("/login")
async def login_user(data: UserLogin, response: Response):
    try:
        user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user_doc.get('password_hash'):
            raise HTTPException(status_code=401, detail="Please use Google login for this account")
        if not verify_password(data.password, user_doc['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user_doc.get('is_active', True):
            raise HTTPException(status_code=401, detail="Account is disabled")
        session_token = await create_session(user_doc['user_id'], response)
        user_data = {k: v for k, v in user_doc.items() if k != 'password_hash'}
        role = user_doc.get('role', 'USER')
        if role == 'CLINIC_ADMIN':
            user_data['redirect_to'] = '/dashboard'
        elif role in ['DOCTOR', 'ASSISTANT']:
            user_data['redirect_to'] = '/staff-dashboard'
        else:
            user_data['redirect_to'] = '/dashboard'
        return {"user": user_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")


@router.post("/register-clinic")
async def register_clinic(data: ClinicRegistration, response: Response):
    try:
        cui_clean = data.cui.strip()
        if not re.match(r'^\d{2,10}$', cui_clean):
            raise HTTPException(status_code=400, detail="CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre.")
        if len(data.admin_password) < 8:
            raise HTTPException(status_code=400, detail="Parola trebuie sa aiba minim 8 caractere.")
        existing_clinic = await db.clinics.find_one({"cui": cui_clean}, {"_id": 0})
        if existing_clinic:
            raise HTTPException(status_code=400, detail="Acest CUI este deja inregistrat.")
        existing_user = await db.users.find_one({"email": data.admin_email.lower()}, {"_id": 0})
        if existing_user:
            raise HTTPException(status_code=400, detail="Aceasta adresa de email este deja inregistrata.")
        clinic_id = f"clinic_{uuid.uuid4().hex[:12]}"
        clinic_doc = {
            "clinic_id": clinic_id,
            "cui": cui_clean,
            "is_verified": True,
            "is_profile_complete": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.clinics.insert_one(clinic_doc)
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        admin_user_doc = {
            "user_id": user_id,
            "email": data.admin_email.lower(),
            "name": data.admin_name,
            "password_hash": hash_password(data.admin_password),
            "auth_provider": "email",
            "role": "CLINIC_ADMIN",
            "clinic_id": clinic_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(admin_user_doc)
        session_token = await create_session(user_id, response)
        user_data = {k: v for k, v in admin_user_doc.items() if k not in ("password_hash", "_id")}
        clinic_data = {k: v for k, v in clinic_doc.items() if k != "_id"}
        return {"user": user_data, "clinic": clinic_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clinic registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@router.post("/session")
async def create_oauth_session(request: Request, response: Response):
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")
    async with httpx.AsyncClient() as client_http:
        try:
            auth_response = await client_http.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session ID")
            user_data = auth_response.json()
        except Exception as e:
            logger.error(f"Auth service error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")

    existing_user = await db.users.find_one({"email": user_data["email"].lower()}, {"_id": 0})
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": user_data["name"], "picture": user_data.get("picture")}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = {
            "user_id": user_id,
            "email": user_data["email"].lower(),
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "auth_provider": "google",
            "role": "USER",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(new_user)

    session_token = await create_session(user_id, response)
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    user_data_clean = {k: v for k, v in user_doc.items() if k != 'password_hash'}
    return {"user": user_data_clean, "session_token": session_token}


@router.get("/me")
async def get_me(request: Request):
    user = await deps.get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_dict = dict(user)
    user_dict.pop('password_hash', None)
    if user.get("role") == "CLINIC_ADMIN" and user.get("clinic_id"):
        clinic = await db.clinics.find_one({"clinic_id": user["clinic_id"]}, {"_id": 0})
        user_dict['clinic'] = clinic
    return user_dict


@router.put("/profile")
async def update_profile(data: dict, request: Request):
    user = await deps.require_auth(request)
    update_data = {}
    for key in ("name", "phone", "address", "date_of_birth"):
        if key in data and data[key] is not None:
            update_data[key] = data[key]
    if update_data:
        await db.users.update_one({"user_id": user["user_id"]}, {"$set": update_data})
        updated_user = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0, "password_hash": 0})
        return updated_user
    raise HTTPException(status_code=400, detail="No data to update")


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
        response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not user_doc:
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    if user_doc.get('auth_provider') == 'google':
        return {"message": "If an account exists with this email, a password reset link has been sent."}

    await db.password_reset_tokens.delete_many({"user_id": user_doc['user_id']})
    token = f"reset_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    token_doc = {
        "token": token,
        "user_id": user_doc['user_id'],
        "email": data.email.lower(),
        "expires_at": expires_at.isoformat(),
        "used": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.password_reset_tokens.insert_one(token_doc)

    medical_center = None
    if user_doc.get('clinic_id'):
        medical_center = await db.clinics.find_one({"clinic_id": user_doc['clinic_id']}, {"_id": 0})

    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?token={token}"
    background_tasks.add_task(
        send_password_reset_email,
        recipient_email=data.email.lower(),
        recipient_name=user_doc.get('name', 'User'),
        reset_link=reset_link,
        medical_center=medical_center,
    )
    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    token_doc = await db.password_reset_tokens.find_one({"token": data.token, "used": False}, {"_id": 0})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    expires_at = token_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    new_password_hash = hash_password(data.new_password)
    await db.users.update_one({"user_id": token_doc["user_id"]}, {"$set": {"password_hash": new_password_hash}})
    await db.password_reset_tokens.update_one({"token": data.token}, {"$set": {"used": True}})
    return {"message": "Password has been reset successfully"}


@router.post("/validate-cui")
async def validate_cui(cui: str):
    cui_clean = cui.strip()
    if not re.match(r'^\d{2,10}$', cui_clean):
        return {"valid": False, "available": False, "message": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."}
    existing = await db.clinics.find_one({"cui": cui_clean}, {"_id": 0})
    if existing:
        return {"valid": True, "available": False, "message": "Acest CUI este deja inregistrat."}
    return {"valid": True, "available": True, "message": "CUI disponibil pentru inregistrare."}
