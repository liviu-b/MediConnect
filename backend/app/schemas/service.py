from datetime import datetime, timezone
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    
    # Support both old and new system
    clinic_id: Optional[str] = None  # Legacy field
    organization_id: Optional[str] = None  # New RBAC system
    location_id: Optional[str] = None  # New RBAC system
    
    name: str  # Keep for backward compatibility
    name_en: Optional[str] = None
    name_ro: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceCreate(BaseModel):
    name: str  # Keep for backward compatibility
    name_en: Optional[str] = None
    name_ro: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"
