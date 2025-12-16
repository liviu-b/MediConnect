from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    doctor_id: str = Field(default_factory=lambda: f"doctor_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: int = 30
    consultation_fee: float = 0.0
    currency: str = "LEI"
    is_active: bool = True
    availability_schedule: dict = Field(default_factory=lambda: {
        "monday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "tuesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "wednesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "thursday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "friday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "saturday": [{"start": "10:00", "end": "14:00"}],
        "sunday": []
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DoctorCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: int = 30
    consultation_fee: float = 0.0
    currency: str = "LEI"
    availability_schedule: Optional[dict] = None


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: Optional[int] = None
    consultation_fee: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[dict] = None
