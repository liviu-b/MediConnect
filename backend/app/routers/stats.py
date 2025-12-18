from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from ..db import db
from .auth import get_current_user

router = APIRouter(tags=["stats"])


@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    Get dashboard statistics based on user role
    """
    user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.get("user_id")
    role = current_user.role if hasattr(current_user, 'role') else current_user.get("role")
    clinic_id = current_user.clinic_id if hasattr(current_user, 'clinic_id') else current_user.get("clinic_id")

    stats = {}

    try:
        if role == "CLINIC_ADMIN":
            # Clinic admin stats
            if not clinic_id:
                raise HTTPException(status_code=400, detail="Clinic ID not found for admin")

            # Today's appointments
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_appointments = await db.appointments.count_documents({
                "clinic_id": clinic_id,
                "date_time": {
                    "$gte": today_start.isoformat(),
                    "$lt": today_end.isoformat()
                },
                "status": {"$ne": "CANCELLED"}
            })

            # Upcoming appointments (from now onwards)
            now = datetime.now()
            upcoming_appointments = await db.appointments.count_documents({
                "clinic_id": clinic_id,
                "date_time": {"$gte": now.isoformat()},
                "status": {"$ne": "CANCELLED"}
            })

            # Total doctors
            total_doctors = await db.doctors.count_documents({
                "clinic_id": clinic_id
            })

            # Total patients (unique patients who have appointments)
            pipeline = [
                {"$match": {"clinic_id": clinic_id}},
                {"$group": {"_id": "$patient_id"}},
                {"$count": "total"}
            ]
            patient_result = await db.appointments.aggregate(pipeline).to_list(1)
            total_patients = patient_result[0]["total"] if patient_result else 0

            # Total staff
            total_staff = await db.staff.count_documents({
                "clinic_id": clinic_id
            })

            # Total services
            total_services = await db.services.count_documents({
                "clinic_id": clinic_id
            })

            # Total appointments (all time)
            total_appointments = await db.appointments.count_documents({
                "clinic_id": clinic_id
            })

            stats = {
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_staff": total_staff,
                "total_services": total_services,
                "total_appointments": total_appointments
            }

        elif role == "DOCTOR" or role == "ASSISTANT":
            # Staff stats
            if not clinic_id:
                raise HTTPException(status_code=400, detail="Clinic ID not found for staff")

            # Today's appointments for this doctor
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            query = {"clinic_id": clinic_id}
            if role == "DOCTOR":
                query["doctor_id"] = user_id

            today_appointments = await db.appointments.count_documents({
                **query,
                "date_time": {
                    "$gte": today_start.isoformat(),
                    "$lt": today_end.isoformat()
                },
                "status": {"$ne": "CANCELLED"}
            })

            # Upcoming appointments
            now = datetime.now()
            upcoming_appointments = await db.appointments.count_documents({
                **query,
                "date_time": {"$gte": now.isoformat()},
                "status": {"$ne": "CANCELLED"}
            })

            # Total appointments
            total_appointments = await db.appointments.count_documents(query)

            stats = {
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "total_appointments": total_appointments
            }

        elif role == "USER":
            # Patient stats
            now = datetime.now()
            
            # Upcoming appointments
            upcoming_appointments = await db.appointments.count_documents({
                "patient_id": user_id,
                "date_time": {"$gte": now.isoformat()},
                "status": {"$ne": "CANCELLED"}
            })

            # Total appointments
            total_appointments = await db.appointments.count_documents({
                "patient_id": user_id
            })

            stats = {
                "upcoming_appointments": upcoming_appointments,
                "total_appointments": total_appointments
            }

        else:
            raise HTTPException(status_code=403, detail="Invalid user role")

        return stats

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")
