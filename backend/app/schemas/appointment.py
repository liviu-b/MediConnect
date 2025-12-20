from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid
from .common import RecurrencePattern


class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    appointment_id: str = Field(default_factory=lambda: f"apt_{uuid.uuid4().hex[:12]}")
    patient_id: str
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    doctor_id: str
    clinic_id: str  # DEPRECATED: kept for backward compatibility
    location_id: Optional[str] = None  # New multi-location support
    date_time: datetime
    duration: int = 30
    status: str = "SCHEDULED"
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    accepted_by: Optional[str] = None  # Who accepted the appointment
    accepted_at: Optional[datetime] = None  # When it was accepted
    rejected_by: Optional[str] = None  # Who rejected the appointment
    rejected_at: Optional[datetime] = None  # When it was rejected
    rejection_reason: Optional[str] = None  # Why it was rejected
    recurrence: Optional[RecurrencePattern] = None
    parent_appointment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
