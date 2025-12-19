from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..db import db
from ..schemas.doctor import Doctor, DoctorCreate, DoctorUpdate
from ..security import require_clinic_admin, get_current_user, require_auth

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("")
async def get_doctors(request: Request, clinic_id: Optional[str] = None, location_id: Optional[str] = None):
    user = await get_current_user(request)
    query = {"is_active": True}
    
    if user and user.role == "SUPER_ADMIN" and user.organization_id:
        # Super admin sees all doctors in their organization
        if location_id:
            query["location_id"] = location_id
        elif clinic_id:
            query["clinic_id"] = clinic_id
        else:
            # Get all locations in organization
            locations = await db.locations.find(
                {"organization_id": user.organization_id},
                {"_id": 0, "location_id": 1}
            ).to_list(100)
            location_ids = [loc["location_id"] for loc in locations]
            if location_ids:
                query["location_id"] = {"$in": location_ids}
    elif user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif location_id:
        query["location_id"] = location_id
    elif clinic_id:
        query["clinic_id"] = clinic_id
    
    doctors = await db.doctors.find(query, {"_id": 0}).to_list(100)
    for doc in doctors:
        # Try to get location info first, fallback to clinic
        if doc.get("location_id"):
            location = await db.locations.find_one({"location_id": doc["location_id"]}, {"_id": 0})
            doc["location_name"] = location.get("name") if location else "Unknown"
        elif doc.get("clinic_id"):
            clinic = await db.clinics.find_one({"clinic_id": doc["clinic_id"]}, {"_id": 0})
            doc["clinic_name"] = clinic.get("name") if clinic else "Unknown"
    return doctors


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str):
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    clinic = await db.clinics.find_one({"clinic_id": doctor["clinic_id"]}, {"_id": 0})
    doctor["clinic_name"] = clinic.get("name") if clinic else "Unknown"
    return doctor


@router.post("")
async def create_doctor(data: DoctorCreate, request: Request, location_id: Optional[str] = None):
    user = await require_auth(request)
    
    # Determine which location/clinic to use
    target_location_id = None
    target_clinic_id = None
    target_organization_id = None
    target_user_id = None
    
    # Check if this is a doctor creating their own profile
    if user.role == "DOCTOR":
        # Doctor is creating their own profile after invitation
        target_user_id = user.user_id
        target_organization_id = user.organization_id
        if user.assigned_location_ids and len(user.assigned_location_ids) > 0:
            target_location_id = user.assigned_location_ids[0]
        target_clinic_id = user.clinic_id
        
        # Verify email matches
        if data.email.lower() != user.email.lower():
            raise HTTPException(status_code=403, detail="Email must match your account")
    
    elif user.role == "SUPER_ADMIN":
        # Super admin must specify a location
        if not location_id:
            # Try to get from request header (set by LocationSwitcher)
            location_id = request.headers.get("X-Location-ID")
        
        if not location_id:
            raise HTTPException(
                status_code=400, 
                detail="Super admin must specify a location_id to add a doctor"
            )
        
        # Verify location belongs to super admin's organization
        location = await db.locations.find_one(
            {"location_id": location_id, "organization_id": user.organization_id},
            {"_id": 0}
        )
        if not location:
            raise HTTPException(
                status_code=403,
                detail="Location not found or does not belong to your organization"
            )
        
        target_location_id = location_id
        target_organization_id = user.organization_id
        # For backward compatibility, also set clinic_id if it exists
        target_clinic_id = location.get("clinic_id")
    
    elif user.role in ["CLINIC_ADMIN", "LOCATION_ADMIN"]:
        # CLINIC_ADMIN or LOCATION_ADMIN use their clinic_id
        if not user.clinic_id:
            raise HTTPException(status_code=400, detail="User does not have a clinic assigned")
        target_clinic_id = user.clinic_id
    else:
        raise HTTPException(status_code=403, detail="Not authorized to create doctor profiles")
    
    doctor = Doctor(
        user_id=target_user_id,
        clinic_id=target_clinic_id,
        location_id=target_location_id,
        organization_id=target_organization_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        specialty=data.specialty,
        bio=data.bio,
        picture=data.picture,
        consultation_duration=data.consultation_duration,
        consultation_fee=data.consultation_fee,
        currency=data.currency,
        availability_schedule=data.availability_schedule or {
            "monday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "tuesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "wednesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "thursday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "friday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "saturday": [{"start": "10:00", "end": "14:00"}],
            "sunday": []
        }
    )
    doc = doctor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.doctors.insert_one(doc)
    return doctor


