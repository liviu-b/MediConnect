from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    picture: Optional[str] = None
    password_hash: Optional[str] = None
    auth_provider: str = "email"
    
    # Role-based access control
    role: str = "USER"  # USER, SUPER_ADMIN, LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
    
    # Multi-location support
    organization_id: Optional[str] = None  # Which organization they belong to
    clinic_id: Optional[str] = None  # DEPRECATED: kept for backward compatibility
    
    # Location access control
    # None = access all locations in organization (for SUPER_ADMIN)
    # List = specific locations (for LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT)
    assigned_location_ids: Optional[List[str]] = None
    
    # Permission caching (updated when role changes or permissions are modified)
    # This improves performance by avoiding repeated permission lookups
    cached_permissions: Optional[List[str]] = Field(default_factory=list)
    permissions_updated_at: Optional[datetime] = None
    
    # Additional metadata
    metadata: Optional[Dict] = Field(default_factory=dict)
    # Can store: {"department": "Cardiology", "employee_id": "EMP001", etc.}
    
    # Status flags
    is_active: bool = True
    is_email_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    metadata: Optional[Dict] = None


class UserRoleUpdate(BaseModel):
    """
    Update user role and location assignments.
    Only accessible by SUPER_ADMIN or LOCATION_ADMIN.
    """
    role: Optional[str] = None
    assigned_location_ids: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class PasswordResetToken(BaseModel):
    model_config = ConfigDict(extra="ignore")
    token: str
    user_id: str
    email: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Role constants for validation
class UserRole:
    """
    Centralized role definitions.
    """
    USER = "USER"  # Regular patient
    SUPER_ADMIN = "SUPER_ADMIN"  # Organization owner
    LOCATION_ADMIN = "LOCATION_ADMIN"  # Branch manager
    RECEPTIONIST = "RECEPTIONIST"  # Front desk staff
    DOCTOR = "DOCTOR"  # Medical doctor
    ASSISTANT = "ASSISTANT"  # Medical assistant/nurse
    
    # All valid roles
    ALL_ROLES = [USER, SUPER_ADMIN, LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT]
    
    # Staff roles (work at medical centers)
    STAFF_ROLES = [SUPER_ADMIN, LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT]
    
    # Admin roles (can manage users)
    ADMIN_ROLES = [SUPER_ADMIN, LOCATION_ADMIN]
    
    # Operational roles (can handle appointments)
    OPERATIONAL_ROLES = [RECEPTIONIST, DOCTOR, ASSISTANT]


def is_valid_role(role: str) -> bool:
    """Check if a role is valid."""
    return role in UserRole.ALL_ROLES


def is_staff_role(role: str) -> bool:
    """Check if a role is a staff role."""
    return role in UserRole.STAFF_ROLES


def is_admin_role(role: str) -> bool:
    """Check if a role is an admin role."""
    return role in UserRole.ADMIN_ROLES


def is_operational_role(role: str) -> bool:
    """Check if a role can perform operational tasks."""
    return role in UserRole.OPERATIONAL_ROLES
