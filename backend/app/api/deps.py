from fastapi import HTTPException, Request
from typing import Optional, Dict
from datetime import datetime, timezone

from app.core.database import db


async def get_current_user(request: Request) -> Optional[Dict]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    if not session_token:
        return None

    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        return None

    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except Exception:
            return None
    if expires_at is None or (expires_at.tzinfo is None):
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None

    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    return user_doc or None


async def require_auth(request: Request) -> Dict:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_clinic_admin(request: Request) -> Dict:
    user = await require_auth(request)
    if user.get("role") != "CLINIC_ADMIN":
        raise HTTPException(status_code=403, detail="Clinic admin access required")
    return user


async def require_staff_or_admin(request: Request) -> Dict:
    user = await require_auth(request)
    if user.get("role") not in ["CLINIC_ADMIN", "DOCTOR", "ASSISTANT"]:
        raise HTTPException(status_code=403, detail="Staff or admin access required")
    return user
