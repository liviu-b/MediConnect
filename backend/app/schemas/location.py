from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Location(BaseModel):
    """
    Location represents a physical clinic/branch within an organization.
    Previously called 'Clinic' - now renamed to support multi-location model.
    """
    model_config = ConfigDict(extra="ignore")
    location_id: str = Field(default_factory=lambda: f"loc_{uuid.uuid4().hex[:12]}")
    organization_id: str  # Parent organization
    
    # Location details
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    
    # Location-specific settings
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
    
    # Metadata
    is_active: bool = True
    is_primary: bool = False  # First location created is primary
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class LocationCreate(BaseModel):
    """Data needed to create a new location"""
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    working_hours: Optional[dict] = None
    settings: Optional[dict] = None
    is_primary: Optional[bool] = False


class LocationUpdate(BaseModel):
    """Fields that can be updated"""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    working_hours: Optional[dict] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
