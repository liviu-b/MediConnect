from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")


class RecurrencePattern(BaseModel):
    pattern_type: str = "NONE"
    interval: int = 1
    end_date: Optional[datetime] = None
    days_of_week: List[int] = []
