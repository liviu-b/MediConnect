from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class AuditLog(BaseModel):
    """
    Tracks all important actions in the system for security and compliance.
    Especially important for tracking admin actions on appointments (view-only enforcement).
    """
    model_config = ConfigDict(extra="ignore")
    
    log_id: str = Field(default_factory=lambda: f"log_{uuid.uuid4().hex[:12]}")
    
    # Who performed the action
    user_id: str
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    
    # What action was performed
    action: str  # e.g., "appointments:view", "appointments:accept_attempt", "user:invite"
    resource_type: str  # e.g., "appointment", "user", "location", "organization"
    resource_id: Optional[str] = None  # ID of the affected resource
    
    # Context
    organization_id: Optional[str] = None
    location_id: Optional[str] = None
    
    # Details
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # Metadata examples:
    # {"appointment_date": "2024-01-15", "doctor_id": "doc_123"}
    # {"invited_email": "user@example.com", "role": "RECEPTIONIST"}
    
    # Result
    status: str = "success"  # "success", "failed", "denied"
    error_message: Optional[str] = None
    
    # Request info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Severity level
    severity: str = "info"  # "info", "warning", "error", "critical"


class AuditLogCreate(BaseModel):
    """
    Simplified model for creating audit logs.
    """
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = "success"
    error_message: Optional[str] = None
    severity: str = "info"


class AuditLogQuery(BaseModel):
    """
    Query parameters for searching audit logs.
    """
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    organization_id: Optional[str] = None
    location_id: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    skip: int = 0


# Audit action constants
class AuditActions:
    """
    Predefined audit action types.
    """
    
    # Authentication
    LOGIN_SUCCESS = "auth:login_success"
    LOGIN_FAILED = "auth:login_failed"
    LOGOUT = "auth:logout"
    PASSWORD_RESET = "auth:password_reset"
    
    # Appointments
    APPOINTMENT_VIEW = "appointments:view"
    APPOINTMENT_CREATE = "appointments:create"
    APPOINTMENT_UPDATE = "appointments:update"
    APPOINTMENT_DELETE = "appointments:delete"
    APPOINTMENT_ACCEPT = "appointments:accept"
    APPOINTMENT_REJECT = "appointments:reject"
    APPOINTMENT_CANCEL = "appointments:cancel"
    APPOINTMENT_ACCEPT_DENIED = "appointments:accept_denied"  # Admin tried to accept
    APPOINTMENT_MODIFY_DENIED = "appointments:modify_denied"  # Admin tried to modify
    
    # Users
    USER_CREATE = "users:create"
    USER_UPDATE = "users:update"
    USER_DELETE = "users:delete"
    USER_INVITE = "users:invite"
    USER_ROLE_CHANGE = "users:role_change"
    
    # Locations
    LOCATION_CREATE = "locations:create"
    LOCATION_UPDATE = "locations:update"
    LOCATION_DELETE = "locations:delete"
    
    # Organization
    ORGANIZATION_UPDATE = "organization:update"
    ORGANIZATION_SETTINGS_CHANGE = "organization:settings_change"
    
    # Access Requests
    ACCESS_REQUEST_CREATE = "access_requests:create"
    ACCESS_REQUEST_APPROVE = "access_requests:approve"
    ACCESS_REQUEST_REJECT = "access_requests:reject"
    
    # Staff
    STAFF_INVITE = "staff:invite"
    STAFF_CREATE = "staff:create"
    STAFF_UPDATE = "staff:update"
    STAFF_DELETE = "staff:delete"
    
    # Permission violations
    PERMISSION_DENIED = "permission:denied"
    UNAUTHORIZED_ACCESS_ATTEMPT = "permission:unauthorized_attempt"
