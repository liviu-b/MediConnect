from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
import uuid

from pydantic import BaseModel, Field, ConfigDict


class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id: str
    appointment_id: str
    notification_type: str
    status: str = "SENT"
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RegistrationCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str
    is_used: bool = False
    used_by_clinic_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
