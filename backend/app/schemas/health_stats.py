from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class VitalSign(BaseModel):
    """Single vital sign measurement"""
    model_config = ConfigDict(extra="ignore")
    
    measurement_id: str = Field(default_factory=lambda: f"vital_{__import__('uuid').uuid4().hex[:12]}")
    user_id: str  # Patient ID
    
    # Vital sign type
    type: str  # blood_pressure, heart_rate, temperature, weight, height, blood_sugar, oxygen_saturation
    
    # Values
    value: float  # Main value
    value_secondary: Optional[float] = None  # For blood pressure (diastolic)
    unit: str  # mmHg, bpm, °C, kg, cm, mg/dL, %
    
    # Context
    notes: Optional[str] = None
    measured_by: Optional[str] = None  # doctor_id or "self"
    measured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VitalSignCreate(BaseModel):
    """Create vital sign request"""
    type: str
    value: float
    value_secondary: Optional[float] = None
    unit: str
    notes: Optional[str] = None
    measured_at: Optional[datetime] = None


class LabResult(BaseModel):
    """Laboratory test result"""
    model_config = ConfigDict(extra="ignore")
    
    result_id: str = Field(default_factory=lambda: f"lab_{__import__('uuid').uuid4().hex[:12]}")
    user_id: str  # Patient ID
    
    # Test information
    test_name: str
    test_category: str  # blood_test, urine_test, imaging, biopsy, etc.
    
    # Results
    result_value: Optional[str] = None  # Numeric or text result
    result_unit: Optional[str] = None
    reference_range: Optional[str] = None  # Normal range
    status: str = "PENDING"  # PENDING, COMPLETED, ABNORMAL
    
    # Files
    file_url: Optional[str] = None  # PDF or image URL
    file_type: Optional[str] = None  # pdf, jpg, png
    
    # Context
    notes: Optional[str] = None
    interpretation: Optional[str] = None  # Doctor's interpretation
    
    # Metadata
    ordered_by: Optional[str] = None  # doctor_id
    ordered_by_name: Optional[str] = None
    lab_name: Optional[str] = None
    test_date: datetime
    result_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LabResultCreate(BaseModel):
    """Create lab result request"""
    test_name: str
    test_category: str
    result_value: Optional[str] = None
    result_unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: str = "PENDING"
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    notes: Optional[str] = None
    interpretation: Optional[str] = None
    lab_name: Optional[str] = None
    test_date: datetime
    result_date: Optional[datetime] = None


class LabResultUpdate(BaseModel):
    """Update lab result"""
    result_value: Optional[str] = None
    result_unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    notes: Optional[str] = None
    interpretation: Optional[str] = None
    result_date: Optional[datetime] = None


class HealthStats(BaseModel):
    """Patient health statistics summary"""
    user_id: str
    
    # Latest vitals
    latest_blood_pressure: Optional[dict] = None
    latest_heart_rate: Optional[dict] = None
    latest_temperature: Optional[dict] = None
    latest_weight: Optional[dict] = None
    latest_height: Optional[dict] = None
    latest_bmi: Optional[float] = None
    
    # Counts
    total_vital_measurements: int = 0
    total_lab_results: int = 0
    pending_lab_results: int = 0
    abnormal_lab_results: int = 0
    
    # Recent activity
    last_measurement_date: Optional[datetime] = None
    last_lab_test_date: Optional[datetime] = None
