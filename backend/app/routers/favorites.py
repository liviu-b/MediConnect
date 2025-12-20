from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from ..db import db
from ..schemas.favorite import (
    FavoriteDoctor,
    FavoriteDoctorCreate,
    FavoriteDoctorUpdate,
    FavoriteDoctorStats
)
from ..security import require_auth

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/doctors", response_model=List[FavoriteDoctor])
async def get_favorite_doctors(request: Request):
    """Get user's favorite doctors"""
    user = await require_auth(request)
    
    favorites = await db.favorite_doctors.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Enrich with latest doctor info
    for fav in favorites:
        doctor = await db.doctors.find_one(
            {"doctor_id": fav["doctor_id"]},
            {"_id": 0}
        )
        
        if doctor:
            fav["doctor_name"] = doctor.get("name")
            fav["doctor_specialty"] = doctor.get("specialty")
            fav["doctor_clinic_id"] = doctor.get("clinic_id")
            fav["doctor_picture"] = doctor.get("picture")
            fav["doctor_consultation_fee"] = doctor.get("consultation_fee")
            fav["doctor_consultation_duration"] = doctor.get("consultation_duration")
            
            # Get clinic name
            if doctor.get("clinic_id"):
                clinic = await db.clinics.find_one(
                    {"clinic_id": doctor["clinic_id"]},
                    {"_id": 0, "name": 1}
                )
                if clinic:
                    fav["doctor_clinic_name"] = clinic.get("name")
            
            # Get last appointment with this doctor
            last_apt = await db.appointments.find_one(
                {
                    "patient_id": user.user_id,
                    "doctor_id": fav["doctor_id"],
                    "status": "COMPLETED"
                },
                {"_id": 0, "date_time": 1}
            ).sort("date_time", -1)
            
            if last_apt:
                fav["last_appointment_date"] = last_apt.get("date_time")
            
            # Count total appointments with this doctor
            total_appointments = await db.appointments.count_documents({
                "patient_id": user.user_id,
                "doctor_id": fav["doctor_id"]
            })
            fav["total_appointments"] = total_appointments
    
    return favorites


@router.post("/doctors", response_model=FavoriteDoctor)
async def add_favorite_doctor(data: FavoriteDoctorCreate, request: Request):
    """Add a doctor to favorites"""
    user = await require_auth(request)
    
    # Check if doctor exists
    doctor = await db.doctors.find_one(
        {"doctor_id": data.doctor_id, "is_active": True},
        {"_id": 0}
    )
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if already favorited
    existing = await db.favorite_doctors.find_one({
        "user_id": user.user_id,
        "doctor_id": data.doctor_id
    })
    
    if existing:
        raise HTTPException(status_code=409, detail="Doctor already in favorites")
    
    # Get clinic info
    clinic_name = None
    if doctor.get("clinic_id"):
        clinic = await db.clinics.find_one(
            {"clinic_id": doctor["clinic_id"]},
            {"_id": 0, "name": 1}
        )
        if clinic:
            clinic_name = clinic.get("name")
    
    # Get last appointment date
    last_apt = await db.appointments.find_one(
        {
            "patient_id": user.user_id,
            "doctor_id": data.doctor_id,
            "status": "COMPLETED"
        },
        {"_id": 0, "date_time": 1}
    ).sort("date_time", -1)
    
    last_appointment_date = None
    if last_apt:
        last_appointment_date = last_apt.get("date_time")
    
    # Create favorite
    favorite = FavoriteDoctor(
        user_id=user.user_id,
        doctor_id=data.doctor_id,
        doctor_name=doctor.get("name"),
        doctor_specialty=doctor.get("specialty"),
        doctor_clinic_id=doctor.get("clinic_id"),
        doctor_clinic_name=clinic_name,
        notes=data.notes,
        last_appointment_date=last_appointment_date
    )
    
    doc = favorite.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('last_appointment_date'):
        doc['last_appointment_date'] = doc['last_appointment_date'].isoformat()
    
    await db.favorite_doctors.insert_one(doc)
    
    return favorite


