from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class Organization(BaseModel):
    """
    Organization represents a company/medical group identified by CUI.
    Multiple locations belong to one organization.
    """
    model_config = ConfigDict(extra="ignore")
    organization_id: str = Field(default_factory=lambda: f"org_{uuid.uuid4().hex[:12]}")
    cui: str  # Fiscal Code - unique identifier
    name: Optional[str] = None
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    tax_registration: Optional[str] = None
    legal_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Super admins who can manage the entire organization
    super_admin_ids: List[str] = Field(default_factory=list)
    
    # Organization-level settings
    settings: dict = Field(default_factory=lambda: {
        "allow_multi_location_booking": True,
        "centralized_billing": False,
        "shared_patient_records": True
    })
    
    is_active: bool = True
    is_verified: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class OrganizationCreate(BaseModel):
    """Data needed to create a new organization during registration"""
    cui: str
    name: Optional[str] = None
    legal_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Fields that can be updated by Super Admin"""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    tax_registration: Optional[str] = None
    legal_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict] = None


class OrganizationRegistration(BaseModel):
    """Complete registration data for new organization + first location + super admin"""
    # Organization data
    cui: str
    organization_name: Optional[str] = None
    
    # First location data
    location_name: str
    location_address: Optional[str] = None
    location_city: Optional[str] = None
    location_county: Optional[str] = None
    location_phone: Optional[str] = None
    
    # Super Admin data
    admin_name: str
    admin_email: str
    admin_password: str
    admin_phone: Optional[str] = None
