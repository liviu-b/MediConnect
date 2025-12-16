from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from ..db import db
from ..schemas.medical_record import MedicalRecord, MedicalRecordCreate
from ..schemas.prescription import Prescription, PrescriptionCreate
from ..security import require_auth

router = APIRouter(prefix="", tags=["records"])


@router.get("/patients/{patient_id}/history")
async def get_patient_history(patient_id: str, request: Request):
    user = await require_auth(request)
    if user.role == "USER" and user.user_id != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if not doctor:
            raise HTTPException(status_code=403, detail="Doctor record not found")
        has_appointment = await db.appointments.find_one({
            "patient_id": patient_id,
            "doctor_id": doctor["doctor_id"],
            "status": "COMPLETED"
        }, {"_id": 0})
        if not has_appointment:
            raise HTTPException(status_code=403, detail="You can only view history for patients you have treated")
    if user.role == "CLINIC_ADMIN":
        patient_in_clinic = await db.appointments.find_one({"patient_id": patient_id, "clinic_id": user.clinic_id}, {"_id": 0})
        if not patient_in_clinic:
            raise HTTPException(status_code=403, detail="Patient not found in your clinic")
    patient = await db.users.find_one({"user_id": patient_id}, {"_id": 0, "password_hash": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    query_filter = {"patient_id": patient_id}
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        query_filter["doctor_id"] = doctor["doctor_id"]
    elif user.role == "CLINIC_ADMIN":
        query_filter["clinic_id"] = user.clinic_id
    appointments = await db.appointments.find(query_filter, {"_id": 0}).sort("date_time", -1).to_list(100)
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"
    prescriptions = await db.prescriptions.find(
        {"patient_id": patient_id} if user.role != "DOCTOR" else {"patient_id": patient_id, "doctor_id": doctor["doctor_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    medical_records = await db.medical_records.find(
        {"patient_id": patient_id} if user.role != "DOCTOR" else {"patient_id": patient_id, "doctor_id": doctor["doctor_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {
        "patient": patient,
        "appointments": appointments,
        "prescriptions": prescriptions,
        "medical_records": medical_records
    }


@router.post("/prescriptions")
async def create_prescription(data: PrescriptionCreate, request: Request):
    user = await require_auth(request)
    if user.role not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create prescriptions")
    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create prescriptions for your own appointments")
    prescription = Prescription(
        appointment_id=data.appointment_id,
        patient_id=appointment["patient_id"],
        doctor_id=appointment["doctor_id"],
        clinic_id=appointment["clinic_id"],
        medications=data.medications,
        notes=data.notes
    )
    doc = prescription.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.prescriptions.insert_one(doc)
    return prescription


@router.post("/medical-records")
async def create_medical_record(data: MedicalRecordCreate, request: Request):
    user = await require_auth(request)
    if user.role not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create medical records")
    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create medical records for your own appointments")
    record = MedicalRecord(
        appointment_id=data.appointment_id,
        patient_id=appointment["patient_id"],
        doctor_id=appointment["doctor_id"],
        clinic_id=appointment["clinic_id"],
        record_type=data.record_type,
        title=data.title,
        content=data.content
    )
    doc = record.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.medical_records.insert_one(doc)
    return record
