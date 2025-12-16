from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    user_id: str
    user_name: str
    rating: int
    comment: Optional[str] = None
    admin_response: Optional[str] = None
    admin_response_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewCreate(BaseModel):
    clinic_id: str
    rating: int
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    response: str
