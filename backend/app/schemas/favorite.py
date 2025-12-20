from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FavoriteDoctor(BaseModel):
    """Favorite doctor model"""
    model_config = ConfigDict(extra="ignore")
    
    favorite_id: str = Field(default_factory=lambda: f"fav_{__import__('uuid').uuid4().hex[:12]}")
    user_id: str  # Patient ID
    doctor_id: str
    
    # Cached doctor info for quick access
    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    doctor_clinic_id: Optional[str] = None
    doctor_clinic_name: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None  # Personal notes about the doctor
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_appointment_date: Optional[datetime] = None  # Track last visit


class FavoriteDoctorCreate(BaseModel):
    """Create favorite doctor request"""
    doctor_id: str
    notes: Optional[str] = None


class FavoriteDoctorUpdate(BaseModel):
    """Update favorite doctor"""
    notes: Optional[str] = None


class FavoriteDoctorStats(BaseModel):
    """Statistics for favorite doctors"""
    total_favorites: int = 0
    total_appointments: int = 0  # Total appointments with favorite doctors
    last_visit: Optional[datetime] = None
