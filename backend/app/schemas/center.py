from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class MedicalCenter(BaseModel):
    """Medical center model with location-based filtering support"""
    center_id: str = Field(default_factory=lambda: f"center_{uuid.uuid4().hex[:12]}")
    name: str
    specialty: str
    address: str
    city: str
    county: str
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MedicalCenterCreate(BaseModel):
    """Schema for creating a new medical center"""
    name: str
    specialty: str
    address: str
    city: str
    county: str
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class MedicalCenterUpdate(BaseModel):
    """Schema for updating a medical center"""
    name: Optional[str] = None
    specialty: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class MedicalCenterResponse(BaseModel):
    """Response schema for medical center"""
    center_id: str
    name: str
    specialty: str
    address: str
    city: str
    county: str
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
