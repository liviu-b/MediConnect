from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Clinic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clinic_id: str = Field(default_factory=lambda: f"clinic_{uuid.uuid4().hex[:12]}")
    cui: str
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = True
    is_profile_complete: bool = False
    working_hours: dict = Field(default_factory=lambda: {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": None
    })
    settings: dict = Field(default_factory=lambda: {
        "allow_online_booking": True,
        "booking_advance_days": 30,
        "cancellation_hours": 24,
        "reminder_hours": 24
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    working_hours: Optional[dict] = None
    settings: Optional[dict] = None


class ClinicRegistration(BaseModel):
    cui: str
    admin_name: str
    admin_email: str
    admin_password: str
