from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional
from collections import defaultdict

from ..db import db
from ..security import require_auth

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(request: Request, days: int = 30):
    """
    Get analytics overview for Super Admin or Clinic Admin.
    
    Tracks:
    - Appointments (total, by status, by location, trends)
    - Doctors (total, appointments per doctor)
    - Patients (total, new, active)
    - Locations (performance comparison)
    - Time patterns (busiest days/hours)
    
    Does NOT track financial data (revenue, payments, etc.)
    """
    user = await require_auth(request)
    
    # Only admins can access analytics
    if user.role not in ["SUPER_ADMIN", "CLINIC_ADMIN", "LOCATION_ADMIN"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Determine query filter based on role
    query_filter = {}
    
    if user.role == "SUPER_ADMIN":
        # Super Admin sees all locations in their organization
        if not user.organization_id:
            raise HTTPException(status_code=404, detail="User is not associated with an organization")
        
        # Get all locations in organization
        locations = await db.locations.find(
            {"organization_id": user.organization_id, "is_active": True},
            {"_id": 0, "location_id": 1}
        ).to_list(100)
        
        location_ids = [loc["location_id"] for loc in locations]
        
        if location_ids:
            query_filter["location_id"] = {"$in": location_ids}
        else:
            # No locations, return empty data
            return _empty_analytics()
    
    elif user.role == "CLINIC_ADMIN":
        # Clinic Admin sees only their clinic
        if not user.clinic_id:
            raise HTTPException(status_code=404, detail="User does not have a clinic assigned")
        query_filter["clinic_id"] = user.clinic_id
    
    elif user.role == "LOCATION_ADMIN":
        # Location Admin sees their assigned locations
        if user.assigned_location_ids:
            query_filter["location_id"] = {"$in": user.assigned_location_ids}
        else:
            return _empty_analytics()
    
    # Date range for trends
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # ========================================
    # 1. APPOINTMENTS ANALYTICS
    # ========================================
    appointments_query = {**query_filter}
    appointments = await db.appointments.find(appointments_query, {"_id": 0}).to_list(10000)
    
    total_appointments = len(appointments)
    
    # Count by status
    status_counts = defaultdict(int)
    for apt in appointments:
        status_counts[apt.get("status", "SCHEDULED")] += 1
    
    # Appointments by location
    appointments_by_location = defaultdict(int)
    for apt in appointments:
        location_id = apt.get("location_id")
        if location_id:
            appointments_by_location[location_id] += 1
    
    # Get location names
    location_data = []
    for location_id, count in appointments_by_location.items():
        location = await db.locations.find_one({"location_id": location_id}, {"_id": 0, "name": 1})
        location_data.append({
            "location": location.get("name", "Unknown") if location else "Unknown",
            "count": count
        })
    
    # Sort by count descending
    location_data.sort(key=lambda x: x["count"], reverse=True)
    
    # Appointments over time (last N days)
    appointments_trend = defaultdict(int)
    
    for apt in appointments:
        apt_date_str = apt.get("date_time")
        if apt_date_str:
            try:
                apt_date = datetime.fromisoformat(apt_date_str.replace("Z", "+00:00"))
                if apt_date >= start_date:
                    date_key = apt_date.strftime("%Y-%m-%d")
                    appointments_trend[date_key] += 1
            except Exception:
                pass
    
    # Fill in missing dates with 0
    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime("%Y-%m-%d")
        trend_data.append({
            "date": date_key,
            "count": appointments_trend.get(date_key, 0)
        })
        current_date += timedelta(days=1)
    
    # Busiest days of week
    day_of_week_counts = defaultdict(int)
    for apt in appointments:
        apt_date_str = apt.get("date_time")
        if apt_date_str:
            try:
                apt_date = datetime.fromisoformat(apt_date_str.replace("Z", "+00:00"))
                day_name = apt_date.strftime("%A")  # Monday, Tuesday, etc.
                day_of_week_counts[day_name] += 1
            except Exception:
                pass
    
    busiest_days = [
        {"day": day, "count": count}
        for day, count in sorted(day_of_week_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Busiest hours
    hour_counts = defaultdict(int)
    for apt in appointments:
        apt_date_str = apt.get("date_time")
        if apt_date_str:
            try:
                apt_date = datetime.fromisoformat(apt_date_str.replace("Z", "+00:00"))
                hour = apt_date.hour
                hour_counts[hour] += 1
            except Exception:
                pass
    
    busiest_hours = [
        {"hour": f"{hour:02d}:00", "count": count}
        for hour, count in sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # ========================================
    # 2. DOCTORS ANALYTICS
    # ========================================
    doctors_query = {**query_filter}
    doctors = await db.doctors.find(doctors_query, {"_id": 0}).to_list(1000)
    total_doctors = len(doctors)
    
    # Appointments per doctor
    doctor_appointments = defaultdict(int)
    for apt in appointments:
        doctor_id = apt.get("doctor_id")
        if doctor_id:
            doctor_appointments[doctor_id] += 1
    
    # Top doctors by appointments
    top_doctors = []
    for doctor_id, apt_count in sorted(doctor_appointments.items(), key=lambda x: x[1], reverse=True)[:10]:
        doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0, "name": 1, "specialty": 1})
        if doctor:
            top_doctors.append({
                "name": doctor.get("name", "Unknown"),
                "specialty": doctor.get("specialty", ""),
                "appointments": apt_count
            })
    
    # ========================================
    # 3. PATIENTS ANALYTICS
    # ========================================
    # Count unique patients from appointments
    unique_patients = set()
    for apt in appointments:
        patient_id = apt.get("patient_id")
        if patient_id:
            unique_patients.add(patient_id)
    
    total_patients = len(unique_patients)
    
    # New patients (first appointment in date range)
    new_patients = 0
    for patient_id in unique_patients:
        patient_appointments = [apt for apt in appointments if apt.get("patient_id") == patient_id]
        if patient_appointments:
            # Sort by date
            patient_appointments.sort(key=lambda x: x.get("date_time", ""))
            first_apt_date_str = patient_appointments[0].get("date_time")
            if first_apt_date_str:
                try:
                    first_apt_date = datetime.fromisoformat(first_apt_date_str.replace("Z", "+00:00"))
                    if first_apt_date >= start_date:
                        new_patients += 1
                except Exception:
                    pass
    
    # ========================================
    # 4. LOCATIONS ANALYTICS
    # ========================================
    locations_query = {"is_active": True}
    if user.role == "SUPER_ADMIN" and user.organization_id:
        locations_query["organization_id"] = user.organization_id
    
    locations_list = await db.locations.find(locations_query, {"_id": 0}).to_list(100)
    total_locations = len(locations_list)
    
    # ========================================
    # 5. SERVICES ANALYTICS
    # ========================================
    services_query = {}
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        services_query["clinic_id"] = user.clinic_id
    
    services = await db.services.find(services_query, {"_id": 0}).to_list(1000)
    total_services = len(services)
    
    # ========================================
    # 6. COMPLETION RATE
    # ========================================
    completion_rate = 0
    if total_appointments > 0:
        completed = status_counts.get("COMPLETED", 0)
        completion_rate = round((completed / total_appointments) * 100, 1)
    
    # ========================================
    # RETURN ANALYTICS DATA
    # ========================================
    return {
        "overview": {
            "total_appointments": total_appointments,
            "total_patients": total_patients,
            "new_patients": new_patients,
            "total_doctors": total_doctors,
            "total_locations": total_locations,
            "total_services": total_services,
            "completed_appointments": status_counts.get("COMPLETED", 0),
            "cancelled_appointments": status_counts.get("CANCELLED", 0),
            "scheduled_appointments": status_counts.get("SCHEDULED", 0),
            "confirmed_appointments": status_counts.get("CONFIRMED", 0),
            "completion_rate": completion_rate
        },
        "appointments_trend": trend_data,
        "appointments_by_location": location_data,
        "appointments_by_status": [
            {"status": "Completed", "count": status_counts.get("COMPLETED", 0), "color": "#10b981"},
            {"status": "Confirmed", "count": status_counts.get("CONFIRMED", 0), "color": "#3b82f6"},
            {"status": "Scheduled", "count": status_counts.get("SCHEDULED", 0), "color": "#f59e0b"},
            {"status": "Cancelled", "count": status_counts.get("CANCELLED", 0), "color": "#ef4444"}
        ],
        "top_doctors": top_doctors,
        "busiest_days": busiest_days,
        "busiest_hours": busiest_hours,
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "days": days
        }
    }


def _empty_analytics():
    """Return empty analytics structure"""
    return {
        "overview": {
            "total_appointments": 0,
            "total_patients": 0,
            "new_patients": 0,
            "total_doctors": 0,
            "total_locations": 0,
            "total_services": 0,
            "completed_appointments": 0,
            "cancelled_appointments": 0,
            "scheduled_appointments": 0,
            "confirmed_appointments": 0,
            "completion_rate": 0
        },
        "appointments_trend": [],
        "appointments_by_location": [],
        "appointments_by_status": [],
        "top_doctors": [],
        "busiest_days": [],
        "busiest_hours": [],
        "date_range": {
            "start": "",
            "end": "",
            "days": 0
        }
    }
