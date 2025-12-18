from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
import uuid
import re

from ..db import db
from ..schemas.organization import (
    Organization, 
    OrganizationCreate, 
    OrganizationUpdate,
    OrganizationRegistration
)
from ..schemas.location import Location, LocationCreate
from ..schemas.user import User
from ..schemas.access_request import AccessRequest, AccessRequestCreate
from ..security import hash_password, create_session, get_current_user, require_auth
from ..services.email import send_password_reset_email

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/register")
async def register_organization(data: OrganizationRegistration, response: Response, background_tasks: BackgroundTasks):
    """
    Register a new organization with CUI validation.
    If CUI exists, create an access request instead.
    """
    # Validate CUI format
    cui_clean = data.cui.strip()
    if not re.match(r'^\d{2,10}$', cui_clean):
        raise HTTPException(
            status_code=400, 
            detail="CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
        )
    
    # Validate password
    if len(data.admin_password) < 8:
        raise HTTPException(
            status_code=400, 
            detail="Parola trebuie sa aiba minim 8 caractere."
        )
    
    # Check if CUI already exists
    existing_org = await db.organizations.find_one({"cui": cui_clean}, {"_id": 0})
    
    if existing_org:
        # CUI exists - create access request instead
        existing_user = await db.users.find_one({"email": data.admin_email.lower()}, {"_id": 0})
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="Aceasta adresa de email este deja inregistrata."
            )
        
        # Create access request
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        access_request = AccessRequest(
            request_id=request_id,
            organization_id=existing_org['organization_id'],
            cui=cui_clean,
            requester_name=data.admin_name,
            requester_email=data.admin_email.lower(),
            requester_phone=data.admin_phone,
            proposed_location_name=data.location_name,
            proposed_location_city=data.location_city,
            status="PENDING"
        )
        
        request_doc = access_request.model_dump()
        request_doc['created_at'] = request_doc['created_at'].isoformat()
        request_doc['expires_at'] = request_doc['expires_at'].isoformat()
        
        # Store password hash temporarily (will be used when approved)
        request_doc['password_hash'] = hash_password(data.admin_password)
        
        await db.access_requests.insert_one(request_doc)
        
        # TODO: Send notification to super admins
        # background_tasks.add_task(notify_super_admins, existing_org, access_request)
        
        return {
            "status": "access_request_created",
            "message": "Acest CUI este deja inregistrat. O cerere de acces a fost trimisa catre administratorii organizatiei.",
            "request_id": request_id,
            "organization_name": existing_org.get('name', 'Organizatia')
        }
    
    # CUI doesn't exist - create new organization
    existing_user = await db.users.find_one({"email": data.admin_email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Aceasta adresa de email este deja inregistrata."
        )
    
    # Create organization
    organization_id = f"org_{uuid.uuid4().hex[:12]}"
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    organization = Organization(
        organization_id=organization_id,
        cui=cui_clean,
        name=data.organization_name or data.location_name,
        phone=data.location_phone,
        super_admin_ids=[user_id],
        is_verified=True
    )
    
    org_doc = organization.model_dump()
    org_doc['created_at'] = org_doc['created_at'].isoformat()
    await db.organizations.insert_one(org_doc)
    
    # Create first location
    location_id = f"loc_{uuid.uuid4().hex[:12]}"
    location = Location(
        location_id=location_id,
        organization_id=organization_id,
        name=data.location_name,
        address=data.location_address,
        city=data.location_city,
        county=data.location_county,
        phone=data.location_phone,
        is_primary=True
    )
    
    location_doc = location.model_dump()
    location_doc['created_at'] = location_doc['created_at'].isoformat()
    await db.locations.insert_one(location_doc)
    
    # Create super admin user
    admin_user = User(
        user_id=user_id,
        email=data.admin_email.lower(),
        name=data.admin_name,
        phone=data.admin_phone,
        password_hash=hash_password(data.admin_password),
        auth_provider="email",
        role="SUPER_ADMIN",
        organization_id=organization_id,
        assigned_location_ids=None  # Super admin has access to all locations
    )
    
    user_doc = admin_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    
    # Create session
    session_token = await create_session(user_id, response)
    
    # Return response
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    org_data = {k: v for k, v in org_doc.items() if k != '_id'}
    location_data = {k: v for k, v in location_doc.items() if k != '_id'}
    
    return {
        "status": "success",
        "user": user_data,
        "organization": org_data,
        "location": location_data,
        "session_token": session_token
    }


@router.get("/me")
async def get_my_organization(request: Request):
    """Get the organization details for the current user"""
    user = await require_auth(request)
    
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not associated with an organization")
    
    organization = await db.organizations.find_one(
        {"organization_id": user.organization_id}, 
        {"_id": 0}
    )
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get all locations for this organization
    locations = await db.locations.find(
        {"organization_id": user.organization_id, "is_active": True},
        {"_id": 0}
    ).to_list(100)
    
    organization['locations'] = locations
    
    return organization


@router.put("/me")
async def update_my_organization(data: OrganizationUpdate, request: Request):
    """Update organization details (Super Admin only)"""
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admins can update organization details")
    
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not associated with an organization")
    
    # Build update data
    update_data = {}
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.organizations.update_one(
            {"organization_id": user.organization_id},
            {"$set": update_data}
        )
    
    # Return updated organization
    updated_org = await db.organizations.find_one(
        {"organization_id": user.organization_id},
        {"_id": 0}
    )
    
    return updated_org


@router.get("/{organization_id}")
async def get_organization(organization_id: str, request: Request):
    """Get organization by ID (authenticated users only)"""
    user = await require_auth(request)
    
    organization = await db.organizations.find_one(
        {"organization_id": organization_id},
        {"_id": 0}
    )
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user has access to this organization
    if user.organization_id != organization_id and user.role != "USER":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return organization


@router.post("/validate-cui")
async def validate_cui(cui: str):
    """
    Validate CUI format and check availability.
    Returns whether CUI is valid and if it's already registered.
    """
    cui_clean = cui.strip()
    
    if not re.match(r'^\d{2,10}$', cui_clean):
        return {
            "valid": False,
            "available": False,
            "message": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
        }
    
    existing = await db.organizations.find_one({"cui": cui_clean}, {"_id": 0})
    
    if existing:
        return {
            "valid": True,
            "available": False,
            "registered": True,
            "organization_name": existing.get('name', 'Organizatie existenta'),
            "message": "Acest CUI este deja inregistrat. Puteti solicita acces la aceasta organizatie."
        }
    
    return {
        "valid": True,
        "available": True,
        "registered": False,
        "message": "CUI disponibil pentru inregistrare."
    }
