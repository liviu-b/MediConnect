from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Invitation(BaseModel):
    """
    Unified invitation model for Location Admins and Staff.
    Replaces the old staff invitation system with a more flexible approach.
    """
    model_config = ConfigDict(extra="ignore")
    
    invitation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    
    # Organization and Location context
    organization_id: str
    location_ids: List[str] = Field(default_factory=list)  # Locations this user will have access to
    
    # Invitee information
    email: str
    name: str
    phone: Optional[str] = None
    
    # Role assignment
    role: str  # LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
    
    # Invitation details
    invitation_token: str
    invited_by: str  # user_id of the person who sent the invitation
    invited_by_name: Optional[str] = None
    
    # Status tracking
    status: str = "PENDING"  # PENDING, ACCEPTED, EXPIRED, CANCELLED
    
    # Expiration
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    # Acceptance tracking
    accepted_at: Optional[datetime] = None
    user_id: Optional[str] = None  # Set when invitation is accepted
    
    # Password hash (stored temporarily until accepted)
    # This will be set when user accepts invitation and creates password
    password_hash: Optional[str] = None
    
    # Metadata
    metadata: Optional[dict] = Field(default_factory=dict)
    # Can store additional info like:
    # {"department": "Cardiology", "specialization": "Cardiologist"}
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class InvitationCreate(BaseModel):
    """
    Data needed to create a new invitation.
    """
    email: str
    name: str
    phone: Optional[str] = None
    role: str  # LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
    location_ids: List[str] = Field(default_factory=list)
    metadata: Optional[dict] = None


class InvitationAccept(BaseModel):
    """
    Data needed to accept an invitation.
    """
    token: str
    password: str  # User sets their password when accepting


class InvitationResend(BaseModel):
    """
    Request to resend an invitation.
    """
    invitation_id: str


class InvitationCancel(BaseModel):
    """
    Request to cancel an invitation.
    """
    invitation_id: str
    reason: Optional[str] = None


class InvitationDetails(BaseModel):
    """
    Public details shown to invitee when they click the invitation link.
    """
    name: str
    email: str
    role: str
    organization_name: str
    location_names: List[str]
    invited_by_name: str
    expires_at: datetime


class InvitationQuery(BaseModel):
    """
    Query parameters for listing invitations.
    """
    organization_id: Optional[str] = None
    location_id: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    invited_by: Optional[str] = None
    limit: int = 100
    skip: int = 0


# Role validation
INVITABLE_ROLES = [
    "LOCATION_ADMIN",
    "RECEPTIONIST", 
    "DOCTOR",
    "ASSISTANT"
]


def validate_invitation_role(role: str, inviter_role: str) -> bool:
    """
    Validate if the inviter can invite someone with the specified role.
    
    Rules:
    - SUPER_ADMIN can invite: LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
    - LOCATION_ADMIN can invite: RECEPTIONIST, DOCTOR, ASSISTANT (NOT other LOCATION_ADMINs)
    """
    if inviter_role == "SUPER_ADMIN":
        return role in INVITABLE_ROLES
    elif inviter_role == "LOCATION_ADMIN":
        return role in ["RECEPTIONIST", "DOCTOR", "ASSISTANT"]
    else:
        return False


def get_user_role_from_invitation_role(invitation_role: str) -> str:
    """
    Map invitation role to user role in the system.
    
    This ensures consistency between invitation roles and user roles.
    """
    role_mapping = {
        "LOCATION_ADMIN": "LOCATION_ADMIN",
        "RECEPTIONIST": "RECEPTIONIST",
        "DOCTOR": "DOCTOR",
        "ASSISTANT": "ASSISTANT"
    }
    return role_mapping.get(invitation_role, "ASSISTANT")
