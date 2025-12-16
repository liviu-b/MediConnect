from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from app.core.database import db
from app.api import deps
from app.services.email import send_notification_email, send_cancellation_notification_email

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class RecurrencePattern(BaseModel):
    pattern_type: str = "NONE"
    interval: int = 1
    end_date: Optional[datetime] = None
    days_of_week: List[int] = []


class AppointmentCreate(BaseModel):
    doctor_id: str
    clinic_id: str
    date_time: datetime
    duration: int = 30
    notes: Optional[str] = None
    recurrence: Optional[RecurrencePattern] = None


class AppointmentUpdate(BaseModel):
    date_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCancel(BaseModel):
    reason: str


class PrescriptionCreate(BaseModel):
    appointment_id: str
    medications: List[dict] = []
    notes: Optional[str] = None


class MedicalRecordCreate(BaseModel):
    appointment_id: str
    record_type: str = "RECOMMENDATION"
    title: str
    content: str


@router.get("")
async def get_appointments(
    request: Request,
    clinic_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
):
    user = await deps.require_auth(request)
    query: dict = {}

    user_doctor_id = None
    if user.get("role") == "DOCTOR" and user.get("clinic_id"):
        user_doctor = await db.doctors.find_one({"email": user.get("email", "").lower(), "clinic_id": user["clinic_id"]}, {"_id": 0})
        if user_doctor:
            user_doctor_id = user_doctor.get("doctor_id")

    if user.get("role") == "CLINIC_ADMIN" and user.get("clinic_id"):
        query["clinic_id"] = user["clinic_id"]
    elif user.get("role") in ["DOCTOR", "ASSISTANT"] and user.get("clinic_id"):
        query["clinic_id"] = user["clinic_id"]
    elif user.get("role") == "USER":
        query["patient_id"] = user["user_id"]

    if doctor_id:
        query["doctor_id"] = doctor_id
    if status:
        query["status"] = status
    if start_date:
        query.setdefault("date_time", {})["$gte"] = start_date
    if end_date:
        query.setdefault("date_time", {})["$lte"] = end_date

    appointments = await db.appointments.find(query, {"_id": 0}).to_list(500)
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"

        if user.get("role") == "CLINIC_ADMIN":
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            apt["is_own_patient"] = True
        elif user.get("role") == "DOCTOR":
            is_own_patient = user_doctor_id and apt["doctor_id"] == user_doctor_id
            apt["is_own_patient"] = bool(is_own_patient)
            if is_own_patient:
                patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
                apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
                apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            else:
                apt["patient_name"] = apt.get("patient_name", "Patient")
                apt["patient_email"] = None
                apt["notes"] = None
        elif user.get("role") == "ASSISTANT":
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = None
            apt["is_own_patient"] = False

    return appointments


