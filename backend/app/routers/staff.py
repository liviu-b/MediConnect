from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
import secrets

from ..db import db
from ..schemas.staff import StaffMember, StaffCreate, StaffUpdate
from ..schemas.user import User
from ..security import get_current_user, create_session, hash_password
from ..services.email import send_staff_invitation_email
from ..config import FRONTEND_URL

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("")
async def get_staff(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user can view staff
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "CLINIC_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to view staff")
    
    # Build query based on user role
    query = {"is_active": True}
    if user.role == "SUPER_ADMIN" and user.organization_id:
        query["organization_id"] = user.organization_id
    elif user.role == "LOCATION_ADMIN" and user.assigned_location_ids:
        query["assigned_location_ids"] = {"$in": user.assigned_location_ids}
    elif user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    
    staff = await db.staff.find(query, {"_id": 0}).to_list(100)
    return staff


@router.post("")
async def create_staff(data: StaffCreate, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user can create staff
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "CLINIC_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to create staff")
    
    # Check for existing user
    existing_user = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered in the system")
    
    # Check for existing staff
    existing_query = {"email": data.email.lower(), "is_active": True}
    if user.organization_id:
        existing_query["organization_id"] = user.organization_id
    elif user.clinic_id:
        existing_query["clinic_id"] = user.clinic_id
    
    existing_staff = await db.staff.find_one(existing_query, {"_id": 0})
    if existing_staff:
        raise HTTPException(status_code=400, detail="A staff member with this email already exists")
    
    # Get location_id from request body (sent from frontend form)
    location_id = data.location_id if hasattr(data, 'location_id') else None
    
    if not location_id:
        # Fallback: try header
        location_id = request.headers.get("x-location-id")
    
    if not location_id:
        if user.role == "SUPER_ADMIN":
            # Get first location in organization as fallback
            location = await db.locations.find_one(
                {"organization_id": user.organization_id, "is_active": True},
                {"_id": 0}
            )
            if location:
                location_id = location["location_id"]
            else:
                raise HTTPException(status_code=400, detail="No location found. Please create a location first.")
        elif user.role == "LOCATION_ADMIN":
            if user.assigned_location_ids:
                location_id = user.assigned_location_ids[0]
    
    # Create invitation
    invitation_token = f"invite_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Build staff data
    staff_data = {
        "name": data.name,
        "email": data.email.lower(),
        "phone": data.phone,
        "role": data.role,
        "invitation_status": "PENDING",
        "invitation_token": invitation_token,
        "invitation_expires_at": expires_at
    }
    
    # Add organization/location IDs for new system
    if user.organization_id:
        staff_data["organization_id"] = user.organization_id
    if location_id:
        staff_data["assigned_location_ids"] = [location_id]
    
    # Add clinic_id for legacy system
    if user.clinic_id:
        staff_data["clinic_id"] = user.clinic_id
    
    staff = StaffMember(**staff_data)
    doc = staff.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['invitation_expires_at'] = doc['invitation_expires_at'].isoformat() if doc['invitation_expires_at'] else None
    await db.staff.insert_one(doc)
    
    # Get organization/clinic name for email
    org_name = "Medical Center"
    if user.organization_id:
        org = await db.organizations.find_one({"organization_id": user.organization_id}, {"_id": 0})
        if org:
            org_name = org.get('name', 'Medical Center')
    elif user.clinic_id:
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        if clinic:
            org_name = clinic.get('name', 'Medical Center')
    
    invitation_link = f"{FRONTEND_URL}/accept-invitation?token={invitation_token}"
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=data.email.lower(),
        recipient_name=data.name,
        role=data.role,
        invitation_link=invitation_link,
        clinic_name=org_name,
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
    # Map staff role to user role
    if staff['role'] == 'LOCATION_ADMIN':
        user_role = "LOCATION_ADMIN"
    elif staff['role'] == 'DOCTOR':
        user_role = "DOCTOR"
    elif staff['role'] == 'RECEPTIONIST':
        user_role = "RECEPTIONIST"
    elif staff['role'] in ['ADMIN', 'NURSE']:
        user_role = "ASSISTANT"
    else:
        user_role = "ASSISTANT"
    user_id = f"user_{secrets.token_hex(12)}"
    
    # Build user data with organization and location info
    user_data_dict = {
        "user_id": user_id,
        "email": staff['email'],
        "name": staff['name'],
        "phone": staff.get('phone'),
        "password_hash": hash_password(password),
        "auth_provider": "email",
        "role": user_role,
    }
    
    # Add organization/location IDs from staff record
    if staff.get('organization_id'):
        user_data_dict["organization_id"] = staff['organization_id']
    if staff.get('assigned_location_ids'):
        user_data_dict["assigned_location_ids"] = staff['assigned_location_ids']
    
    # Add clinic_id for legacy system
    if staff.get('clinic_id'):
        user_data_dict["clinic_id"] = staff['clinic_id']
    
    new_user = User(**user_data_dict)
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
    
    # Determine redirect based on role
    if user_role == "DOCTOR":
        # Redirect doctors to complete their profile
        user_data['redirect_to'] = '/complete-doctor-profile'
        user_data['dashboard_type'] = 'doctor_setup'
    elif user_role == "LOCATION_ADMIN":
        # Redirect Location Admin to Settings page
        user_data['redirect_to'] = '/settings'
        user_data['dashboard_type'] = 'location_admin'
    else:
        # Other staff go to staff dashboard
        user_data['redirect_to'] = '/staff-dashboard'
        user_data['dashboard_type'] = 'staff'
    
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
