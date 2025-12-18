from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, Request, Response
from passlib.context import CryptContext
import secrets
import os

from .db import db
from .schemas.user import User, UserSession

ENV = os.environ.get("ENV", "development")
IS_PRODUCTION = ENV == "production"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(request: Request) -> Optional[User]:
    session_token = request.cookies.get("session_token")

    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ", 1)[1]

    if not session_token:
        return None

    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0},
    )
    if not session_doc:
        return None

    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        await db.user_sessions.delete_one({"session_token": session_token})
        return None

    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0},
    )
    if not user_doc:
        return None

    return User(**user_doc)


async def require_auth(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_clinic_admin(request: Request) -> User:
    user = await require_auth(request)
    if user.role != "CLINIC_ADMIN":
        raise HTTPException(status_code=403, detail="Clinic admin access required")
    return user


async def require_staff_or_admin(request: Request) -> User:
    user = await require_auth(request)
    if user.role not in {"CLINIC_ADMIN", "DOCTOR", "ASSISTANT"}:
        raise HTTPException(status_code=403, detail="Staff or admin access required")
    return user


async def create_session(user_id: str, response: Response) -> str:
    session_token = f"session_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    await db.user_sessions.delete_many({"user_id": user_id})

    session = UserSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at,
    )

    session_doc = session.model_dump()
    session_doc["expires_at"] = session_doc["expires_at"].isoformat()
    session_doc["created_at"] = session_doc["created_at"].isoformat()

    await db.user_sessions.insert_one(session_doc)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="none" if IS_PRODUCTION else "lax",
        path="/",
        max_age=7 * 24 * 60 * 60,
    )

    return session_token
