from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid
import logging
from ..db import db

logger = logging.getLogger("mediconnect")


class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id: str
    appointment_id: str
    notification_type: str
    status: str = "SENT"
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


async def send_notification_email(user_id: str, appointment_id: str, notification_type: str, message: str):
    notification = NotificationLog(
        user_id=user_id,
        appointment_id=appointment_id,
        notification_type=notification_type,
        status="SENT",
        message=message
    )
    doc = notification.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.notification_logs.insert_one(doc)
    logger.info(f"[MOCK EMAIL] {notification_type} sent to user {user_id}: {message}")
    return notification
