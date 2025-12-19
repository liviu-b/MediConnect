from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Permission(BaseModel):
    """
    Defines a specific permission/action in the system.
    Permissions are granular actions like 'appointments:view', 'appointments:accept', etc.
    """
    model_config = ConfigDict(extra="ignore")
    
    permission_id: str = Field(default_factory=lambda: f"perm_{uuid.uuid4().hex[:12]}")
    name: str  # e.g., "appointments:view", "appointments:accept"
    resource: str  # e.g., "appointments", "users", "settings"
    action: str  # e.g., "view", "create", "update", "delete", "accept", "reject"
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RolePermission(BaseModel):
    """
    Maps roles to their allowed permissions.
    This defines what each role can do in the system.
    """
    model_config = ConfigDict(extra="ignore")
    
    role_permission_id: str = Field(default_factory=lambda: f"rperm_{uuid.uuid4().hex[:12]}")
    role: str  # SUPER_ADMIN, LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT, USER
    permission_name: str  # Reference to Permission.name
    
    # Scope constraints
    scope: str = "location"  # "global", "organization", "location", "self"
    
    # Additional constraints
    constraints: Optional[Dict] = Field(default_factory=dict)
    # Example constraints:
    # {"own_location_only": True}
    # {"own_appointments_only": True}
    # {"view_only": True}
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPermissionOverride(BaseModel):
    """
    Allows specific permission overrides for individual users.
    Use sparingly - most permissions should come from roles.
    """
    model_config = ConfigDict(extra="ignore")
    
    override_id: str = Field(default_factory=lambda: f"ovr_{uuid.uuid4().hex[:12]}")
    user_id: str
    permission_name: str
    granted: bool = True  # True = grant permission, False = revoke permission
    reason: Optional[str] = None
    granted_by: Optional[str] = None  # user_id of admin who granted this
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PermissionCheck(BaseModel):
    """
    Request model for checking if a user has a specific permission.
    """
    user_id: str
    permission_name: str
    resource_id: Optional[str] = None  # e.g., appointment_id, location_id
    context: Optional[Dict] = Field(default_factory=dict)


class PermissionCheckResult(BaseModel):
    """
    Result of a permission check.
    """
    allowed: bool
    reason: Optional[str] = None
    scope: Optional[str] = None
    constraints: Optional[Dict] = None


# Predefined permission constants
class PermissionConstants:
    """
    Centralized permission definitions.
    Format: "resource:action"
    """
    
    # Appointment Permissions
    APPOINTMENTS_VIEW = "appointments:view"
    APPOINTMENTS_CREATE = "appointments:create"
    APPOINTMENTS_UPDATE = "appointments:update"
    APPOINTMENTS_DELETE = "appointments:delete"
    APPOINTMENTS_ACCEPT = "appointments:accept"
    APPOINTMENTS_REJECT = "appointments:reject"
    APPOINTMENTS_CANCEL = "appointments:cancel"
    APPOINTMENTS_RESCHEDULE = "appointments:reschedule"
    
    # User Management Permissions
    USERS_VIEW = "users:view"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_INVITE = "users:invite"
    USERS_MANAGE_ROLES = "users:manage_roles"
    
    # Location Permissions
    LOCATIONS_VIEW = "locations:view"
    LOCATIONS_CREATE = "locations:create"
    LOCATIONS_UPDATE = "locations:update"
    LOCATIONS_DELETE = "locations:delete"
    LOCATIONS_MANAGE = "locations:manage"
    
    # Organization Permissions
    ORGANIZATION_VIEW = "organization:view"
    ORGANIZATION_UPDATE = "organization:update"
    ORGANIZATION_SETTINGS = "organization:settings"
    ORGANIZATION_BILLING = "organization:billing"
    
    # Staff Permissions
    STAFF_VIEW = "staff:view"
    STAFF_CREATE = "staff:create"
    STAFF_UPDATE = "staff:update"
    STAFF_DELETE = "staff:delete"
    STAFF_INVITE = "staff:invite"
    
    # Doctor Permissions
    DOCTORS_VIEW = "doctors:view"
    DOCTORS_CREATE = "doctors:create"
    DOCTORS_UPDATE = "doctors:update"
    DOCTORS_DELETE = "doctors:delete"
    
    # Patient/Medical Records Permissions
    RECORDS_VIEW = "records:view"
    RECORDS_CREATE = "records:create"
    RECORDS_UPDATE = "records:update"
    RECORDS_DELETE = "records:delete"
    
    # Service Permissions
    SERVICES_VIEW = "services:view"
    SERVICES_CREATE = "services:create"
    SERVICES_UPDATE = "services:update"
    SERVICES_DELETE = "services:delete"
    
    # Settings Permissions
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"
    
    # Access Request Permissions
    ACCESS_REQUESTS_VIEW = "access_requests:view"
    ACCESS_REQUESTS_APPROVE = "access_requests:approve"
    ACCESS_REQUESTS_REJECT = "access_requests:reject"


