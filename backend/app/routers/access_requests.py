from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone
import uuid

from ..db import db
from ..schemas.access_request import (
    AccessRequest, 
    AccessRequestApprove, 
    AccessRequestReject
)
from ..schemas.user import User
from ..schemas.location import Location
from ..security import require_auth, create_session
from ..services.email import send_password_reset_email

router = APIRouter(prefix="/access-requests", tags=["access-requests"])


@router.get("")
async def get_access_requests(request: Request, status: str = None):
    """
    Get all access requests for the organization (Super Admin only)
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can view access requests"
        )
    
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not associated with an organization")
    
    # Build query
    query = {"organization_id": user.organization_id}
    if status:
        query["status"] = status.upper()
    
    # Get requests
    requests = await db.access_requests.find(
        query,
        {"_id": 0, "password_hash": 0}  # Don't return password hash
    ).sort("created_at", -1).to_list(100)
    
    return requests


@router.get("/{request_id}")
async def get_access_request(request_id: str, request: Request):
    """
    Get a specific access request (Super Admin only)
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can view access requests"
        )
    
    access_request = await db.access_requests.find_one(
        {"request_id": request_id},
        {"_id": 0, "password_hash": 0}
    )
    
    if not access_request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    # Check if request belongs to user's organization
    if access_request['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return access_request


@router.post("/{request_id}/approve")
async def approve_access_request(
    request_id: str, 
    data: AccessRequestApprove, 
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks
):
    """
    Approve an access request and create the user account (Super Admin only)
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can approve access requests"
        )
    
    # Get access request
    access_request = await db.access_requests.find_one(
        {"request_id": request_id},
        {"_id": 0}
    )
    
    if not access_request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    # Check if request belongs to user's organization
    if access_request['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already processed
    if access_request['status'] != "PENDING":
        raise HTTPException(
            status_code=400, 
            detail=f"Request already {access_request['status'].lower()}"
        )
    
    # Check if email is already registered
    existing_user = await db.users.find_one(
        {"email": access_request['requester_email']},
        {"_id": 0}
    )
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="This email is already registered"
        )
    
    # Create new location if requested
    new_location_id = None
    if data.create_new_location and access_request.get('proposed_location_name'):
        location_id = f"loc_{uuid.uuid4().hex[:12]}"
        location = Location(
            location_id=location_id,
            organization_id=user.organization_id,
            name=access_request['proposed_location_name'],
            city=access_request.get('proposed_location_city'),
            is_primary=False
        )
        
        location_doc = location.model_dump()
        location_doc['created_at'] = location_doc['created_at'].isoformat()
        await db.locations.insert_one(location_doc)
        
        new_location_id = location_id
    
    # Create user account
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    # Determine assigned locations
    assigned_location_ids = data.assigned_location_ids
    if new_location_id and assigned_location_ids is None:
        assigned_location_ids = [new_location_id]
    
    new_user = User(
        user_id=user_id,
        email=access_request['requester_email'],
        name=access_request['requester_name'],
        phone=access_request.get('requester_phone'),
        password_hash=access_request['password_hash'],  # Already hashed
        auth_provider="email",
        role=data.role,
        organization_id=user.organization_id,
        assigned_location_ids=assigned_location_ids
    )
    
    user_doc = new_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    
    # Update access request status
    await db.access_requests.update_one(
        {"request_id": request_id},
        {"$set": {
            "status": "APPROVED",
            "reviewed_by": user.user_id,
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # TODO: Send approval email to requester
    # background_tasks.add_task(send_approval_email, access_request, new_user)
    
    return {
        "message": "Access request approved successfully",
        "user_id": user_id,
        "new_location_id": new_location_id
    }


@router.post("/{request_id}/reject")
async def reject_access_request(
    request_id: str, 
    data: AccessRequestReject, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Reject an access request (Super Admin only)
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can reject access requests"
        )
    
    # Get access request
    access_request = await db.access_requests.find_one(
        {"request_id": request_id},
        {"_id": 0}
    )
    
    if not access_request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    # Check if request belongs to user's organization
    if access_request['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already processed
    if access_request['status'] != "PENDING":
        raise HTTPException(
            status_code=400, 
            detail=f"Request already {access_request['status'].lower()}"
        )
    
    # Update access request status
    await db.access_requests.update_one(
        {"request_id": request_id},
        {"$set": {
            "status": "REJECTED",
            "reviewed_by": user.user_id,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "rejection_reason": data.rejection_reason
        }}
    )
    
    # TODO: Send rejection email to requester
    # background_tasks.add_task(send_rejection_email, access_request, data.rejection_reason)
    
    return {
        "message": "Access request rejected successfully"
    }


@router.delete("/{request_id}")
async def delete_access_request(request_id: str, request: Request):
    """
    Delete an access request (Super Admin only)
    Can only delete rejected or expired requests
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can delete access requests"
        )
    
    # Get access request
    access_request = await db.access_requests.find_one(
        {"request_id": request_id},
        {"_id": 0}
    )
    
    if not access_request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    # Check if request belongs to user's organization
    if access_request['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Can only delete rejected requests
    if access_request['status'] not in ["REJECTED"]:
        raise HTTPException(
            status_code=400, 
            detail="Can only delete rejected requests"
        )
    
    # Delete request
    await db.access_requests.delete_one({"request_id": request_id})
    
    return {"message": "Access request deleted successfully"}
