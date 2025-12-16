from fastapi import APIRouter, Request
from datetime import datetime, timezone

from app.core.database import db
from app.api import deps

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats(request: Request):
    user = await deps.require_auth(request)
    if user.get("role") == "CLINIC_ADMIN" and user.get("clinic_id"):
        clinic_id = user["clinic_id"]
        total_appointments = await db.appointments.count_documents({"clinic_id": clinic_id})
        total_doctors = await db.doctors.count_documents({"clinic_id": clinic_id, "is_active": True})
        total_staff = await db.staff.count_documents({"clinic_id": clinic_id, "is_active": True})
        total_services = await db.services.count_documents({"clinic_id": clinic_id, "is_active": True})

        now = datetime.now(timezone.utc).isoformat()
        upcoming = await db.appointments.count_documents({
            "clinic_id": clinic_id,
            "date_time": {"$gte": now},
            "status": {"$ne": "CANCELLED"}
        })
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
        today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat()
        today_appointments = await db.appointments.count_documents({
            "clinic_id": clinic_id,
            "date_time": {"$gte": today_start, "$lte": today_end},
            "status": {"$ne": "CANCELLED"}
        })
        pipeline = [
            {"$match": {"clinic_id": clinic_id}},
            {"$group": {"_id": "$patient_id"}},
            {"$count": "total"}
        ]
        result = await db.appointments.aggregate(pipeline).to_list(1)
        total_patients = result[0]["total"] if result else 0
        return {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming,
            "today_appointments": today_appointments,
            "total_doctors": total_doctors,
            "total_staff": total_staff,
            "total_services": total_services,
            "total_patients": total_patients
        }
    else:
        total_appointments = await db.appointments.count_documents({"patient_id": user["user_id"]})
        now = datetime.now(timezone.utc).isoformat()
        upcoming = await db.appointments.count_documents({
            "patient_id": user["user_id"],
            "date_time": {"$gte": now},
            "status": {"$ne": "CANCELLED"}
        })
        return {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming
        }


@router.get("/revenue")
async def get_revenue_stats(request: Request, period: str = "month"):
    await deps.require_clinic_admin(request)
    return {
        "period": period,
        "total_revenue": 15000.00,
        "appointments_count": 120,
        "average_per_appointment": 125.00
    }


@router.get("/staff")
async def get_staff_stats(request: Request):
    user = await deps.require_staff_or_admin(request)
    if not user.get("clinic_id"):
        return {"today_appointments": 0, "upcoming_appointments": 0, "total_patients": 0}

    clinic_id = user["clinic_id"]
    now = datetime.now(timezone.utc).isoformat()
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
    today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat()

    query_filter = {"clinic_id": clinic_id, "status": {"$ne": "CANCELLED"}}
    if user.get("role") == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.get("email", "").lower(), "clinic_id": clinic_id}, {"_id": 0})
        if doctor:
            query_filter["doctor_id"] = doctor["doctor_id"]

    today_appointments = await db.appointments.count_documents({**query_filter, "date_time": {"$gte": today_start, "$lte": today_end}})
    upcoming = await db.appointments.count_documents({**query_filter, "date_time": {"$gte": now}})

    pipeline = [
        {"$match": query_filter},
        {"$group": {"_id": "$patient_id"}},
        {"$count": "total"}
    ]
    result = await db.appointments.aggregate(pipeline).to_list(1)
    total_patients = result[0]["total"] if result else 0

    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    return {
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming,
        "total_patients": total_patients,
        "clinic_name": clinic.get('name', 'Medical Center') if clinic else 'Medical Center'
    }