@router.post("")
async def create_appointment(data: AppointmentCreate, request: Request):
    user = await deps.require_auth(request)
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

    appointment = {
        "appointment_id": f"apt_{datetime.now(timezone.utc).timestamp()}",
        "patient_id": user["user_id"],
        "patient_name": user.get("name"),
        "patient_email": user.get("email"),
        "patient_phone": user.get("phone"),
        "doctor_id": data.doctor_id,
        "clinic_id": data.clinic_id,
        "date_time": apt_datetime.isoformat(),
        "duration": data.duration or doctor.get("consultation_duration", 30),
        "status": "SCHEDULED",
        "notes": data.notes,
        "recurrence": data.recurrence.model_dump() if data.recurrence else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.appointments.insert_one(appointment)

    await send_notification_email(
        user_id=user["user_id"],
        appointment_id=appointment["appointment_id"],
        notification_type="BOOKING_CONFIRMATION",
        message=f"Your appointment with {doctor['name']} on {apt_datetime.strftime('%B %d, %Y at %H:%M')} has been confirmed.",
    )
    appointment.pop("_id", None)
    return appointment


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, data: AppointmentUpdate, request: Request):
    user = await deps.require_auth(request)
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.get("role") == "USER" and appointment["patient_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.get("role") == "CLINIC_ADMIN" and appointment["clinic_id"] != user["clinic_id"]:
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
    user = await deps.require_auth(request)
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.get("role") == "USER" and appointment["patient_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.get("role") == "CLINIC_ADMIN" and appointment["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    await db.appointments.update_one({"appointment_id": appointment_id}, {"$set": {"status": "CANCELLED"}})
    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="CANCELLATION",
        message="Your appointment has been cancelled.",
    )
    return {"message": "Appointment cancelled successfully"}


@router.post("/{appointment_id}/cancel")
async def cancel_appointment_with_reason(appointment_id: str, data: AppointmentCancel, request: Request, background_tasks: BackgroundTasks):
    user = await deps.require_auth(request)
    if user.get("role") not in ["CLINIC_ADMIN", "DOCTOR", "ASSISTANT"]:
        raise HTTPException(status_code=403, detail="Only clinic staff can use this cancellation method")

    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.get("role") == "CLINIC_ADMIN" and appointment["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.get("role") == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.get("email", "").lower(), "clinic_id": user.get("clinic_id")}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only cancel your own appointments")

    if not data.reason or len(data.reason.strip()) < 3:
        raise HTTPException(status_code=400, detail="Cancellation reason is required (minimum 3 characters)")

    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "status": "CANCELLED",
            "cancellation_reason": data.reason.strip(),
            "cancelled_by": user["user_id"],
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    patient = await db.users.find_one({"user_id": appointment["patient_id"]}, {"_id": 0})
    doctor = await db.doctors.find_one({"doctor_id": appointment["doctor_id"]}, {"_id": 0})
    clinic = await db.clinics.find_one({"clinic_id": appointment["clinic_id"]}, {"_id": 0})

    if patient and patient.get("email"):
        background_tasks.add_task(
            send_cancellation_notification_email,
            patient_email=patient["email"],
            patient_name=patient.get("name", "Patient"),
            doctor_name=doctor.get("name", "Doctor") if doctor else "Doctor",
            clinic_name=clinic.get("name", "Clinic") if clinic else "Clinic",
            appointment_date=appointment["date_time"],
            cancellation_reason=data.reason.strip(),
        )

    return {"message": "Appointment cancelled successfully", "reason": data.reason}


@router.get("/{appointment_id}/records")
async def get_appointment_records(appointment_id: str, request: Request):
    user = await deps.require_auth(request)
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.get("role") == "USER" and appointment["patient_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.get("role") == "CLINIC_ADMIN" and appointment["clinic_id"] != user["clinic_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.get("role") == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.get("email", "").lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="Access denied")

    prescriptions = await db.prescriptions.find({"appointment_id": appointment_id}, {"_id": 0}).to_list(100)
    medical_records = await db.medical_records.find({"appointment_id": appointment_id}, {"_id": 0}).to_list(100)
    return {"prescriptions": prescriptions, "medical_records": medical_records}


@router.post("/prescriptions")
async def create_prescription(data: PrescriptionCreate, request: Request):
    user = await deps.require_auth(request)
    if user.get("role") not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create prescriptions")

    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.get("role") == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.get("email", "").lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create prescriptions for your own appointments")

    prescription = {
        "prescription_id": f"presc_{datetime.now(timezone.utc).timestamp()}",
        "appointment_id": data.appointment_id,
        "patient_id": appointment["patient_id"],
        "doctor_id": appointment["doctor_id"],
        "clinic_id": appointment["clinic_id"],
        "medications": data.medications,
        "notes": data.notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.prescriptions.insert_one(prescription)
    prescription.pop("_id", None)
    return prescription


@router.post("/medical-records")
async def create_medical_record(data: MedicalRecordCreate, request: Request):
    user = await deps.require_auth(request)
    if user.get("role") not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create medical records")

    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if user.get("role") == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.get("email", "").lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create records for your own appointments")

    record = {
        "record_id": f"rec_{datetime.now(timezone.utc).timestamp()}",
        "appointment_id": data.appointment_id,
        "patient_id": appointment["patient_id"],
        "doctor_id": appointment["doctor_id"],
        "clinic_id": appointment["clinic_id"],
        "record_type": data.record_type,
        "title": data.title,
        "content": data.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.medical_records.insert_one(record)
    record.pop("_id", None)
    return record
