from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import db
from app.api import deps

router = APIRouter(prefix="/api/services", tags=["services"])


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"


@router.get("")
async def get_services(request: Request, clinic_id: Optional[str] = None):
    user = await deps.get_current_user(request)
    if user and user.get("role") == "CLINIC_ADMIN" and user.get("clinic_id"):
        query = {"clinic_id": user["clinic_id"], "is_active": True}
    elif clinic_id:
        query = {"clinic_id": clinic_id, "is_active": True}
    else:
        query = {"is_active": True}
    services = await db.services.find(query, {"_id": 0}).to_list(100)
    return services


@router.post("")
async def create_service(data: ServiceCreate, request: Request):
    user = await deps.require_clinic_admin(request)
    service = {
        "service_id": f"svc_{datetime.now(timezone.utc).timestamp()}",
        "clinic_id": user["clinic_id"],
        "name": data.name,
        "description": data.description,
        "duration": data.duration,
        "price": data.price,
        "currency": data.currency,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.services.insert_one(service)
    service.pop("_id", None)
    return service


@router.put("/{service_id}")
async def update_service(service_id: str, data: ServiceCreate, request: Request):
    user = await deps.require_clinic_admin(request)
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=404, detail="Service not found")
    update_data = {
        "name": data.name,
        "description": data.description,
        "duration": data.duration,
        "price": data.price,
        "currency": data.currency
    }
    await db.services.update_one({"service_id": service_id}, {"$set": update_data})
    updated = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    return updated


@router.delete("/{service_id}")
async def delete_service(service_id: str, request: Request):
    user = await deps.require_clinic_admin(request)
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.services.update_one({"service_id": service_id}, {"$set": {"is_active": False}})
    return {"message": "Service removed successfully"}
