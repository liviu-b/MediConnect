from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from ..db import db
from ..schemas.service import Service, ServiceCreate
from ..security import require_clinic_admin, get_current_user

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
async def get_services(request: Request, clinic_id: Optional[str] = None):
    user = await get_current_user(request)
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        query = {"clinic_id": user.clinic_id, "is_active": True}
    elif clinic_id:
        query = {"clinic_id": clinic_id, "is_active": True}
    else:
        query = {"is_active": True}
    services = await db.services.find(query, {"_id": 0}).to_list(100)
    return services


@router.post("")
async def create_service(data: ServiceCreate, request: Request):
    user = await require_clinic_admin(request)
    service = Service(
        clinic_id=user.clinic_id,
        name=data.name,
        description=data.description,
        duration=data.duration,
        price=data.price,
        currency=data.currency
    )
    doc = service.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.services.insert_one(doc)
    return service


@router.put("/{service_id}")
async def update_service(service_id: str, data: ServiceCreate, request: Request):
    user = await require_clinic_admin(request)
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Service not found")
    update_data = {
        "name": data.name,
        "description": data.description,
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
    user = await require_clinic_admin(request)
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.services.update_one({"service_id": service_id}, {"$set": {"is_active": False}})
    return {"message": "Service removed successfully"}
