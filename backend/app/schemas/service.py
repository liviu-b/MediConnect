from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"
