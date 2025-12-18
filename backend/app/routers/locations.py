from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from ..db import db
from ..schemas.location import Location, LocationCreate, LocationUpdate
from ..security import require_auth

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("")
async def get_locations(request: Request):
    """
    Get all locations for the user's organization.
    Returns all active locations the user has access to.
    """
    user = await require_auth(request)
    
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not associated with an organization")
    
    # Get all locations for this organization
    locations = await db.locations.find(
        {"organization_id": user.organization_id, "is_active": True},
        {"_id": 0}
    ).sort("is_primary", -1).to_list(100)
    
    # If user has assigned_location_ids, filter to only those
    if user.assigned_location_ids:
        locations = [loc for loc in locations if loc['location_id'] in user.assigned_location_ids]
    
    return locations


@router.get("/{location_id}")
async def get_location(location_id: str, request: Request):
    """Get a specific location by ID"""
    user = await require_auth(request)
    
    location = await db.locations.find_one(
        {"location_id": location_id},
        {"_id": 0}
    )
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check if user has access to this location
    if location['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user.assigned_location_ids and location_id not in user.assigned_location_ids:
        raise HTTPException(status_code=403, detail="You don't have access to this location")
    
    return location


@router.post("")
async def create_location(data: LocationCreate, request: Request):
    """
    Create a new location (Super Admin or Location Admin only)
    """
    user = await require_auth(request)
    
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN"]:
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins and Location Admins can create locations"
        )
    
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not associated with an organization")
    
    # Create location
    location_id = f"loc_{uuid.uuid4().hex[:12]}"
    location = Location(
        location_id=location_id,
        organization_id=user.organization_id,
        name=data.name,
        address=data.address,
        city=data.city,
        county=data.county,
        phone=data.phone,
        email=data.email,
        description=data.description,
        working_hours=data.working_hours or Location().working_hours,
        settings=data.settings or Location().settings,
        is_primary=False
    )
    
    location_doc = location.model_dump()
    location_doc['created_at'] = location_doc['created_at'].isoformat()
    
    await db.locations.insert_one(location_doc)
    
    return {k: v for k, v in location_doc.items() if k != '_id'}


@router.put("/{location_id}")
async def update_location(location_id: str, data: LocationUpdate, request: Request):
    """
    Update a location (Super Admin or Location Admin only)
    """
    user = await require_auth(request)
    
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN"]:
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins and Location Admins can update locations"
        )
    
    # Get location
    location = await db.locations.find_one({"location_id": location_id}, {"_id": 0})
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check access
    if location['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user.role == "LOCATION_ADMIN" and user.assigned_location_ids:
        if location_id not in user.assigned_location_ids:
            raise HTTPException(status_code=403, detail="You don't have access to this location")
    
    # Build update data
    update_data = {}
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.locations.update_one(
            {"location_id": location_id},
            {"$set": update_data}
        )
    
    # Return updated location
    updated_location = await db.locations.find_one(
        {"location_id": location_id},
        {"_id": 0}
    )
    
    return updated_location


@router.delete("/{location_id}")
async def delete_location(location_id: str, request: Request):
    """
    Soft delete a location (Super Admin only)
    """
    user = await require_auth(request)
    
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="Only Super Admins can delete locations"
        )
    
    # Get location
    location = await db.locations.find_one({"location_id": location_id}, {"_id": 0})
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check access
    if location['organization_id'] != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Don't allow deleting primary location if it's the only one
    if location.get('is_primary'):
        other_locations = await db.locations.count_documents({
            "organization_id": user.organization_id,
            "is_active": True,
            "location_id": {"$ne": location_id}
        })
        
        if other_locations == 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete the only location. Create another location first."
            )
    
    # Soft delete
    await db.locations.update_one(
        {"location_id": location_id},
        {"$set": {
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Location deleted successfully"}
