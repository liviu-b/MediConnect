from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
import uuid
import httpx
import re
from ..db import db
from ..schemas.user import User, UserRegister, UserLogin, UserUpdate, ForgotPasswordRequest, ResetPasswordRequest, PasswordResetToken
from ..schemas.clinic import Clinic, ClinicRegistration
from ..security import hash_password, verify_password, create_session, get_current_user, require_auth
from ..config import FRONTEND_URL
from ..services.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

# Add OPTIONS handler for CORS preflight
@router.options("/login")
@router.options("/register")
@router.options("/register-clinic")
@router.options("/session")
@router.options("/me")
@router.options("/profile")
@router.options("/logout")
@router.options("/forgot-password")
@router.options("/reset-password")
@router.options("/validate-cui")
async def options_handler():
    return Response(status_code=200)


@router.post("/register")
async def register_user(data: UserRegister, response: Response):
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    existing = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user = User(
        user_id=user_id,
        email=data.email.lower(),
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        auth_provider="email",
        role="USER"
    )
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    session_token = await create_session(user_id, response)
    user_data = {k: v for k, v in doc.items() if k != 'password_hash' and k != '_id'}
    return {"user": user_data, "session_token": session_token}


@router.post("/login")
async def login_user(data: UserLogin, response: Response):
    user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not user_doc or not user_doc.get('password_hash') or not verify_password(data.password, user_doc['password_hash']):
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


@router.post("/register-clinic")
async def register_clinic(data: ClinicRegistration, response: Response):
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
    clinic = Clinic(
        clinic_id=clinic_id,
        cui=cui_clean,
        is_verified=True,
        is_profile_complete=False
    )
    clinic_doc = clinic.model_dump()
    clinic_doc['created_at'] = clinic_doc['created_at'].isoformat()
    await db.clinics.insert_one(clinic_doc)
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    admin_user = User(
        user_id=user_id,
        email=data.admin_email.lower(),
        name=data.admin_name,
        password_hash=hash_password(data.admin_password),
        auth_provider="email",
        role="CLINIC_ADMIN",
        clinic_id=clinic_id
    )
    user_doc = admin_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    session_token = await create_session(user_id, response)
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    clinic_data = {k: v for k, v in clinic_doc.items() if k != '_id'}
    return {"user": user_data, "clinic": clinic_data, "session_token": session_token}


@router.post("/session")
async def create_oauth_session(request: Request, response: Response):
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")
    async with httpx.AsyncClient() as client_http:
        auth_response = await client_http.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session ID")
        user_data = auth_response.json()
    existing_user = await db.users.find_one({"email": user_data["email"].lower()}, {"_id": 0})
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one({"user_id": user_id},
                                  {"$set": {"name": user_data["name"], "picture": user_data.get("picture")}})
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = User(
            user_id=user_id,
            email=user_data["email"].lower(),
            name=user_data["name"],
            picture=user_data.get("picture"),
            auth_provider="google",
            role="USER"
        )
        doc = new_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    session_token = await create_session(user_id, response)
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    user_data_clean = {k: v for k, v in user_doc.items() if k != 'password_hash'}
    return {"user": user_data_clean, "session_token": session_token}


@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_dict = user.model_dump()
    user_dict.pop('password_hash', None)
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        user_dict['clinic'] = clinic
    return user_dict


@router.put("/profile")
async def update_profile(data: UserUpdate, request: Request):
    user = await require_auth(request)
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.address is not None:
        update_data["address"] = data.address
    if data.date_of_birth is not None:
        update_data["date_of_birth"] = data.date_of_birth
    if update_data:
        await db.users.update_one({"user_id": user.user_id}, {"$set": update_data})
    updated_user = await db.users.find_one({"user_id": user.user_id}, {"_id": 0, "password_hash": 0})
    return updated_user


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    from ..security import IS_PRODUCTION
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=IS_PRODUCTION,
        samesite="none" if IS_PRODUCTION else "lax"
    )
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not user_doc or user_doc.get('auth_provider') == 'google':
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    await db.password_reset_tokens.delete_many({"user_id": user_doc['user_id']})
    token = f"reset_{uuid.uuid4().hex}{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    reset_token = PasswordResetToken(
        token=token,
        user_id=user_doc['user_id'],
        email=data.email.lower(),
        expires_at=expires_at
    )
    token_doc = reset_token.model_dump()
    token_doc['expires_at'] = token_doc['expires_at'].isoformat()
    token_doc['created_at'] = token_doc['created_at'].isoformat()
    await db.password_reset_tokens.insert_one(token_doc)
    medical_center = None
    if user_doc.get('clinic_id'):
        medical_center = await db.clinics.find_one({"clinic_id": user_doc['clinic_id']}, {"_id": 0})
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token.token}"
    background_tasks.add_task(
        send_password_reset_email,
        recipient_email=data.email.lower(),
        recipient_name=user_doc.get('name', 'User'),
        reset_link=reset_link,
        medical_center=medical_center
    )
    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    token_doc = await db.password_reset_tokens.find_one({"token": data.token, "used": False}, {"_id": 0})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    expires_at = token_doc["expires_at"]
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
