from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..db import db
from ..schemas.doctor import Doctor, DoctorCreate, DoctorUpdate
from ..security import require_clinic_admin, get_current_user, require_auth

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("")
async def get_doctors(request: Request, clinic_id: Optional[str] = None):
    user = await get_current_user(request)
    query = {"is_active": True}
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif clinic_id:
        query["clinic_id"] = clinic_id
    doctors = await db.doctors.find(query, {"_id": 0}).to_list(100)
    for doc in doctors:
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
async def create_doctor(data: DoctorCreate, request: Request):
    user = await require_clinic_admin(request)
    doctor = Doctor(
        clinic_id=user.clinic_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        specialty=data.specialty,
        bio=data.bio,
        picture=data.picture,
        consultation_duration=data.consultation_duration,
        consultation_fee=data.consultation_fee,
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
    if doctor["clinic_id"] != user.clinic_id:
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
    if doctor["clinic_id"] != user.clinic_id:
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
