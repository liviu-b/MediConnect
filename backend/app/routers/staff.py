from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import secrets
import os

from app.core.database import db
from app.api import deps
from app.services.email import send_staff_invitation_email

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class AcceptInvitationRequest(BaseModel):
    token: str
    password: str


@router.get("")
async def get_staff(request: Request):
    user = await deps.require_clinic_admin(request)
    staff = await db.staff.find({"clinic_id": user["clinic_id"], "is_active": True}, {"_id": 0}).to_list(100)
    return staff


@router.post("")
async def create_staff(data: StaffCreate, request: Request, background_tasks: BackgroundTasks):
    user = await deps.require_clinic_admin(request)

    existing_user = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered in the system")

    existing_staff = await db.staff.find_one({"email": data.email.lower(), "clinic_id": user["clinic_id"], "is_active": True}, {"_id": 0})
    if existing_staff:
        raise HTTPException(status_code=400, detail="A staff member with this email already exists")

    invitation_token = f"invite_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    staff_doc = {
        "staff_id": f"staff_{datetime.now(timezone.utc).timestamp()}",
        "clinic_id": user["clinic_id"],
        "name": data.name,
        "email": data.email.lower(),
        "phone": data.phone,
        "role": data.role,
        "is_active": True,
        "invitation_status": "PENDING",
        "invitation_token": invitation_token,
        "invitation_expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_id": None,
    }
    await db.staff.insert_one(staff_doc)

    clinic = await db.clinics.find_one({"clinic_id": user["clinic_id"]}, {"_id": 0})
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=data.email.lower(),
        recipient_name=data.name,
        role=data.role,
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.get('name', 'Admin'),
    )

    staff_doc.pop("_id", None)
    return staff_doc


@router.post("/{staff_id}/resend-invitation")
async def resend_staff_invitation(staff_id: str, request: Request, background_tasks: BackgroundTasks):
    user = await deps.require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user["clinic_id"]}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")

    new_token = f"invite_{secrets.token_hex(32)}"
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.staff.update_one(
        {"staff_id": staff_id},
        {"$set": {"invitation_token": new_token, "invitation_expires_at": new_expires_at.isoformat()}}
    )

    clinic = await db.clinics.find_one({"clinic_id": user["clinic_id"]}, {"_id": 0})
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    invitation_link = f"{frontend_url}/accept-invitation?token={new_token}"
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=staff['email'],
        recipient_name=staff['name'],
        role=staff['role'],
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.get('name', 'Admin'),
    )
    return {"message": "Invitation resent successfully"}


@router.get("/invitation/{token}")
async def get_invitation_details(token: str):
    staff = await db.staff.find_one({"invitation_token": token}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")

    expires_at = staff.get('invitation_expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Invitation has expired")

    clinic = await db.clinics.find_one({"clinic_id": staff['clinic_id']}, {"_id": 0})
    return {
        "name": staff['name'],
        "email": staff['email'],
        "role": staff['role'],
        "clinic_name": clinic.get('name', 'Medical Center') if clinic else 'Medical Center'
    }


@router.post("/accept-invitation")
async def accept_staff_invitation(data: AcceptInvitationRequest, response: Response):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    staff = await db.staff.find_one({"invitation_token": data.token}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")

    expires_at = staff.get('invitation_expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Invitation has expired")

    existing_user = await db.users.find_one({"email": staff['email']}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered")

    def hash_password(p: str) -> str:
        return pwd_context.hash(p)

    user_role = "ASSISTANT"
    if staff['role'] == 'DOCTOR':
        user_role = "DOCTOR"
    elif staff['role'] in ['ADMIN', 'RECEPTIONIST', 'NURSE']:
        user_role = "ASSISTANT"

    user_id = f"user_{datetime.now(timezone.utc).timestamp()}"
    new_user = {
        "user_id": user_id,
        "email": staff['email'],
        "name": staff['name'],
        "phone": staff.get('phone'),
        "password_hash": hash_password(data.password),
        "auth_provider": "email",
        "role": user_role,
        "clinic_id": staff['clinic_id'],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }
    await db.users.insert_one(new_user)

    await db.staff.update_one(
        {"staff_id": staff['staff_id']},
        {"$set": {
            "invitation_status": "ACCEPTED",
            "invitation_token": None,
            "invitation_expires_at": None,
            "user_id": user_id
        }}
    )

    # Create session via auth route helper
    from app.routers.auth import create_session
    await create_session(user_id, response)

    user_data = {k: v for k, v in new_user.items() if k not in ("password_hash", "_id")}
    user_data['redirect_to'] = '/staff-dashboard'
    return {"user": user_data, "session_token": response.headers.get('set-cookie')}


@router.put("/{staff_id}")
async def update_staff(staff_id: str, data: StaffUpdate, request: Request):
    user = await deps.require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user["clinic_id"]}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

    if staff.get('user_id') and data.role is not None:
        user_role = "ASSISTANT"
        if data.role == 'DOCTOR':
            user_role = "DOCTOR"
        await db.users.update_one({"user_id": staff['user_id']}, {"$set": {"role": user_role}})

    if update_data:
        await db.staff.update_one({"staff_id": staff_id}, {"$set": update_data})
    updated = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    return updated


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str, request: Request):
    user = await deps.require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    if not staff or staff["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=404, detail="Staff not found")

    await db.staff.update_one({"staff_id": staff_id}, {"$set": {"is_active": False}})
    if staff.get('user_id'):
        await db.users.update_one({"user_id": staff['user_id']}, {"$set": {"is_active": False}})
    return {"message": "Staff removed successfully"}
