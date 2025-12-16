from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
import secrets

from ..db import db
from ..schemas.staff import StaffMember, StaffCreate, StaffUpdate
from ..schemas.user import User
from ..security import require_clinic_admin, create_session, hash_password
from ..services.email import send_staff_invitation_email

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("")
async def get_staff(request: Request):
    user = await require_clinic_admin(request)
    staff = await db.staff.find({"clinic_id": user.clinic_id, "is_active": True}, {"_id": 0}).to_list(100)
    return staff


@router.post("")
async def create_staff(data: StaffCreate, request: Request, background_tasks: BackgroundTasks):
    user = await require_clinic_admin(request)
    existing_user = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered in the system")
    existing_staff = await db.staff.find_one({"email": data.email.lower(), "clinic_id": user.clinic_id, "is_active": True}, {"_id": 0})
    if existing_staff:
        raise HTTPException(status_code=400, detail="A staff member with this email already exists")
    invitation_token = f"invite_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    staff = StaffMember(
        clinic_id=user.clinic_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        role=data.role,
        invitation_status="PENDING",
        invitation_token=invitation_token,
        invitation_expires_at=expires_at
    )
    doc = staff.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['invitation_expires_at'] = doc['invitation_expires_at'].isoformat() if doc['invitation_expires_at'] else None
    await db.staff.insert_one(doc)
    clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
    frontend_url = "http://localhost:3000"
    invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=data.email.lower(),
        recipient_name=data.name,
        role=data.role,
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.name
    )
    return staff


@router.post("/{staff_id}/resend-invitation")
async def resend_staff_invitation(staff_id: str, request: Request, background_tasks: BackgroundTasks):
    user = await require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user.clinic_id}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    new_token = f"invite_{secrets.token_hex(32)}"
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.staff.update_one(
        {"staff_id": staff_id},
        {"$set": {
            "invitation_token": new_token,
            "invitation_expires_at": new_expires_at.isoformat()
        }}
    )
    clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
    frontend_url = "http://localhost:3000"
    invitation_link = f"{frontend_url}/accept-invitation?token={new_token}"
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=staff['email'],
        recipient_name=staff['name'],
        role=staff['role'],
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.name
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
async def accept_staff_invitation(data: dict, response: Response):
    token = data.get("token", "")
    password = data.get("password", "")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
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
    existing_user = await db.users.find_one({"email": staff['email']}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered")
    user_role = "ASSISTANT"
    if staff['role'] == 'DOCTOR':
        user_role = "DOCTOR"
    elif staff['role'] in ['ADMIN', 'RECEPTIONIST', 'NURSE']:
        user_role = "ASSISTANT"
    user_id = f"user_{secrets.token_hex(12)}"
    new_user = User(
        user_id=user_id,
        email=staff['email'],
        name=staff['name'],
        phone=staff.get('phone'),
        password_hash=hash_password(password),
        auth_provider="email",
        role=user_role,
        clinic_id=staff['clinic_id']
    )
    user_doc = new_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    await db.staff.update_one(
        {"staff_id": staff['staff_id']},
        {"$set": {
            "invitation_status": "ACCEPTED",
            "invitation_token": None,
            "invitation_expires_at": None,
            "user_id": user_id
        }}
    )
    session_token = await create_session(user_id, response)
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    user_data['redirect_to'] = '/staff-dashboard'
    return {"user": user_data, "session_token": session_token}


@router.put("/{staff_id}")
async def update_staff(staff_id: str, data: StaffUpdate, request: Request):
    user = await require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user.clinic_id}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.role is not None:
        update_data["role"] = data.role
        if staff.get('user_id'):
            user_role = "ASSISTANT"
            if data.role == 'DOCTOR':
                user_role = "DOCTOR"
            await db.users.update_one({"user_id": staff['user_id']}, {"$set": {"role": user_role}})
    if update_data:
        await db.staff.update_one(
            {"staff_id": staff_id},
            {"$set": update_data}
        )
    updated_staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    return updated_staff


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str, request: Request):
    user = await require_clinic_admin(request)
    staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    if not staff or staff["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Staff not found")
    await db.staff.update_one({"staff_id": staff_id}, {"$set": {"is_active": False}})
    if staff.get('user_id'):
        await db.users.update_one({"user_id": staff['user_id']}, {"$set": {"is_active": False}})
    return {"message": "Staff removed successfully"}
