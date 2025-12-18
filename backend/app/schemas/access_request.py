from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class AccessRequest(BaseModel):
    """
    Access Request is created when someone tries to register with an existing CUI.
    Super Admin must approve before the user can access the organization.
    """
    model_config = ConfigDict(extra="ignore")
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    organization_id: str  # Which organization they want to join
    cui: str  # The CUI they tried to register with
    
    # Requester information
    requester_name: str
    requester_email: str
    requester_phone: Optional[str] = None
    
    # Proposed location (optional - they might want to create a new one)
    proposed_location_name: Optional[str] = None
    proposed_location_city: Optional[str] = None
    
    # Request status
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    
    # Review information
    reviewed_by: Optional[str] = None  # user_id of super admin who reviewed
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(hour=23, minute=59, second=59) + timezone.timedelta(days=7))


class AccessRequestCreate(BaseModel):
    """Data submitted when requesting access to existing organization"""
    cui: str
    requester_name: str
    requester_email: str
    requester_phone: Optional[str] = None
    proposed_location_name: Optional[str] = None
    proposed_location_city: Optional[str] = None
    password: str  # Store temporarily, will be hashed when approved


class AccessRequestApprove(BaseModel):
    """Data needed to approve an access request"""
    role: str = "LOCATION_ADMIN"  # SUPER_ADMIN, LOCATION_ADMIN, STAFF
    assigned_location_ids: Optional[list] = None  # Which locations they can access (None = all)
    create_new_location: bool = False  # If true, create the proposed location


class AccessRequestReject(BaseModel):
    """Data needed to reject an access request"""
    rejection_reason: str
