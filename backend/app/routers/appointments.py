from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone, timedelta

from ..db import db
from ..schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentCancel
from ..security import require_auth
from ..services.notifications import send_notification_email

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("")
async def get_appointments(
    request: Request,
    clinic_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    user = await require_auth(request)

    query = {}

    user_doctor_id = None
    if user.role == "DOCTOR" and user.clinic_id:
        user_doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if user_doctor:
            user_doctor_id = user_doctor.get("doctor_id")

    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif user.role in ["DOCTOR", "ASSISTANT"] and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif user.role == "USER":
        query["patient_id"] = user.user_id

    if doctor_id:
        query["doctor_id"] = doctor_id
    if status:
        query["status"] = status

    if start_date:
        query["date_time"] = query.get("date_time", {})
        query["date_time"]["$gte"] = start_date
    if end_date:
        query["date_time"] = query.get("date_time", {})
        query["date_time"]["$lte"] = end_date

    appointments = await db.appointments.find(query, {"_id": 0}).to_list(500)

    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"

        if user.role == "CLINIC_ADMIN":
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            apt["is_own_patient"] = True
        elif user.role == "DOCTOR":
            is_own_patient = user_doctor_id and apt["doctor_id"] == user_doctor_id
            apt["is_own_patient"] = is_own_patient

            if is_own_patient:
                patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
                apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
                apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            else:
                apt["patient_name"] = apt.get("patient_name", "Patient")
                apt["patient_email"] = None
                apt["notes"] = None
        elif user.role == "ASSISTANT":
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = None
            apt["is_own_patient"] = False

    return appointments


@router.post("")
async def create_appointment(data: AppointmentCreate, request: Request):
    user = await require_auth(request)

    doctor = await db.doctors.find_one({"doctor_id": data.doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    clinic = await db.clinics.find_one({"clinic_id": data.clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    apt_datetime = data.date_time
    if apt_datetime.tzinfo is None:
        apt_datetime = apt_datetime.replace(tzinfo=timezone.utc)

    existing = await db.appointments.find_one({
        "doctor_id": data.doctor_id,
        "date_time": apt_datetime.isoformat(),
        "status": {"$ne": "CANCELLED"}
    })

    if existing:
        raise HTTPException(status_code=409, detail="This time slot is already booked")

    appointment = Appointment(
        patient_id=user.user_id,
        patient_name=user.name,
        patient_email=user.email,
        patient_phone=user.phone,
        doctor_id=data.doctor_id,
        clinic_id=data.clinic_id,
        date_time=apt_datetime,
        duration=data.duration or doctor.get("consultation_duration", 30),
        notes=data.notes,
        recurrence=data.recurrence
    )

    doc = appointment.model_dump()
    doc['date_time'] = doc['date_time'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('recurrence') and doc['recurrence'].get('end_date'):
        doc['recurrence']['end_date'] = doc['recurrence']['end_date'].isoformat()

    await db.appointments.insert_one(doc)

    await send_notification_email(
        user_id=user.user_id,
        appointment_id=appointment.appointment_id,
        notification_type="BOOKING_CONFIRMATION",
        message=f"Your appointment with {doctor['name']} on {apt_datetime.strftime('%B %d, %Y at %H:%M')} has been confirmed."
    )

    return appointment


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, data: AppointmentUpdate, request: Request):
    user = await require_auth(request)

    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.role == "USER" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = data.model_dump(exclude_unset=True)
    if "date_time" in update_data and update_data["date_time"]:
        new_datetime = update_data["date_time"]
        if new_datetime.tzinfo is None:
            new_datetime = new_datetime.replace(tzinfo=timezone.utc)

        existing = await db.appointments.find_one({
            "doctor_id": appointment["doctor_id"],
            "date_time": new_datetime.isoformat(),
            "status": {"$ne": "CANCELLED"},
            "appointment_id": {"$ne": appointment_id}
        })

        if existing:
            raise HTTPException(status_code=409, detail="This time slot is already booked")

        update_data["date_time"] = new_datetime.isoformat()

    await db.appointments.update_one({"appointment_id": appointment_id}, {"$set": update_data})

    updated = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    return updated


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str, request: Request):
    user = await require_auth(request)

    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.role == "USER" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")

    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {"status": "CANCELLED"}}
    )

    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="CANCELLATION",
        message="Your appointment has been cancelled."
    )

    return {"message": "Appointment cancelled successfully"}


@router.post("/{appointment_id}/cancel")
async def cancel_appointment_with_reason(appointment_id: str, data: AppointmentCancel, request: Request):
    user = await require_auth(request)

    if user.role not in ["CLINIC_ADMIN", "DOCTOR", "ASSISTANT"]:
        raise HTTPException(status_code=403, detail="Only clinic staff can use this cancellation method")

    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only cancel your own appointments")

    if not data.reason or len(data.reason.strip()) < 3:
        raise HTTPException(status_code=400, detail="Cancellation reason is required (minimum 3 characters)")

    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "status": "CANCELLED",
            "cancellation_reason": data.reason.strip(),
            "cancelled_by": user.user_id,
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"message": "Appointment cancelled successfully", "reason": data.reason}
