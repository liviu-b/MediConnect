from fastapi import APIRouter, HTTPException, Request
from ..db import db
from ..schemas.clinic import ClinicUpdate
from ..security import require_clinic_admin

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("")
async def get_clinics():
    clinics = await db.clinics.find({}, {"_id": 0}).to_list(length=100)
    return clinics


@router.get("/{clinic_id}")
async def get_clinic(clinic_id: str):
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.put("/{clinic_id}")
async def update_clinic(clinic_id: str, data: ClinicUpdate, request: Request):
    user = await require_clinic_admin(request)
    if user.clinic_id != clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    new_name = update_data.get('name', clinic.get('name'))
    new_address = update_data.get('address', clinic.get('address'))
    if new_name and new_address:
        update_data['is_profile_complete'] = True
    await db.clinics.update_one({"clinic_id": clinic_id}, {"$set": update_data})
    updated = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    return updated
