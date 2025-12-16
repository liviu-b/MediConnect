from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid


class MedicalRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    appointment_id: str
    patient_id: str
    doctor_id: str
    clinic_id: str
    record_type: str = "RECOMMENDATION"
    title: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MedicalRecordCreate(BaseModel):
    appointment_id: str
    record_type: str = "RECOMMENDATION"
    title: str
    content: str
