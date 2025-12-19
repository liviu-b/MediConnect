"""
Invitation Routes

This module handles user invitations for Location Admins and Staff.
Critical rules:
1. SUPER_ADMIN can invite LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
2. LOCATION_ADMIN can invite RECEPTIONIST, DOCTOR, ASSISTANT (NOT other LOCATION_ADMINs)
3. Invitations are email-based with secure tokens
4. Tokens expire after 7 days
"""

from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import secrets

from ..db import db
from ..schemas.invitation import (
    Invitation,
    InvitationCreate,
    InvitationAccept,
    InvitationDetails,
    validate_invitation_role,
    get_user_role_from_invitation_role
)
from ..schemas.user import User, UserRole
from ..schemas.audit_log import AuditActions
from ..security import require_auth, hash_password, create_session
from ..services.permissions import PermissionService
from ..services.email import send_staff_invitation_email
from ..config import FRONTEND_URL
from ..middleware.permissions import require_role

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("")
async def create_invitation(
    data: InvitationCreate,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Create a new invitation for a user.
    
    Rules:
    - SUPER_ADMIN can invite: LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
    - LOCATION_ADMIN can invite: RECEPTIONIST, DOCTOR, ASSISTANT
    """
    user = await require_auth(request)
    
    # Validate role hierarchy
    if not validate_invitation_role(data.role, user.role):
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to invite users with role {data.role}"
        )
    
    # Check if user can invite
    can_invite = await PermissionService.can_invite_users(user, data.role)
    if not can_invite:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to invite users"
        )
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists"
        )
    
    # Check if there's already a pending invitation
    existing_invitation = await db.invitations.find_one({
        "email": data.email.lower(),
        "status": "PENDING"
    }, {"_id": 0})
    
    if existing_invitation:
        raise HTTPException(
            status_code=400,
            detail="There is already a pending invitation for this email"
        )
    
    # Validate location assignments
    if data.role != UserRole.LOCATION_ADMIN and not data.location_ids:
        raise HTTPException(
            status_code=400,
            detail="Location assignments are required for this role"
        )
    
    # Verify user has access to assigned locations
    if data.location_ids:
        accessible_locations = await PermissionService.get_accessible_locations(user)
        for loc_id in data.location_ids:
            if loc_id not in accessible_locations:
                raise HTTPException(
                    status_code=403,
                    detail=f"You do not have access to location {loc_id}"
                )
    
    # Generate secure invitation token
    invitation_token = f"invite_{secrets.token_hex(32)}"
    
    # Create invitation
    invitation = Invitation(
        organization_id=user.organization_id,
        location_ids=data.location_ids or [],
        email=data.email.lower(),
        name=data.name,
        phone=data.phone,
        role=data.role,
        invitation_token=invitation_token,
        invited_by=user.user_id,
        invited_by_name=user.name,
        status="PENDING",
        metadata=data.metadata or {}
    )
    
    # Save to database
    invitation_doc = invitation.model_dump()
    invitation_doc['created_at'] = invitation_doc['created_at'].isoformat()
    invitation_doc['expires_at'] = invitation_doc['expires_at'].isoformat()
    await db.invitations.insert_one(invitation_doc)
    
    # Get organization and location details for email
    organization = await db.organizations.find_one(
        {"organization_id": user.organization_id},
        {"_id": 0}
    )
    
    location_names = []
    if data.location_ids:
        locations = await db.locations.find(
            {"location_id": {"$in": data.location_ids}},
            {"_id": 0, "name": 1}
        ).to_list(100)
        location_names = [loc.get("name", "Unknown") for loc in locations]
    
    # Send invitation email
    invitation_link = f"{FRONTEND_URL}/accept-invitation?token={invitation_token}"
    
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=data.email.lower(),
        recipient_name=data.name,
        role=data.role,
        invitation_link=invitation_link,
        clinic_name=organization.get("name", "Medical Center") if organization else "Medical Center",
        inviter_name=user.name
    )
    
    # Log the action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.STAFF_INVITE,
        resource_type="invitation",
        resource_id=invitation.invitation_id,
        description=f"Invited {data.name} ({data.email}) as {data.role}",
        metadata={
            "invitee_email": data.email,
            "invitee_role": data.role,
            "location_ids": data.location_ids
        },
        status="success"
    )
    
    return {
        "invitation_id": invitation.invitation_id,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "expires_at": invitation.expires_at.isoformat()
    }


@router.get("")
async def list_invitations(
    request: Request,
    status: Optional[str] = None,
    role: Optional[str] = None,
    location_id: Optional[str] = None
):
    """
    List invitations for the current user's organization.
    
    Filters:
    - status: PENDING, ACCEPTED, EXPIRED, CANCELLED
    - role: Filter by invited role
    - location_id: Filter by location
    """
    user = await require_auth(request)
    
    # Build query
    query = {"organization_id": user.organization_id}
    
    if status:
        query["status"] = status
    
    if role:
        query["role"] = role
    
    if location_id:
        query["location_ids"] = location_id
    
    # Get invitations
    invitations = await db.invitations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Filter by accessible locations for LOCATION_ADMIN
    if user.role == UserRole.LOCATION_ADMIN:
        accessible_locations = await PermissionService.get_accessible_locations(user)
        invitations = [
            inv for inv in invitations
            if any(loc_id in accessible_locations for loc_id in inv.get("location_ids", []))
        ]
    
    return invitations


@router.get("/{invitation_id}")
async def get_invitation(invitation_id: str, request: Request):
    """
    Get invitation details by ID.
    """
    user = await require_auth(request)
    
    invitation = await db.invitations.find_one(
        {"invitation_id": invitation_id},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check access
    if invitation["organization_id"] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # For LOCATION_ADMIN, check location access
    if user.role == UserRole.LOCATION_ADMIN:
        accessible_locations = await PermissionService.get_accessible_locations(user)
        if not any(loc_id in accessible_locations for loc_id in invitation.get("location_ids", [])):
            raise HTTPException(status_code=403, detail="Access denied")
    
    return invitation


@router.get("/token/{token}")
async def get_invitation_by_token(token: str):
    """
    Get invitation details by token (public endpoint for invitees).
    """
    invitation = await db.invitations.find_one(
        {"invitation_token": token},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    # Check if already accepted
    if invitation["status"] == "ACCEPTED":
        raise HTTPException(status_code=400, detail="This invitation has already been accepted")
    
    # Check if expired
    expires_at = invitation["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        # Mark as expired
        await db.invitations.update_one(
            {"invitation_token": token},
            {"$set": {"status": "EXPIRED"}}
        )
        raise HTTPException(status_code=400, detail="This invitation has expired")
    
    # Get organization details
    organization = await db.organizations.find_one(
        {"organization_id": invitation["organization_id"]},
        {"_id": 0}
    )
    
    # Get location names
    location_names = []
    if invitation.get("location_ids"):
        locations = await db.locations.find(
            {"location_id": {"$in": invitation["location_ids"]}},
            {"_id": 0, "name": 1}
        ).to_list(100)
        location_names = [loc.get("name", "Unknown") for loc in locations]
    
    # Return public details
    return InvitationDetails(
        name=invitation["name"],
        email=invitation["email"],
        role=invitation["role"],
        organization_name=organization.get("name", "Medical Center") if organization else "Medical Center",
        location_names=location_names,
        invited_by_name=invitation.get("invited_by_name", "Administrator"),
        expires_at=expires_at
    )


@router.post("/accept")
async def accept_invitation(data: InvitationAccept, response: Response):
    """
    Accept an invitation and create user account.
    """
    # Validate password
    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    
    # Get invitation
    invitation = await db.invitations.find_one(
        {"invitation_token": data.token},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    # Check if already accepted
    if invitation["status"] == "ACCEPTED":
        raise HTTPException(status_code=400, detail="This invitation has already been accepted")
    
    # Check if expired
    expires_at = invitation["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        await db.invitations.update_one(
            {"invitation_token": data.token},
            {"$set": {"status": "EXPIRED"}}
        )
        raise HTTPException(status_code=400, detail="This invitation has expired")
    
    # Check if email already registered
    existing_user = await db.users.find_one(
        {"email": invitation["email"]},
        {"_id": 0}
    )
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered"
        )
    
    # Create user account
    user_id = f"user_{secrets.token_hex(12)}"
    user_role = get_user_role_from_invitation_role(invitation["role"])
    
    # Get cached permissions for the role
    from ..schemas.permission import ROLE_PERMISSIONS_MATRIX
    cached_permissions = list(ROLE_PERMISSIONS_MATRIX.get(user_role, {}).keys())
    
    new_user = User(
        user_id=user_id,
        email=invitation["email"],
        name=invitation["name"],
        phone=invitation.get("phone"),
        password_hash=hash_password(data.password),
        auth_provider="email",
        role=user_role,
        organization_id=invitation["organization_id"],
        assigned_location_ids=invitation.get("location_ids", []),
        cached_permissions=cached_permissions,
        permissions_updated_at=datetime.now(timezone.utc),
        metadata=invitation.get("metadata", {}),
        is_active=True,
        is_email_verified=True
    )
    
    user_doc = new_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    user_doc['permissions_updated_at'] = user_doc['permissions_updated_at'].isoformat()
    await db.users.insert_one(user_doc)
    
    # Update invitation status
    await db.invitations.update_one(
        {"invitation_token": data.token},
        {
            "$set": {
                "status": "ACCEPTED",
                "accepted_at": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id
            }
        }
    )
    
    # Create session
    session_token = await create_session(user_id, response)
    
    # Prepare user data for response
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    
    # Determine redirect based on role
    if user_role in [UserRole.RECEPTIONIST, UserRole.DOCTOR, UserRole.ASSISTANT]:
        user_data['redirect_to'] = '/staff-dashboard'
        user_data['dashboard_type'] = 'staff'
    elif user_role == UserRole.LOCATION_ADMIN:
        if invitation.get("location_ids"):
            primary_location = invitation["location_ids"][0]
            user_data['redirect_to'] = f"/location/{primary_location}/dashboard"
            user_data['dashboard_type'] = 'location'
            user_data['primary_location_id'] = primary_location
        else:
            user_data['redirect_to'] = '/dashboard'
            user_data['dashboard_type'] = 'location'
    else:
        user_data['redirect_to'] = '/dashboard'
        user_data['dashboard_type'] = 'admin'
    
    # Log the action
    await PermissionService.log_action(
        user=new_user,
        action=AuditActions.USER_CREATE,
        resource_type="user",
        resource_id=user_id,
        description=f"User account created via invitation acceptance",
        metadata={
            "invitation_id": invitation["invitation_id"],
            "invited_by": invitation.get("invited_by")
        },
        status="success"
    )
    
    return {
        "user": user_data,
        "session_token": session_token,
        "message": "Account created successfully"
    }


@router.post("/{invitation_id}/resend")
async def resend_invitation(
    invitation_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Resend an invitation email.
    """
    user = await require_auth(request)
    
    invitation = await db.invitations.find_one(
        {"invitation_id": invitation_id},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check access
    if invitation["organization_id"] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already accepted
    if invitation["status"] == "ACCEPTED":
        raise HTTPException(
            status_code=400,
            detail="Cannot resend an accepted invitation"
        )
    
    # Generate new token and expiration
    new_token = f"invite_{secrets.token_hex(32)}"
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Update invitation
    await db.invitations.update_one(
        {"invitation_id": invitation_id},
        {
            "$set": {
                "invitation_token": new_token,
                "expires_at": new_expires_at.isoformat(),
                "status": "PENDING",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Get organization details
    organization = await db.organizations.find_one(
        {"organization_id": invitation["organization_id"]},
        {"_id": 0}
    )
    
    # Send email
    invitation_link = f"{FRONTEND_URL}/accept-invitation?token={new_token}"
    
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=invitation["email"],
        recipient_name=invitation["name"],
        role=invitation["role"],
        invitation_link=invitation_link,
        clinic_name=organization.get("name", "Medical Center") if organization else "Medical Center",
        inviter_name=user.name
    )
    
    # Log the action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.STAFF_INVITE,
        resource_type="invitation",
        resource_id=invitation_id,
        description=f"Resent invitation to {invitation['email']}",
        status="success"
    )
    
    return {
        "message": "Invitation resent successfully",
        "expires_at": new_expires_at.isoformat()
    }


@router.delete("/{invitation_id}")
async def cancel_invitation(invitation_id: str, request: Request):
    """
    Cancel a pending invitation.
    """
    user = await require_auth(request)
    
    invitation = await db.invitations.find_one(
        {"invitation_id": invitation_id},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check access
    if invitation["organization_id"] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already accepted
    if invitation["status"] == "ACCEPTED":
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel an accepted invitation"
        )
    
    # Update status
    await db.invitations.update_one(
        {"invitation_id": invitation_id},
        {
            "$set": {
                "status": "CANCELLED",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log the action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.STAFF_DELETE,
        resource_type="invitation",
        resource_id=invitation_id,
        description=f"Cancelled invitation for {invitation['email']}",
        status="success"
    )
    
    return {"message": "Invitation cancelled successfully"}
