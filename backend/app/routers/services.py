from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from ..db import db
from ..schemas.service import Service, ServiceCreate
from ..security import get_current_user

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
async def get_services(request: Request, clinic_id: Optional[str] = None, location_id: Optional[str] = None):
    user = await get_current_user(request)
    
    # Build query based on user role and parameters
    query = {"is_active": True}
    
    if user:
        if user.role == "SUPER_ADMIN" and user.organization_id:
            # Super admin sees all services in their organization
            query["organization_id"] = user.organization_id
        elif user.role == "LOCATION_ADMIN" and user.assigned_location_ids:
            # Location admin sees services in their locations
            query["location_id"] = {"$in": user.assigned_location_ids}
        elif user.role == "CLINIC_ADMIN" and user.clinic_id:
            # Legacy clinic admin
            query["clinic_id"] = user.clinic_id
        elif location_id:
            query["location_id"] = location_id
        elif clinic_id:
            query["clinic_id"] = clinic_id
    
    services = await db.services.find(query, {"_id": 0}).to_list(100)
    return services


@router.post("")
async def create_service(data: ServiceCreate, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user can create services
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "CLINIC_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to create services")
    
    # Get location_id from request header or use first assigned location
    location_id = request.headers.get("x-location-id")
    
    if user.role == "SUPER_ADMIN":
        if not location_id:
            # Get first location in organization
            location = await db.locations.find_one(
                {"organization_id": user.organization_id, "is_active": True},
                {"_id": 0}
            )
            if location:
                location_id = location["location_id"]
            else:
                raise HTTPException(status_code=400, detail="No location found. Please create a location first.")
    elif user.role == "LOCATION_ADMIN":
        if not location_id and user.assigned_location_ids:
            location_id = user.assigned_location_ids[0]
    
    # Create service with appropriate IDs
    service_data = {
        "name": data.name,
        "name_en": data.name_en,
        "name_ro": data.name_ro,
        "description": data.description,
        "description_en": data.description_en,
        "description_ro": data.description_ro,
        "duration": data.duration,
        "price": data.price,
        "currency": data.currency
    }
    
    # Add organization/location IDs for new system
    if user.organization_id:
        service_data["organization_id"] = user.organization_id
    if location_id:
        service_data["location_id"] = location_id
    
    # Add clinic_id for legacy system
    if user.clinic_id:
        service_data["clinic_id"] = user.clinic_id
    
    service = Service(**service_data)
    doc = service.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.services.insert_one(doc)
    return service


@router.put("/{service_id}")
async def update_service(service_id: str, data: ServiceCreate, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user can update services
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "CLINIC_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update services")
    
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check access rights
    has_access = False
    if user.role == "SUPER_ADMIN" and service.get("organization_id") == user.organization_id:
        has_access = True
    elif user.role == "LOCATION_ADMIN" and service.get("location_id") in (user.assigned_location_ids or []):
        has_access = True
    elif user.role == "CLINIC_ADMIN" and service.get("clinic_id") == user.clinic_id:
        has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to update this service")
    
    update_data = {
        "name": data.name,
        "name_en": data.name_en,
        "name_ro": data.name_ro,
        "description": data.description,
        "description_en": data.description_en,
        "description_ro": data.description_ro,
        "duration": data.duration,
        "price": data.price,
        "currency": data.currency
    }
    await db.services.update_one(
        {"service_id": service_id},
        {"$set": update_data}
    )
    updated_service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    return updated_service


@router.delete("/{service_id}")
async def delete_service(service_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user can delete services
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "CLINIC_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete services")
    
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check access rights
    has_access = False
    if user.role == "SUPER_ADMIN" and service.get("organization_id") == user.organization_id:
        has_access = True
    elif user.role == "LOCATION_ADMIN" and service.get("location_id") in (user.assigned_location_ids or []):
        has_access = True
    elif user.role == "CLINIC_ADMIN" and service.get("clinic_id") == user.clinic_id:
        has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")
    
    await db.services.update_one({"service_id": service_id}, {"$set": {"is_active": False}})
    return {"message": "Service removed successfully"}