@router.put("/doctors/{favorite_id}")
async def update_favorite_doctor(
    favorite_id: str,
    data: FavoriteDoctorUpdate,
    request: Request
):
    """Update favorite doctor (e.g., add notes)"""
    user = await require_auth(request)
    
    # Check if favorite exists and belongs to user
    favorite = await db.favorite_doctors.find_one({
        "favorite_id": favorite_id,
        "user_id": user.user_id
    })
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    await db.favorite_doctors.update_one(
        {"favorite_id": favorite_id},
        {"$set": update_data}
    )
    
    updated = await db.favorite_doctors.find_one(
        {"favorite_id": favorite_id},
        {"_id": 0}
    )
    
    return updated


@router.delete("/doctors/{favorite_id}")
async def remove_favorite_doctor(favorite_id: str, request: Request):
    """Remove a doctor from favorites"""
    user = await require_auth(request)
    
    # Check if favorite exists and belongs to user
    favorite = await db.favorite_doctors.find_one({
        "favorite_id": favorite_id,
        "user_id": user.user_id
    })
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.favorite_doctors.delete_one({"favorite_id": favorite_id})
    
    return {"message": "Doctor removed from favorites"}


@router.delete("/doctors/by-doctor/{doctor_id}")
async def remove_favorite_by_doctor_id(doctor_id: str, request: Request):
    """Remove a doctor from favorites by doctor_id"""
    user = await require_auth(request)
    
    result = await db.favorite_doctors.delete_one({
        "user_id": user.user_id,
        "doctor_id": doctor_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Doctor removed from favorites"}


@router.get("/doctors/check/{doctor_id}")
async def check_if_favorite(doctor_id: str, request: Request):
    """Check if a doctor is in user's favorites"""
    user = await require_auth(request)
    
    favorite = await db.favorite_doctors.find_one({
        "user_id": user.user_id,
        "doctor_id": doctor_id
    })
    
    return {
        "is_favorite": favorite is not None,
        "favorite_id": favorite.get("favorite_id") if favorite else None
    }


@router.get("/stats", response_model=FavoriteDoctorStats)
async def get_favorite_stats(request: Request):
    """Get statistics about favorite doctors"""
    user = await require_auth(request)
    
    # Count total favorites
    total_favorites = await db.favorite_doctors.count_documents({
        "user_id": user.user_id
    })
    
    # Get all favorite doctor IDs
    favorites = await db.favorite_doctors.find(
        {"user_id": user.user_id},
        {"_id": 0, "doctor_id": 1}
    ).to_list(100)
    
    favorite_doctor_ids = [f["doctor_id"] for f in favorites]
    
    # Count appointments with favorite doctors
    total_appointments = 0
    last_visit = None
    
    if favorite_doctor_ids:
        total_appointments = await db.appointments.count_documents({
            "patient_id": user.user_id,
            "doctor_id": {"$in": favorite_doctor_ids}
        })
        
        # Get last visit
        last_apt = await db.appointments.find_one(
            {
                "patient_id": user.user_id,
                "doctor_id": {"$in": favorite_doctor_ids},
                "status": "COMPLETED"
            },
            {"_id": 0, "date_time": 1}
        ).sort("date_time", -1)
        
        if last_apt:
            last_visit = last_apt.get("date_time")
    
    return FavoriteDoctorStats(
        total_favorites=total_favorites,
        total_appointments=total_appointments,
        last_visit=last_visit
    )


@router.get("/doctors/{doctor_id}/availability")
async def get_favorite_doctor_availability(doctor_id: str, date: str, request: Request):
    """Get availability for a favorite doctor (quick booking)"""
    user = await require_auth(request)
    
    # Check if doctor is in favorites
    favorite = await db.favorite_doctors.find_one({
        "user_id": user.user_id,
        "doctor_id": doctor_id
    })
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Doctor not in favorites")
    
    # Get doctor info
    doctor = await db.doctors.find_one(
        {"doctor_id": doctor_id, "is_active": True},
        {"_id": 0}
    )
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get availability (reuse logic from doctors router)
    from ..routers.doctors import get_doctor_availability
    
    # This would call the existing availability endpoint
    # For now, return basic info
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.get("name"),
        "clinic_id": doctor.get("clinic_id"),
        "date": date,
        "message": "Use /api/doctors/{doctor_id}/availability endpoint for full availability"
    }
