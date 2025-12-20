from datetime import datetime, timezone
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class NotificationType:
    """Notification type constants"""
    # Appointment notifications
    APPOINTMENT_REMINDER_24H = "APPOINTMENT_REMINDER_24H"
    APPOINTMENT_REMINDER_1H = "APPOINTMENT_REMINDER_1H"
    APPOINTMENT_CONFIRMED = "APPOINTMENT_CONFIRMED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    APPOINTMENT_RESCHEDULED = "APPOINTMENT_RESCHEDULED"
    APPOINTMENT_COMPLETED = "APPOINTMENT_COMPLETED"
    
    # Medical records
    PRESCRIPTION_ADDED = "PRESCRIPTION_ADDED"
    MEDICAL_RECORD_ADDED = "MEDICAL_RECORD_ADDED"
    TEST_RESULTS_AVAILABLE = "TEST_RESULTS_AVAILABLE"
    
    # System notifications
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    PASSWORD_RESET = "PASSWORD_RESET"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    
    # Doctor availability
    DOCTOR_AVAILABLE = "DOCTOR_AVAILABLE"
    
    ALL_TYPES = [
        APPOINTMENT_REMINDER_24H,
        APPOINTMENT_REMINDER_1H,
        APPOINTMENT_CONFIRMED,
        APPOINTMENT_CANCELLED,
        APPOINTMENT_RESCHEDULED,
        APPOINTMENT_COMPLETED,
        PRESCRIPTION_ADDED,
        MEDICAL_RECORD_ADDED,
        TEST_RESULTS_AVAILABLE,
        ACCOUNT_CREATED,
        PASSWORD_RESET,
        PROFILE_UPDATED,
        DOCTOR_AVAILABLE
    ]


class NotificationPriority:
    """Notification priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Notification(BaseModel):
    """User notification model"""
    model_config = ConfigDict(extra="ignore")
    
    notification_id: str = Field(default_factory=lambda: f"notif_{__import__('uuid').uuid4().hex[:12]}")
    user_id: str
    
    # Notification content
    type: str  # From NotificationType
    title: str
    message: str
    priority: str = NotificationPriority.MEDIUM
    
    # Related resources
    appointment_id: Optional[str] = None
    prescription_id: Optional[str] = None
    record_id: Optional[str] = None
    doctor_id: Optional[str] = None
    
    # Metadata
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    # Delivery channels
    sent_email: bool = False
    sent_push: bool = False
    sent_sms: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_for: Optional[datetime] = None  # For scheduled notifications
    sent_at: Optional[datetime] = None


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    
    # Email preferences
    email_enabled: bool = True
    email_appointment_reminders: bool = True
    email_appointment_changes: bool = True
    email_medical_records: bool = True
    email_marketing: bool = False
    
    # Push notification preferences
    push_enabled: bool = True
    push_appointment_reminders: bool = True
    push_appointment_changes: bool = True
    push_medical_records: bool = True
    
    # SMS preferences
    sms_enabled: bool = False
    sms_appointment_reminders: bool = False
    sms_urgent_only: bool = True
    
    # Reminder timing preferences
    reminder_24h_before: bool = True
    reminder_1h_before: bool = True
    reminder_custom_hours: Optional[int] = None  # Custom reminder time in hours
    
    # Quiet hours (no notifications during this time)
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = "22:00"  # Format: "HH:MM"
    quiet_hours_end: Optional[str] = "08:00"
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class NotificationCreate(BaseModel):
    """Create notification request"""
    user_id: str
    type: str
    title: str
    message: str
    priority: Optional[str] = NotificationPriority.MEDIUM
    appointment_id: Optional[str] = None
    prescription_id: Optional[str] = None
    record_id: Optional[str] = None
    doctor_id: Optional[str] = None
    metadata: Optional[Dict] = None
    scheduled_for: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    """Update notification"""
    is_read: Optional[bool] = None


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""
    email_enabled: Optional[bool] = None
    email_appointment_reminders: Optional[bool] = None
    email_appointment_changes: Optional[bool] = None
    email_medical_records: Optional[bool] = None
    email_marketing: Optional[bool] = None
    
    push_enabled: Optional[bool] = None
    push_appointment_reminders: Optional[bool] = None
    push_appointment_changes: Optional[bool] = None
    push_medical_records: Optional[bool] = None
    
    sms_enabled: Optional[bool] = None
    sms_appointment_reminders: Optional[bool] = None
    sms_urgent_only: Optional[bool] = None
    
    reminder_24h_before: Optional[bool] = None
    reminder_1h_before: Optional[bool] = None
    reminder_custom_hours: Optional[int] = None
    
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationStats(BaseModel):
    """Notification statistics"""
    total_notifications: int = 0
    unread_count: int = 0
    read_count: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)
