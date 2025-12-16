from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Prescription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    prescription_id: str = Field(default_factory=lambda: f"presc_{uuid.uuid4().hex[:12]}")
    appointment_id: str
    patient_id: str
    doctor_id: str
    clinic_id: str
    medications: List[dict] = []
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrescriptionCreate(BaseModel):
    appointment_id: str
    medications: List[dict] = []
    notes: Optional[str] = None