@router.put("/{doctor_id}")
async def update_doctor(doctor_id: str, data: DoctorUpdate, request: Request):
    user = await require_clinic_admin(request)
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check access permissions
    has_access = False
    if user.role == "SUPER_ADMIN":
        # Super admin can update doctors in their organization
        if doctor.get("organization_id") == user.organization_id:
            has_access = True
        elif doctor.get("location_id"):
            # Check if location belongs to super admin's organization
            location = await db.locations.find_one(
                {"location_id": doctor["location_id"], "organization_id": user.organization_id},
                {"_id": 0}
            )
            has_access = location is not None
    elif user.clinic_id and doctor.get("clinic_id") == user.clinic_id:
        has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if update_data:
        await db.doctors.update_one({"doctor_id": doctor_id}, {"$set": update_data})
    return await get_doctor(doctor_id)


@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: str, request: Request):
    user = await require_clinic_admin(request)
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check access permissions
    has_access = False
    if user.role == "SUPER_ADMIN":
        # Super admin can delete doctors in their organization
        if doctor.get("organization_id") == user.organization_id:
            has_access = True
        elif doctor.get("location_id"):
            # Check if location belongs to super admin's organization
            location = await db.locations.find_one(
                {"location_id": doctor["location_id"], "organization_id": user.organization_id},
                {"_id": 0}
            )
            has_access = location is not None
    elif user.clinic_id and doctor.get("clinic_id") == user.clinic_id:
        has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.doctors.update_one({"doctor_id": doctor_id}, {"$set": {"is_active": False}})
    return {"message": "Doctor deactivated successfully"}


@router.get("/{doctor_id}/availability")
async def get_doctor_availability(doctor_id: str, date: str):
    doctor = await db.doctors.find_one({"doctor_id": doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = day_names[target_date.weekday()]
    schedule = doctor.get("availability_schedule", {}).get(day_name, [])
    if not schedule:
        return {"date": date, "available_slots": [], "duration": doctor.get("consultation_duration", 30)}
    start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    existing_appointments = await db.appointments.find({
        "doctor_id": doctor_id,
        "date_time": {"$gte": start_of_day.isoformat(), "$lte": end_of_day.isoformat()},
        "status": {"$ne": "CANCELLED"}
    }, {"_id": 0}).to_list(100)
    booked_times = set()
    for apt in existing_appointments:
        apt_time = datetime.fromisoformat(apt["date_time"].replace("Z", "+00:00"))
        booked_times.add(apt_time.strftime("%H:%M"))
    duration = doctor.get("consultation_duration", 30)
    available_slots = []
    for period in schedule:
        start_time = datetime.strptime(period["start"], "%H:%M")
        end_time = datetime.strptime(period["end"], "%H:%M")
        current = start_time
        while current < end_time:
            time_str = current.strftime("%H:%M")
            if time_str not in booked_times:
                slot_datetime = datetime.combine(target_date, current.time()).replace(tzinfo=timezone.utc)
                if target_date > datetime.now(timezone.utc).date() or slot_datetime > datetime.now(timezone.utc):
                    available_slots.append({"time": time_str, "datetime": slot_datetime.isoformat()})
            current += timedelta(minutes=duration)
    return {"date": date, "available_slots": available_slots, "duration": duration}


@router.put("/{doctor_id}/availability")
async def update_doctor_availability(doctor_id: str, data: dict, request: Request):
    user = await require_auth(request)
    doctor = await db.doctors.find_one({"doctor_id": doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    is_own_profile = user.email.lower() == doctor.get('email', '').lower()
    is_admin = user.role == 'CLINIC_ADMIN' and user.clinic_id == doctor['clinic_id']
    if not is_own_profile and not is_admin:
        raise HTTPException(status_code=403, detail="You can only update your own availability")
    clinic = await db.clinics.find_one({"clinic_id": doctor['clinic_id']}, {"_id": 0})
    clinic_hours = clinic.get('working_hours', {}) if clinic else {}
    availability_schedule = data.get('availability_schedule', {})
    validated_schedule = {}
    for day, periods in availability_schedule.items():
        clinic_day_hours = clinic_hours.get(day)
        if clinic_day_hours is None:
            validated_schedule[day] = []
            continue
        valid_periods = []
        for period in periods:
            start = period.get('start', '09:00')
            end = period.get('end', '17:00')
            if clinic_day_hours:
                clinic_start = clinic_day_hours.get('start', '00:00')
                clinic_end = clinic_day_hours.get('end', '23:59')
                if start < clinic_start:
                    start = clinic_start
                if end > clinic_end:
                    end = clinic_end
            if start < end:
                valid_periods.append({'start': start, 'end': end})
        validated_schedule[day] = valid_periods
    await db.doctors.update_one(
        {"doctor_id": doctor_id},
        {"$set": {"availability_schedule": validated_schedule}}
    )
    updated_doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    return updated_doctor
