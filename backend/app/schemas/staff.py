from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class StaffMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    staff_id: str = Field(default_factory=lambda: f"staff_{uuid.uuid4().hex[:12]}")
    
    # Support both old and new system
    organization_id: Optional[str] = None  # Organization they belong to (new RBAC)
    clinic_id: Optional[str] = None  # DEPRECATED: kept for backward compatibility
    
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"  # RECEPTIONIST, NURSE, DOCTOR, ADMIN
    
    # Location access (None = can access all locations)
    assigned_location_ids: Optional[list] = None
    
    is_active: bool = True
    invitation_status: str = "PENDING"
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StaffCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"
    location_id: Optional[str] = None  # Location assignment from frontend


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