# Role-based permission matrix
ROLE_PERMISSIONS_MATRIX = {
    "SUPER_ADMIN": {
        # Full organization access
        PermissionConstants.ORGANIZATION_VIEW: {"scope": "organization"},
        PermissionConstants.ORGANIZATION_UPDATE: {"scope": "organization"},
        PermissionConstants.ORGANIZATION_SETTINGS: {"scope": "organization"},
        PermissionConstants.ORGANIZATION_BILLING: {"scope": "organization"},
        
        # Location management
        PermissionConstants.LOCATIONS_VIEW: {"scope": "organization"},
        PermissionConstants.LOCATIONS_CREATE: {"scope": "organization"},
        PermissionConstants.LOCATIONS_UPDATE: {"scope": "organization"},
        PermissionConstants.LOCATIONS_DELETE: {"scope": "organization"},
        PermissionConstants.LOCATIONS_MANAGE: {"scope": "organization"},
        
        # User management (organization-wide)
        PermissionConstants.USERS_VIEW: {"scope": "organization"},
        PermissionConstants.USERS_INVITE: {"scope": "organization"},
        PermissionConstants.USERS_MANAGE_ROLES: {"scope": "organization"},
        
        # Appointments - VIEW ONLY (CRITICAL CONSTRAINT)
        PermissionConstants.APPOINTMENTS_VIEW: {
            "scope": "organization",
            "view_only": True,
            "cannot_modify": True
        },
        
        # Access requests
        PermissionConstants.ACCESS_REQUESTS_VIEW: {"scope": "organization"},
        PermissionConstants.ACCESS_REQUESTS_APPROVE: {"scope": "organization"},
        PermissionConstants.ACCESS_REQUESTS_REJECT: {"scope": "organization"},
        
        # Staff management
        PermissionConstants.STAFF_VIEW: {"scope": "organization"},
        PermissionConstants.STAFF_INVITE: {"scope": "organization"},
        
        # Doctors
        PermissionConstants.DOCTORS_VIEW: {"scope": "organization"},
        
        # Services
        PermissionConstants.SERVICES_VIEW: {"scope": "organization"},
        
        # Settings
        PermissionConstants.SETTINGS_VIEW: {"scope": "organization"},
        PermissionConstants.SETTINGS_UPDATE: {"scope": "organization"},
    },
    
    "LOCATION_ADMIN": {
        # Location-specific access only
        PermissionConstants.LOCATIONS_VIEW: {"scope": "location", "own_location_only": True},
        PermissionConstants.LOCATIONS_UPDATE: {"scope": "location", "own_location_only": True},
        
        # User management (location-scoped)
        PermissionConstants.USERS_VIEW: {"scope": "location"},
        PermissionConstants.USERS_INVITE: {"scope": "location"},
        
        # Appointments - VIEW ONLY (CRITICAL CONSTRAINT)
        PermissionConstants.APPOINTMENTS_VIEW: {
            "scope": "location",
            "view_only": True,
            "cannot_modify": True,
            "own_location_only": True
        },
        
        # Staff management (location-scoped)
        PermissionConstants.STAFF_VIEW: {"scope": "location"},
        PermissionConstants.STAFF_CREATE: {"scope": "location"},
        PermissionConstants.STAFF_UPDATE: {"scope": "location"},
        PermissionConstants.STAFF_DELETE: {"scope": "location"},
        PermissionConstants.STAFF_INVITE: {"scope": "location"},
        
        # Doctors (location-scoped)
        PermissionConstants.DOCTORS_VIEW: {"scope": "location"},
        PermissionConstants.DOCTORS_CREATE: {"scope": "location"},
        PermissionConstants.DOCTORS_UPDATE: {"scope": "location"},
        
        # Services (location-scoped)
        PermissionConstants.SERVICES_VIEW: {"scope": "location"},
        PermissionConstants.SERVICES_CREATE: {"scope": "location"},
        PermissionConstants.SERVICES_UPDATE: {"scope": "location"},
        
        # Settings (location-scoped)
        PermissionConstants.SETTINGS_VIEW: {"scope": "location"},
        PermissionConstants.SETTINGS_UPDATE: {"scope": "location"},
    },
    
    "RECEPTIONIST": {
        # Appointments - FULL OPERATIONAL ACCESS
        PermissionConstants.APPOINTMENTS_VIEW: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_CREATE: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_UPDATE: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_ACCEPT: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_REJECT: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_CANCEL: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_RESCHEDULE: {"scope": "location"},
        
        # Patients/Users
        PermissionConstants.USERS_VIEW: {"scope": "location"},
        
        # Doctors
        PermissionConstants.DOCTORS_VIEW: {"scope": "location"},
        
        # Services
        PermissionConstants.SERVICES_VIEW: {"scope": "location"},
        
        # Staff
        PermissionConstants.STAFF_VIEW: {"scope": "location"},
    },
    
    "DOCTOR": {
        # Appointments - Own appointments only
        PermissionConstants.APPOINTMENTS_VIEW: {
            "scope": "location",
            "own_appointments_only": True
        },
        PermissionConstants.APPOINTMENTS_UPDATE: {
            "scope": "location",
            "own_appointments_only": True
        },
        PermissionConstants.APPOINTMENTS_ACCEPT: {
            "scope": "location",
            "own_appointments_only": True
        },
        PermissionConstants.APPOINTMENTS_REJECT: {
            "scope": "location",
            "own_appointments_only": True
        },
        PermissionConstants.APPOINTMENTS_CANCEL: {
            "scope": "location",
            "own_appointments_only": True
        },
        
        # Medical records - Full access for own patients
        PermissionConstants.RECORDS_VIEW: {"scope": "location"},
        PermissionConstants.RECORDS_CREATE: {"scope": "location"},
        PermissionConstants.RECORDS_UPDATE: {"scope": "location"},
        
        # Services
        PermissionConstants.SERVICES_VIEW: {"scope": "location"},
        
        # Staff
        PermissionConstants.STAFF_VIEW: {"scope": "location"},
    },
    
    "ASSISTANT": {
        # Appointments - View and assist
        PermissionConstants.APPOINTMENTS_VIEW: {"scope": "location"},
        PermissionConstants.APPOINTMENTS_UPDATE: {"scope": "location", "limited": True},
        
        # Medical records - View only
        PermissionConstants.RECORDS_VIEW: {"scope": "location"},
        
        # Doctors
        PermissionConstants.DOCTORS_VIEW: {"scope": "location"},
        
        # Services
        PermissionConstants.SERVICES_VIEW: {"scope": "location"},
    },
    
    "USER": {
        # Patients - Own data only
        PermissionConstants.APPOINTMENTS_VIEW: {"scope": "self"},
        PermissionConstants.APPOINTMENTS_CREATE: {"scope": "self"},
        PermissionConstants.APPOINTMENTS_CANCEL: {"scope": "self"},
        
        PermissionConstants.RECORDS_VIEW: {"scope": "self"},
        
        # Public views
        PermissionConstants.DOCTORS_VIEW: {"scope": "public"},
        PermissionConstants.SERVICES_VIEW: {"scope": "public"},
        PermissionConstants.LOCATIONS_VIEW: {"scope": "public"},
    }
}
