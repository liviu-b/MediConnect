from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone, timedelta

from ..db import db
from ..schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentCancel
from ..schemas.user import UserRole
from ..schemas.permission import PermissionConstants
from ..schemas.audit_log import AuditActions
from ..security import require_auth
from ..services.notifications import send_notification_email
from ..services.email import (
    send_appointment_confirmation_email,
    send_cancellation_notification_email,
    send_appointment_reminder_email
)
from ..services.permissions import PermissionService
from ..middleware.permissions import (
    require_permission,
    block_admin_appointment_modification,
    check_appointment_access
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


async def create_recurring_appointments(base_appointment, recurrence, user, doctor, clinic):
    """
    Create recurring appointments based on the recurrence pattern.
    
    Args:
        base_appointment: The initial appointment
        recurrence: RecurrencePattern with frequency and end_date
        user: The patient user object
        doctor: The doctor document
        clinic: The clinic document
    
    Returns:
        List of created recurring appointments
    """
    import uuid
    from ..schemas.common import RecurrencePattern
    
    recurring_appointments = []
    current_date = base_appointment.date_time
    end_date = recurrence.end_date
    
    # Limit to maximum 52 occurrences (1 year weekly) to prevent abuse
    max_occurrences = 52
    occurrence_count = 0
    
    while occurrence_count < max_occurrences:
        # Calculate next occurrence based on frequency
        if recurrence.frequency == "daily":
            current_date = current_date + timedelta(days=1)
        elif recurrence.frequency == "weekly":
            current_date = current_date + timedelta(weeks=1)
        elif recurrence.frequency == "monthly":
            # Add one month (approximately 30 days, adjust for month boundaries)
            current_date = current_date + timedelta(days=30)
        else:
            break
        
        # Stop if we've passed the end date
        if end_date and current_date > end_date:
            break
        
        # Check if slot is available
        existing = await db.appointments.find_one({
            "doctor_id": base_appointment.doctor_id,
            "date_time": current_date.isoformat(),
            "status": {"$ne": "CANCELLED"}
        })
        
        if existing:
            # Skip this slot if already booked
            continue
        
        # Create recurring appointment
        recurring_apt = Appointment(
            appointment_id=f"apt_{uuid.uuid4().hex[:12]}",
            patient_id=user.user_id,
            patient_name=user.name,
            patient_email=user.email,
            patient_phone=user.phone,
            doctor_id=base_appointment.doctor_id,
            clinic_id=base_appointment.clinic_id,
            date_time=current_date,
            duration=base_appointment.duration,
            notes=base_appointment.notes,
            status="SCHEDULED",
            parent_appointment_id=base_appointment.appointment_id,  # Link to parent
            recurrence=None  # Recurring appointments don't have their own recurrence
        )
        
        doc = recurring_apt.model_dump()
        doc['date_time'] = doc['date_time'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.appointments.insert_one(doc)
        recurring_appointments.append(recurring_apt)
        occurrence_count += 1
    
    return recurring_appointments


@router.get("")
async def get_appointments(
    request: Request,
    clinic_id: Optional[str] = None,
    location_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get appointments with permission-based filtering.
    
    - SUPER_ADMIN: Can view all appointments in organization
    - LOCATION_ADMIN: Can view appointments in assigned locations
    - RECEPTIONIST: Can view appointments in assigned locations
    - DOCTOR: Can view only own appointments
    - ASSISTANT: Can view appointments in assigned locations
    - USER: Can view only own appointments
    """
    user = await require_auth(request)

    # Check view permission
    can_view = await PermissionService.can_view_appointments(user, location_id)
    if not can_view:
        raise HTTPException(status_code=403, detail="You do not have permission to view appointments")

    query = {}

    # Get accessible locations for the user
    accessible_locations = await PermissionService.get_accessible_locations(user)

    # Role-based filtering
    if user.role == UserRole.USER:
        # Patients can only see their own appointments
        query["patient_id"] = user.user_id
    
    elif user.role == UserRole.DOCTOR:
        # Doctors can only see their own appointments
        user_doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if user_doctor:
            query["doctor_id"] = user_doctor.get("doctor_id")
        else:
            # No doctor profile, return empty
            return []
    
    elif user.role in [UserRole.SUPER_ADMIN, UserRole.LOCATION_ADMIN, UserRole.RECEPTIONIST, UserRole.ASSISTANT]:
        # Staff can see appointments in their accessible locations
        if accessible_locations:
            query["$or"] = [
                {"location_id": {"$in": accessible_locations}},
                {"clinic_id": {"$in": accessible_locations}}  # Legacy support
            ]
        else:
            return []

    # Apply additional filters
    if location_id:
        query["$or"] = [
            {"location_id": location_id},
            {"clinic_id": location_id}  # Legacy support
        ]
    
    if clinic_id:
        query["$or"] = [
            {"location_id": clinic_id},
            {"clinic_id": clinic_id}
        ]
    
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

    # Enrich appointment data
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"

        # Patient information visibility based on role
        if user.role in [UserRole.SUPER_ADMIN, UserRole.LOCATION_ADMIN, UserRole.RECEPTIONIST]:
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            apt["is_own_patient"] = True
        
        elif user.role == UserRole.DOCTOR:
            # Doctors see full info for their own appointments
            apt["is_own_patient"] = True
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
        
        elif user.role == UserRole.ASSISTANT:
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = None  # Assistants don't see email
            apt["is_own_patient"] = False

    # Log the view action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.APPOINTMENT_VIEW,
        resource_type="appointment",
        description=f"Viewed {len(appointments)} appointments",
        metadata={"count": len(appointments), "filters": {"location_id": location_id, "doctor_id": doctor_id}},
        status="success"
    )

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
    
    # Handle recurring appointments
    recurring_appointments = []
    if data.recurrence and data.recurrence.frequency != "none":
        recurring_appointments = await create_recurring_appointments(
            base_appointment=appointment,
            recurrence=data.recurrence,
            user=user,
            doctor=doctor,
            clinic=clinic
        )

    # Send confirmation email to patient
    send_appointment_confirmation_email(
        patient_email=user.email,
        patient_name=user.name,
        doctor_name=doctor.get('name', 'Unknown'),
        clinic_name=clinic.get('name', 'Unknown'),
        appointment_date=apt_datetime.isoformat(),
        appointment_id=appointment.appointment_id,
        clinic_address=clinic.get('address')
    )
    
    # Also log notification
    await send_notification_email(
        user_id=user.user_id,
        appointment_id=appointment.appointment_id,
        notification_type="BOOKING_CONFIRMATION",
        message=f"Your appointment with {doctor['name']} on {apt_datetime.strftime('%B %d, %Y at %H:%M')} has been confirmed." + 
                (f" ({len(recurring_appointments)} recurring appointments created)" if recurring_appointments else "")
    )

    return {
        **appointment.model_dump(),
        "recurring_count": len(recurring_appointments) if recurring_appointments else 0
    }


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
    
    # Get doctor and clinic info for email
    doctor = await db.doctors.find_one({"doctor_id": appointment["doctor_id"]}, {"_id": 0})
    clinic = await db.clinics.find_one({"clinic_id": appointment["clinic_id"]}, {"_id": 0})
    
    # Send cancellation email to patient
    send_cancellation_notification_email(
        patient_email=appointment.get("patient_email", ""),
        patient_name=appointment.get("patient_name", ""),
        doctor_name=doctor.get("name", "Unknown") if doctor else "Unknown",
        clinic_name=clinic.get("name", "Unknown") if clinic else "Unknown",
        appointment_date=appointment.get("date_time", ""),
        cancellation_reason=data.reason.strip()
    )

    return {"message": "Appointment cancelled successfully", "reason": data.reason}


@router.post("/{appointment_id}/accept")
@block_admin_appointment_modification()
async def accept_appointment(appointment_id: str, request: Request):
    """
    Accept a pending appointment.
    
    CRITICAL: Only RECEPTIONIST can accept appointments.
    SUPER_ADMIN and LOCATION_ADMIN are BLOCKED (view-only).
    """
    user = await require_auth(request)
    
    # Check permission
    can_accept = await PermissionService.can_accept_appointments(user)
    if not can_accept:
        await PermissionService.log_action(
            user=user,
            action=AuditActions.APPOINTMENT_ACCEPT_DENIED,
            resource_type="appointment",
            resource_id=appointment_id,
            description="Attempted to accept appointment without permission",
            status="denied",
            severity="warning"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to accept appointments. Only Receptionists can perform this action."
        )
    
    # Check appointment access
    has_access = await check_appointment_access(user, appointment_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="You do not have access to this appointment")
    
    # Get appointment
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update status
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {
            "$set": {
                "status": "CONFIRMED",
                "accepted_by": user.user_id,
                "accepted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log the action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.APPOINTMENT_ACCEPT,
        resource_type="appointment",
        resource_id=appointment_id,
        description=f"Accepted appointment for patient {appointment.get('patient_name')}",
        metadata={"patient_id": appointment.get("patient_id"), "doctor_id": appointment.get("doctor_id")},
        status="success"
    )
    
    # Send notification
    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="APPOINTMENT_CONFIRMED",
        message="Your appointment has been confirmed."
    )
    
    return {"message": "Appointment accepted successfully", "appointment_id": appointment_id}


@router.post("/{appointment_id}/reject")
@block_admin_appointment_modification()
async def reject_appointment(appointment_id: str, request: Request, reason: Optional[str] = None):
    """
    Reject a pending appointment.
    
    CRITICAL: Only RECEPTIONIST and DOCTOR can reject appointments.
    SUPER_ADMIN and LOCATION_ADMIN are BLOCKED (view-only).
    """
    user = await require_auth(request)
    
    # Check permission
    result = await PermissionService.check_permission(
        user=user,
        permission=PermissionConstants.APPOINTMENTS_REJECT,
        resource_id=appointment_id
    )
    
    if not result.allowed:
        await PermissionService.log_action(
            user=user,
            action=AuditActions.PERMISSION_DENIED,
            resource_type="appointment",
            resource_id=appointment_id,
            description="Attempted to reject appointment without permission",
            status="denied",
            severity="warning"
        )
        raise HTTPException(status_code=403, detail=result.reason)
    
    # Check appointment access
    has_access = await check_appointment_access(user, appointment_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="You do not have access to this appointment")
    
    # Get appointment
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update status
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {
            "$set": {
                "status": "REJECTED",
                "rejected_by": user.user_id,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "rejection_reason": reason or "No reason provided"
            }
        }
    )
    
    # Log the action
    await PermissionService.log_action(
        user=user,
        action=AuditActions.APPOINTMENT_REJECT,
        resource_type="appointment",
        resource_id=appointment_id,
        description=f"Rejected appointment for patient {appointment.get('patient_name')}",
        metadata={"patient_id": appointment.get("patient_id"), "reason": reason},
        status="success"
    )
    
    # Send notification
    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="APPOINTMENT_REJECTED",
        message=f"Your appointment has been rejected. Reason: {reason or 'Not specified'}"
    )
    
    return {"message": "Appointment rejected successfully", "appointment_id": appointment_id}
