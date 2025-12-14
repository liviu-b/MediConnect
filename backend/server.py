from fastapi import FastAPI, APIRouter, HTTPException, Response, Request, Depends, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from passlib.context import CryptContext
import secrets
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with optimized settings for Atlas
mongo_url = os.environ.get('MONGO_URL', '')
if not mongo_url:
    raise ValueError("MONGO_URL environment variable is required")

client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    maxPoolSize=50,
    minPoolSize=5,
    maxIdleTimeMS=45000,
    retryWrites=True,
    retryReads=True
)
db = client[os.environ.get('DB_NAME', 'mediconnect_db')]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Resend email configuration
resend.api_key = os.environ.get('RESEND_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@mediconnect.com')

# Create the main app without a prefix
app = FastAPI(title="MediConnect API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

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
    role: str = "USER"
    clinic_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class ClinicRegistration(BaseModel):
    cui: str
    admin_name: str
    admin_email: str
    admin_password: str

class Clinic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clinic_id: str = Field(default_factory=lambda: f"clinic_{uuid.uuid4().hex[:12]}")
    cui: str
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = True
    is_profile_complete: bool = False
    working_hours: dict = Field(default_factory=lambda: {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": None
    })
    settings: dict = Field(default_factory=lambda: {
        "allow_online_booking": True,
        "booking_advance_days": 30,
        "cancellation_hours": 24,
        "reminder_hours": 24
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    working_hours: Optional[dict] = None
    settings: Optional[dict] = None

class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    doctor_id: str = Field(default_factory=lambda: f"doctor_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: int = 30
    consultation_fee: float = 0.0
    is_active: bool = True
    availability_schedule: dict = Field(default_factory=lambda: {
        "monday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "tuesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "wednesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "thursday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "friday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
        "saturday": [{"start": "10:00", "end": "14:00"}],
        "sunday": []
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DoctorCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    specialty: str
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: int = 30
    consultation_fee: float = 0.0
    availability_schedule: Optional[dict] = None

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    picture: Optional[str] = None
    consultation_duration: Optional[int] = None
    consultation_fee: Optional[float] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[dict] = None

class RecurrencePattern(BaseModel):
    pattern_type: str = "NONE"
    interval: int = 1
    end_date: Optional[datetime] = None
    days_of_week: List[int] = []

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    appointment_id: str = Field(default_factory=lambda: f"apt_{uuid.uuid4().hex[:12]}")
    patient_id: str
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    doctor_id: str
    clinic_id: str
    date_time: datetime
    duration: int = 30
    status: str = "SCHEDULED"
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    recurrence: Optional[RecurrencePattern] = None
    parent_appointment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppointmentCreate(BaseModel):
    doctor_id: str
    clinic_id: str
    date_time: datetime
    duration: int = 30
    notes: Optional[str] = None
    recurrence: Optional[RecurrencePattern] = None

class AppointmentUpdate(BaseModel):
    date_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCancel(BaseModel):
    reason: str  # Required cancellation reason

class Prescription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    prescription_id: str = Field(default_factory=lambda: f"presc_{uuid.uuid4().hex[:12]}")
    appointment_id: str
    patient_id: str
    doctor_id: str
    clinic_id: str
    medications: List[dict] = []  # [{name, dosage, frequency, duration}]
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PrescriptionCreate(BaseModel):
    appointment_id: str
    medications: List[dict] = []
    notes: Optional[str] = None

class MedicalRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    appointment_id: str
    patient_id: str
    doctor_id: str
    clinic_id: str
    record_type: str = "RECOMMENDATION"  # RECOMMENDATION, LETTER, NOTE
    title: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MedicalRecordCreate(BaseModel):
    appointment_id: str
    record_type: str = "RECOMMENDATION"
    title: str
    content: str

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PasswordResetToken(BaseModel):
    model_config = ConfigDict(extra="ignore")
    token: str = Field(default_factory=lambda: f"reset_{secrets.token_hex(32)}")
    user_id: str
    email: str
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id: str
    appointment_id: str
    notification_type: str
    status: str = "SENT"
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StaffMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    staff_id: str = Field(default_factory=lambda: f"staff_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"  # RECEPTIONIST, NURSE, ADMIN, DOCTOR, ASSISTANT
    is_active: bool = True
    invitation_status: str = "PENDING"  # PENDING, ACCEPTED
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    user_id: Optional[str] = None  # Link to User account once invitation is accepted
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StaffCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class StaffInvitation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    invitation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    staff_id: str
    clinic_id: str
    email: str
    name: str
    role: str
    token: str = Field(default_factory=lambda: f"invite_{secrets.token_hex(32)}")
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AcceptInvitationRequest(BaseModel):
    token: str
    password: str

class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewCreate(BaseModel):
    clinic_id: str
    rating: int  # 1-5 stars
    comment: Optional[str] = None

class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"  # LEI or EURO
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    currency: str = "LEI"  # LEI or EURO

class RegistrationCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str
    is_used: bool = False
    used_by_clinic_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(request: Request) -> Optional[User]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        return None
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    
    return User(**user_doc)

async def require_auth(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def require_clinic_admin(request: Request) -> User:
    user = await require_auth(request)
    if user.role != "CLINIC_ADMIN":
        raise HTTPException(status_code=403, detail="Clinic admin access required")
    return user

async def require_staff_or_admin(request: Request) -> User:
    """Require user to be staff (Doctor/Assistant) or admin of a clinic"""
    user = await require_auth(request)
    if user.role not in ["CLINIC_ADMIN", "DOCTOR", "ASSISTANT"]:
        raise HTTPException(status_code=403, detail="Staff or admin access required")
    return user

async def create_session(user_id: str, response: Response) -> str:
    session_token = f"session_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.delete_many({"user_id": user_id})
    
    session = UserSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    session_doc = session.model_dump()
    session_doc['expires_at'] = session_doc['expires_at'].isoformat()
    session_doc['created_at'] = session_doc['created_at'].isoformat()
    await db.user_sessions.insert_one(session_doc)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return session_token

# ==================== MOCK EMAIL SERVICE ====================

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

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register_user(data: UserRegister, response: Response):
    """Register a new user with email/password"""
    try:
        if len(data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        existing = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user = User(
            user_id=user_id,
            email=data.email.lower(),
            name=data.name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            auth_provider="email",
            role="USER"
        )
        doc = user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        
        session_token = await create_session(user_id, response)
        
        user_data = {k: v for k, v in doc.items() if k != 'password_hash' and k != '_id'}
        return {"user": user_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@api_router.post("/auth/login")
async def login_user(data: UserLogin, response: Response):
    """Login with email/password - supports Admin, Doctor, and Assistant roles"""
    try:
        user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user_doc.get('password_hash'):
            raise HTTPException(status_code=401, detail="Please use Google login for this account")
        
        if not verify_password(data.password, user_doc['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active
        if not user_doc.get('is_active', True):
            raise HTTPException(status_code=401, detail="Account is disabled")
        
        session_token = await create_session(user_doc['user_id'], response)
        
        user_data = {k: v for k, v in user_doc.items() if k != 'password_hash'}
        
        # Determine redirect target based on role
        role = user_doc.get('role', 'USER')
        if role == 'CLINIC_ADMIN':
            user_data['redirect_to'] = '/dashboard'
        elif role in ['DOCTOR', 'ASSISTANT']:
            user_data['redirect_to'] = '/staff-dashboard'
        else:
            user_data['redirect_to'] = '/dashboard'
        
        return {"user": user_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")

@api_router.post("/auth/register-clinic")
async def register_clinic(data: ClinicRegistration, response: Response):
    """Register a new clinic with Romanian CUI"""
    import re
    
    try:
        cui_clean = data.cui.strip()
        if not re.match(r'^\d{2,10}$', cui_clean):
            raise HTTPException(
                status_code=400, 
                detail="CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
            )
        
        if len(data.admin_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Parola trebuie sa aiba minim 8 caractere."
            )
        
        existing_clinic = await db.clinics.find_one({"cui": cui_clean}, {"_id": 0})
        if existing_clinic:
            raise HTTPException(
                status_code=400, 
                detail="Acest CUI este deja inregistrat."
            )
        
        existing_user = await db.users.find_one({"email": data.admin_email.lower()}, {"_id": 0})
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="Aceasta adresa de email este deja inregistrata."
            )
        
        clinic_id = f"clinic_{uuid.uuid4().hex[:12]}"
        clinic = Clinic(
            clinic_id=clinic_id,
            cui=cui_clean,
            is_verified=True,
            is_profile_complete=False
        )
        clinic_doc = clinic.model_dump()
        clinic_doc['created_at'] = clinic_doc['created_at'].isoformat()
        await db.clinics.insert_one(clinic_doc)
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        admin_user = User(
            user_id=user_id,
            email=data.admin_email.lower(),
            name=data.admin_name,
            password_hash=hash_password(data.admin_password),
            auth_provider="email",
            role="CLINIC_ADMIN",
            clinic_id=clinic_id
        )
        user_doc = admin_user.model_dump()
        user_doc['created_at'] = user_doc['created_at'].isoformat()
        await db.users.insert_one(user_doc)
        
        session_token = await create_session(user_id, response)
        
        user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
        clinic_data = {k: v for k, v in clinic_doc.items() if k != '_id'}
        return {"user": user_data, "clinic": clinic_data, "session_token": session_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clinic registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@api_router.post("/auth/session")
async def create_oauth_session(request: Request, response: Response):
    """Exchange session_id for session_token after Google OAuth"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")
    
    async with httpx.AsyncClient() as client_http:
        try:
            auth_response = await client_http.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session ID")
            
            user_data = auth_response.json()
        except Exception as e:
            logger.error(f"Auth service error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")
    
    existing_user = await db.users.find_one({"email": user_data["email"].lower()}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": user_data["name"],
                "picture": user_data.get("picture")
            }}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = User(
            user_id=user_id,
            email=user_data["email"].lower(),
            name=user_data["name"],
            picture=user_data.get("picture"),
            auth_provider="google",
            role="USER"
        )
        doc = new_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    
    session_token = await create_session(user_id, response)
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    user_data_clean = {k: v for k, v in user_doc.items() if k != 'password_hash'}
    
    return {"user": user_data_clean, "session_token": session_token}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_dict = user.model_dump()
    user_dict.pop('password_hash', None)
    
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        user_dict['clinic'] = clinic
    
    return user_dict

@api_router.put("/auth/profile")
async def update_profile(data: UserUpdate, request: Request):
    """Update user profile settings"""
    user = await require_auth(request)
    
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.address is not None:
        update_data["address"] = data.address
    if data.date_of_birth is not None:
        update_data["date_of_birth"] = data.date_of_birth
    
    if update_data:
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one({"user_id": user.user_id}, {"_id": 0, "password_hash": 0})
    return updated_user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out successfully"}

@api_router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Request a password reset link"""
    user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    
    if not user_doc:
        logger.info(f"Password reset requested for non-existent email: {data.email}")
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    
    if user_doc.get('auth_provider') == 'google':
        logger.info(f"Password reset requested for Google OAuth user: {data.email}")
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    
    await db.password_reset_tokens.delete_many({"user_id": user_doc['user_id']})
    
    reset_token = PasswordResetToken(
        user_id=user_doc['user_id'],
        email=data.email.lower()
    )
    
    token_doc = reset_token.model_dump()
    token_doc['expires_at'] = token_doc['expires_at'].isoformat()
    token_doc['created_at'] = token_doc['created_at'].isoformat()
    await db.password_reset_tokens.insert_one(token_doc)
    
    medical_center = None
    if user_doc.get('clinic_id'):
        medical_center = await db.clinics.find_one({"clinic_id": user_doc['clinic_id']}, {"_id": 0})
    
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?token={reset_token.token}"
    
    background_tasks.add_task(
        send_password_reset_email,
        recipient_email=data.email.lower(),
        recipient_name=user_doc.get('name', 'User'),
        reset_link=reset_link,
        medical_center=medical_center
    )
    
    logger.info(f"Password reset email queued for: {data.email}")
    return {"message": "If an account exists with this email, a password reset link has been sent."}


def send_password_reset_email(recipient_email: str, recipient_name: str, reset_link: str, medical_center: dict = None):
    """Send password reset email using Resend"""
    try:
        from_email = "MediConnect <onboarding@resend.dev>"
        center_name = medical_center.get('name', 'MediConnect') if medical_center else 'MediConnect'
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">{center_name}</h1>
</div>
<div style="padding: 40px 30px;">
<h2 style="color: #1f2937;">Password Reset Request</h2>
<p style="color: #4b5563;">Hello {recipient_name},</p>
<p style="color: #4b5563;">Click the button below to reset your password.</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{reset_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Reset Your Password</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Or copy this link: {reset_link}</p>
<p style="color: #9ca3af; font-size: 12px;">This link expires in 1 hour.</p>
</div>
</div>
</body>
</html>"""
        
        text_content = f"Password Reset\n\nHello {recipient_name},\n\nReset your password: {reset_link}\n\nThis link expires in 1 hour."
        
        response = resend.Emails.send({
            "from": from_email,
            "to": recipient_email,
            "subject": f"Reset Your Password - {center_name}",
            "html": html_content,
            "text": text_content
        })
        
        logger.info(f"Password reset email sent to {recipient_email}")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return {"success": False, "error": str(e)}

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """Reset password using reset token"""
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    token_doc = await db.password_reset_tokens.find_one({"token": data.token, "used": False}, {"_id": 0})
    
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = token_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    new_password_hash = hash_password(data.new_password)
    await db.users.update_one(
        {"user_id": token_doc["user_id"]},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    await db.password_reset_tokens.update_one(
        {"token": data.token},
        {"$set": {"used": True}}
    )
    
    logger.info(f"Password reset successful for user: {token_doc['user_id']}")
    return {"message": "Password has been reset successfully"}

@api_router.post("/auth/validate-cui")
async def validate_cui(cui: str):
    """Check if a CUI is already registered"""
    import re
    cui_clean = cui.strip()
    
    if not re.match(r'^\d{2,10}$', cui_clean):
        return {"valid": False, "available": False, "message": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."}
    
    existing = await db.clinics.find_one({"cui": cui_clean}, {"_id": 0})
    if existing:
        return {"valid": True, "available": False, "message": "Acest CUI este deja inregistrat."}
    
    return {"valid": True, "available": True, "message": "CUI disponibil pentru inregistrare."}

# ==================== CLINIC MANAGEMENT ROUTES ====================

@api_router.get("/clinics")
async def get_clinics(request: Request):
    user = await get_current_user(request)
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        return [clinic] if clinic else []
    
    clinics = await db.clinics.find({"is_verified": True}, {"_id": 0}).to_list(100)
    return clinics

@api_router.get("/clinics/{clinic_id}")
async def get_clinic(clinic_id: str):
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

@api_router.put("/clinics/{clinic_id}")
async def update_clinic(clinic_id: str, data: ClinicUpdate, request: Request):
    user = await require_clinic_admin(request)
    if user.clinic_id != clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    new_name = update_data.get('name', clinic.get('name'))
    new_address = update_data.get('address', clinic.get('address'))
    if new_name and new_address:
        update_data['is_profile_complete'] = True
    
    await db.clinics.update_one({"clinic_id": clinic_id}, {"$set": update_data})
    return await get_clinic(clinic_id)

# ==================== REVIEW ROUTES ====================

@api_router.get("/clinics/{clinic_id}/reviews")
async def get_clinic_reviews(clinic_id: str):
    """Get all reviews for a clinic"""
    reviews = await db.reviews.find(
        {"clinic_id": clinic_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return reviews

@api_router.post("/clinics/{clinic_id}/reviews")
async def create_review(clinic_id: str, data: ReviewCreate, request: Request):
    """Create a review for a clinic"""
    user = await require_auth(request)
    
    # Verify clinic exists
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    # Validate rating
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if user already reviewed this clinic
    existing_review = await db.reviews.find_one({
        "clinic_id": clinic_id,
        "user_id": user.user_id
    }, {"_id": 0})
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this clinic")
    
    review = Review(
        clinic_id=clinic_id,
        user_id=user.user_id,
        user_name=user.name,
        rating=data.rating,
        comment=data.comment
    )
    
    doc = review.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.reviews.insert_one(doc)
    
    return review

@api_router.get("/clinics/{clinic_id}/stats")
async def get_clinic_stats(clinic_id: str):
    """Get clinic statistics including average rating"""
    # Get average rating
    pipeline = [
        {"$match": {"clinic_id": clinic_id}},
        {"$group": {
            "_id": None,
            "average_rating": {"$avg": "$rating"},
            "review_count": {"$sum": 1}
        }}
    ]
    result = await db.reviews.aggregate(pipeline).to_list(1)
    
    if result:
        return {
            "average_rating": round(result[0]["average_rating"], 1),
            "review_count": result[0]["review_count"]
        }
    
    return {"average_rating": 0, "review_count": 0}

# ==================== DOCTOR MANAGEMENT ROUTES ====================

@api_router.get("/doctors")
async def get_doctors(request: Request, clinic_id: Optional[str] = None):
    user = await get_current_user(request)
    
    query = {"is_active": True}
    
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif clinic_id:
        query["clinic_id"] = clinic_id
    
    doctors = await db.doctors.find(query, {"_id": 0}).to_list(100)
    
    for doc in doctors:
        clinic = await db.clinics.find_one({"clinic_id": doc["clinic_id"]}, {"_id": 0})
        doc["clinic_name"] = clinic.get("name") if clinic else "Unknown"
    
    return doctors

@api_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    clinic = await db.clinics.find_one({"clinic_id": doctor["clinic_id"]}, {"_id": 0})
    doctor["clinic_name"] = clinic.get("name") if clinic else "Unknown"
    
    return doctor

@api_router.post("/doctors")
async def create_doctor(data: DoctorCreate, request: Request):
    user = await require_clinic_admin(request)
    
    doctor = Doctor(
        clinic_id=user.clinic_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        specialty=data.specialty,
        bio=data.bio,
        picture=data.picture,
        consultation_duration=data.consultation_duration,
        consultation_fee=data.consultation_fee,
        availability_schedule=data.availability_schedule or {
            "monday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "tuesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "wednesday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "thursday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "friday": [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}],
            "saturday": [{"start": "10:00", "end": "14:00"}],
            "sunday": []
        }
    )
    doc = doctor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.doctors.insert_one(doc)
    
    return doctor

@api_router.put("/doctors/{doctor_id}")
async def update_doctor(doctor_id: str, data: DoctorUpdate, request: Request):
    user = await require_clinic_admin(request)
    
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if doctor["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if update_data:
        await db.doctors.update_one({"doctor_id": doctor_id}, {"$set": update_data})
    
    return await get_doctor(doctor_id)

@api_router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str, request: Request):
    user = await require_clinic_admin(request)
    
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if doctor["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.doctors.update_one({"doctor_id": doctor_id}, {"$set": {"is_active": False}})
    return {"message": "Doctor deactivated successfully"}

@api_router.get("/doctors/{doctor_id}/availability")
async def get_doctor_availability(doctor_id: str, date: str):
    doctor = await db.doctors.find_one({"doctor_id": doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = day_names[target_date.weekday()]
    
    schedule = doctor.get("availability_schedule", {}).get(day_name, [])
    if not schedule:
        return {"date": date, "available_slots": [], "duration": doctor.get("consultation_duration", 30)}
    
    start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    existing_appointments = await db.appointments.find({
        "doctor_id": doctor_id,
        "date_time": {"$gte": start_of_day.isoformat(), "$lte": end_of_day.isoformat()},
        "status": {"$ne": "CANCELLED"}
    }, {"_id": 0}).to_list(100)
    
    booked_times = set()
    for apt in existing_appointments:
        apt_time = datetime.fromisoformat(apt["date_time"].replace("Z", "+00:00"))
        booked_times.add(apt_time.strftime("%H:%M"))
    
    duration = doctor.get("consultation_duration", 30)
    available_slots = []
    
    for period in schedule:
        start_time = datetime.strptime(period["start"], "%H:%M")
        end_time = datetime.strptime(period["end"], "%H:%M")
        
        current = start_time
        while current < end_time:
            time_str = current.strftime("%H:%M")
            if time_str not in booked_times:
                slot_datetime = datetime.combine(target_date, current.time()).replace(tzinfo=timezone.utc)
                if target_date > datetime.now(timezone.utc).date() or slot_datetime > datetime.now(timezone.utc):
                    available_slots.append({
                        "time": time_str,
                        "datetime": slot_datetime.isoformat()
                    })
            current += timedelta(minutes=duration)
    
    return {"date": date, "available_slots": available_slots, "duration": duration}

@api_router.put("/doctors/{doctor_id}/availability")
async def update_doctor_availability(doctor_id: str, data: dict, request: Request):
    """Allow doctor to update their own availability schedule (within clinic hours)"""
    user = await require_auth(request)
    
    doctor = await db.doctors.find_one({"doctor_id": doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if user is the doctor or clinic admin
    is_own_profile = user.email.lower() == doctor.get('email', '').lower()
    is_admin = user.role == 'CLINIC_ADMIN' and user.clinic_id == doctor['clinic_id']
    
    if not is_own_profile and not is_admin:
        raise HTTPException(status_code=403, detail="You can only update your own availability")
    
    # Get clinic working hours
    clinic = await db.clinics.find_one({"clinic_id": doctor['clinic_id']}, {"_id": 0})
    clinic_hours = clinic.get('working_hours', {}) if clinic else {}
    
    # Validate availability is within clinic hours
    availability_schedule = data.get('availability_schedule', {})
    validated_schedule = {}
    
    for day, periods in availability_schedule.items():
        clinic_day_hours = clinic_hours.get(day)
        
        # If clinic is closed on this day, doctor cannot work
        if clinic_day_hours is None:
            validated_schedule[day] = []
            continue
        
        # Validate each period is within clinic hours
        valid_periods = []
        for period in periods:
            start = period.get('start', '09:00')
            end = period.get('end', '17:00')
            
            # Ensure doctor hours are within clinic hours
            if clinic_day_hours:
                clinic_start = clinic_day_hours.get('start', '00:00')
                clinic_end = clinic_day_hours.get('end', '23:59')
                
                if start < clinic_start:
                    start = clinic_start
                if end > clinic_end:
                    end = clinic_end
            
            if start < end:
                valid_periods.append({'start': start, 'end': end})
        
        validated_schedule[day] = valid_periods
    
    # Update doctor availability
    await db.doctors.update_one(
        {"doctor_id": doctor_id},
        {"$set": {"availability_schedule": validated_schedule}}
    )
    
    updated_doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    return updated_doctor

# ==================== STAFF MANAGEMENT ROUTES ====================

@api_router.get("/staff")
async def get_staff(request: Request):
    user = await require_clinic_admin(request)
    staff = await db.staff.find({"clinic_id": user.clinic_id, "is_active": True}, {"_id": 0}).to_list(100)
    return staff

@api_router.post("/staff")
async def create_staff(data: StaffCreate, request: Request, background_tasks: BackgroundTasks):
    """Create staff member and send invitation email"""
    user = await require_clinic_admin(request)
    
    # Check if email is already used
    existing_user = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered in the system")
    
    existing_staff = await db.staff.find_one({"email": data.email.lower(), "clinic_id": user.clinic_id, "is_active": True}, {"_id": 0})
    if existing_staff:
        raise HTTPException(status_code=400, detail="A staff member with this email already exists")
    
    # Generate invitation token
    invitation_token = f"invite_{secrets.token_hex(32)}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    staff = StaffMember(
        clinic_id=user.clinic_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        role=data.role,
        invitation_status="PENDING",
        invitation_token=invitation_token,
        invitation_expires_at=expires_at
    )
    doc = staff.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['invitation_expires_at'] = doc['invitation_expires_at'].isoformat() if doc['invitation_expires_at'] else None
    await db.staff.insert_one(doc)
    
    # Get clinic info for email
    clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
    
    # Send invitation email
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"
    
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=data.email.lower(),
        recipient_name=data.name,
        role=data.role,
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.name
    )
    
    logger.info(f"Staff invitation sent to {data.email} for clinic {user.clinic_id}")
    
    return staff

@api_router.post("/staff/{staff_id}/resend-invitation")
async def resend_staff_invitation(staff_id: str, request: Request, background_tasks: BackgroundTasks):
    """Resend invitation email to staff member"""
    user = await require_clinic_admin(request)
    
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user.clinic_id}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    
    # Generate new invitation token
    new_token = f"invite_{secrets.token_hex(32)}"
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.staff.update_one(
        {"staff_id": staff_id},
        {"$set": {
            "invitation_token": new_token,
            "invitation_expires_at": new_expires_at.isoformat()
        }}
    )
    
    # Get clinic info
    clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
    
    # Send invitation email
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    invitation_link = f"{frontend_url}/accept-invitation?token={new_token}"
    
    background_tasks.add_task(
        send_staff_invitation_email,
        recipient_email=staff['email'],
        recipient_name=staff['name'],
        role=staff['role'],
        invitation_link=invitation_link,
        clinic_name=clinic.get('name', 'Medical Center') if clinic else 'Medical Center',
        inviter_name=user.name
    )
    
    return {"message": "Invitation resent successfully"}

@api_router.get("/staff/invitation/{token}")
async def get_invitation_details(token: str):
    """Get invitation details by token"""
    staff = await db.staff.find_one({"invitation_token": token}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    
    # Check expiry
    expires_at = staff.get('invitation_expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Invitation has expired")
    
    # Get clinic info
    clinic = await db.clinics.find_one({"clinic_id": staff['clinic_id']}, {"_id": 0})
    
    return {
        "name": staff['name'],
        "email": staff['email'],
        "role": staff['role'],
        "clinic_name": clinic.get('name', 'Medical Center') if clinic else 'Medical Center'
    }

@api_router.post("/staff/accept-invitation")
async def accept_staff_invitation(data: AcceptInvitationRequest, response: Response):
    """Accept invitation and create user account"""
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    staff = await db.staff.find_one({"invitation_token": data.token}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    if staff.get('invitation_status') == 'ACCEPTED':
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    
    # Check expiry
    expires_at = staff.get('invitation_expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Invitation has expired")
    
    # Check if email is already registered as a user
    existing_user = await db.users.find_one({"email": staff['email']}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered")
    
    # Map staff role to user role
    user_role = "ASSISTANT"  # Default
    if staff['role'] == 'DOCTOR':
        user_role = "DOCTOR"
    elif staff['role'] in ['ADMIN', 'RECEPTIONIST', 'NURSE']:
        user_role = "ASSISTANT"
    
    # Create user account
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    new_user = User(
        user_id=user_id,
        email=staff['email'],
        name=staff['name'],
        phone=staff.get('phone'),
        password_hash=hash_password(data.password),
        auth_provider="email",
        role=user_role,
        clinic_id=staff['clinic_id']
    )
    user_doc = new_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    
    # Update staff record
    await db.staff.update_one(
        {"staff_id": staff['staff_id']},
        {"$set": {
            "invitation_status": "ACCEPTED",
            "invitation_token": None,
            "invitation_expires_at": None,
            "user_id": user_id
        }}
    )
    
    # Create session
    session_token = await create_session(user_id, response)
    
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    user_data['redirect_to'] = '/staff-dashboard'
    
    logger.info(f"Staff invitation accepted for {staff['email']}, user {user_id} created")
    
    return {"user": user_data, "session_token": session_token}

@api_router.put("/staff/{staff_id}")
async def update_staff(staff_id: str, data: StaffUpdate, request: Request):
    """Update staff member details"""
    user = await require_clinic_admin(request)
    
    staff = await db.staff.find_one({"staff_id": staff_id, "clinic_id": user.clinic_id}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Build update data
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.role is not None:
        update_data["role"] = data.role
        # Also update the linked user's role if exists
        if staff.get('user_id'):
            user_role = "ASSISTANT"
            if data.role == 'DOCTOR':
                user_role = "DOCTOR"
            await db.users.update_one(
                {"user_id": staff['user_id']},
                {"$set": {"role": user_role}}
            )
    
    if update_data:
        await db.staff.update_one(
            {"staff_id": staff_id},
            {"$set": update_data}
        )
    
    updated_staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    return updated_staff

@api_router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str, request: Request):
    user = await require_clinic_admin(request)
    
    staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    if not staff or staff["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Deactivate staff record
    await db.staff.update_one({"staff_id": staff_id}, {"$set": {"is_active": False}})
    
    # If staff has an associated user, deactivate that too
    if staff.get('user_id'):
        await db.users.update_one({"user_id": staff['user_id']}, {"$set": {"is_active": False}})
    
    return {"message": "Staff removed successfully"}


def send_staff_invitation_email(recipient_email: str, recipient_name: str, role: str, invitation_link: str, clinic_name: str, inviter_name: str):
    """Send staff invitation email using Resend"""
    try:
        from_email = "MediConnect <onboarding@resend.dev>"
        
        role_display = {
            'DOCTOR': 'Doctor',
            'ASSISTANT': 'Assistant',
            'RECEPTIONIST': 'Receptionist',
            'NURSE': 'Nurse',
            'ADMIN': 'Administrator'
        }.get(role, role)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">{clinic_name}</h1>
</div>
<div style="padding: 40px 30px;">
<h2 style="color: #1f2937;">You're Invited to Join {clinic_name}</h2>
<p style="color: #4b5563;">Hello {recipient_name},</p>
<p style="color: #4b5563;">{inviter_name} has invited you to join <strong>{clinic_name}</strong> as a <strong>{role_display}</strong> on MediConnect.</p>
<p style="color: #4b5563;">Click the button below to accept your invitation and set up your account:</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{invitation_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Accept Invitation</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Or copy this link: {invitation_link}</p>
<p style="color: #9ca3af; font-size: 12px;">This invitation expires in 7 days.</p>
</div>
</div>
</body>
</html>"""
        
        text_content = f"Staff Invitation\n\nHello {recipient_name},\n\n{inviter_name} has invited you to join {clinic_name} as a {role_display}.\n\nAccept your invitation: {invitation_link}\n\nThis invitation expires in 7 days."
        
        response = resend.Emails.send({
            "from": from_email,
            "to": recipient_email,
            "subject": f"You're Invited to Join {clinic_name} - MediConnect",
            "html": html_content,
            "text": text_content
        })
        
        logger.info(f"Staff invitation email sent to {recipient_email}")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to send staff invitation email: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== SERVICES MANAGEMENT ROUTES ====================

@api_router.get("/services")
async def get_services(request: Request, clinic_id: Optional[str] = None):
    user = await get_current_user(request)
    
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        query = {"clinic_id": user.clinic_id, "is_active": True}
    elif clinic_id:
        query = {"clinic_id": clinic_id, "is_active": True}
    else:
        query = {"is_active": True}
    
    services = await db.services.find(query, {"_id": 0}).to_list(100)
    return services

@api_router.post("/services")
async def create_service(data: ServiceCreate, request: Request):
    user = await require_clinic_admin(request)
    
    service = Service(
        clinic_id=user.clinic_id,
        name=data.name,
        description=data.description,
        duration=data.duration,
        price=data.price,
        currency=data.currency
    )
    doc = service.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.services.insert_one(doc)
    
    return service

@api_router.put("/services/{service_id}")
async def update_service(service_id: str, data: ServiceCreate, request: Request):
    user = await require_clinic_admin(request)
    
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = {
        "name": data.name,
        "description": data.description,
        "duration": data.duration,
        "price": data.price,
        "currency": data.currency
    }
    
    await db.services.update_one(
        {"service_id": service_id},
        {"$set": update_data}
    )
    
    updated_service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    return updated_service

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str, request: Request):
    user = await require_clinic_admin(request)
    
    service = await db.services.find_one({"service_id": service_id}, {"_id": 0})
    if not service or service["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Service not found")
    
    await db.services.update_one({"service_id": service_id}, {"$set": {"is_active": False}})
    return {"message": "Service removed successfully"}

# ==================== APPOINTMENT ROUTES ====================

@api_router.get("/appointments")
async def get_appointments(
    request: Request,
    clinic_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    user = await require_auth(request)
    
    query = {}
    
    # Determine user's doctor record if they are a DOCTOR role
    user_doctor_id = None
    if user.role == "DOCTOR" and user.clinic_id:
        user_doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if user_doctor:
            user_doctor_id = user_doctor.get("doctor_id")
    
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif user.role in ["DOCTOR", "ASSISTANT"] and user.clinic_id:
        query["clinic_id"] = user.clinic_id
    elif user.role == "USER":
        query["patient_id"] = user.user_id
    
    if doctor_id:
        query["doctor_id"] = doctor_id
    if status:
        query["status"] = status
    
    if start_date:
        query["date_time"] = query.get("date_time", {})
        query["date_time"]["$gte"] = start_date
    if end_date:
        query["date_time"] = query.get("date_time", {})
        query["date_time"]["$lte"] = end_date
    
    appointments = await db.appointments.find(query, {"_id": 0}).to_list(500)
    
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"
        
        # Privacy control for doctors/assistants
        if user.role == "CLINIC_ADMIN":
            # Admin sees full details
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            apt["is_own_patient"] = True
        elif user.role == "DOCTOR":
            # Doctor sees full details only for their own patients
            is_own_patient = user_doctor_id and apt["doctor_id"] == user_doctor_id
            apt["is_own_patient"] = is_own_patient
            
            if is_own_patient:
                patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
                apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
                apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
            else:
                # For colleagues' patients: only show name and time (no sensitive data)
                apt["patient_name"] = apt.get("patient_name", "Patient")
                apt["patient_email"] = None
                apt["notes"] = None  # Hide notes for privacy
        elif user.role == "ASSISTANT":
            # Assistant sees limited info similar to colleague view
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = None  # Hide email for privacy
            apt["is_own_patient"] = False
    
    return appointments

@api_router.post("/appointments")
async def create_appointment(data: AppointmentCreate, request: Request):
    user = await require_auth(request)
    
    doctor = await db.doctors.find_one({"doctor_id": data.doctor_id, "is_active": True}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    clinic = await db.clinics.find_one({"clinic_id": data.clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    apt_datetime = data.date_time
    if apt_datetime.tzinfo is None:
        apt_datetime = apt_datetime.replace(tzinfo=timezone.utc)
    
    existing = await db.appointments.find_one({
        "doctor_id": data.doctor_id,
        "date_time": apt_datetime.isoformat(),
        "status": {"$ne": "CANCELLED"}
    })
    
    if existing:
        raise HTTPException(status_code=409, detail="This time slot is already booked")
    
    appointment = Appointment(
        patient_id=user.user_id,
        patient_name=user.name,
        patient_email=user.email,
        patient_phone=user.phone,
        doctor_id=data.doctor_id,
        clinic_id=data.clinic_id,
        date_time=apt_datetime,
        duration=data.duration or doctor.get("consultation_duration", 30),
        notes=data.notes,
        recurrence=data.recurrence
    )
    
    doc = appointment.model_dump()
    doc['date_time'] = doc['date_time'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('recurrence') and doc['recurrence'].get('end_date'):
        doc['recurrence']['end_date'] = doc['recurrence']['end_date'].isoformat()
    
    await db.appointments.insert_one(doc)
    
    await send_notification_email(
        user_id=user.user_id,
        appointment_id=appointment.appointment_id,
        notification_type="BOOKING_CONFIRMATION",
        message=f"Your appointment with {doctor['name']} on {apt_datetime.strftime('%B %d, %Y at %H:%M')} has been confirmed."
    )
    
    return appointment

@api_router.put("/appointments/{appointment_id}")
async def update_appointment(appointment_id: str, data: AppointmentUpdate, request: Request):
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if user.role == "USER" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = data.model_dump(exclude_unset=True)
    if "date_time" in update_data and update_data["date_time"]:
        new_datetime = update_data["date_time"]
        if new_datetime.tzinfo is None:
            new_datetime = new_datetime.replace(tzinfo=timezone.utc)
        
        existing = await db.appointments.find_one({
            "doctor_id": appointment["doctor_id"],
            "date_time": new_datetime.isoformat(),
            "status": {"$ne": "CANCELLED"},
            "appointment_id": {"$ne": appointment_id}
        })
        
        if existing:
            raise HTTPException(status_code=409, detail="This time slot is already booked")
        
        update_data["date_time"] = new_datetime.isoformat()
    
    await db.appointments.update_one({"appointment_id": appointment_id}, {"$set": update_data})
    
    updated = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    return updated

@api_router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str, request: Request):
    """Cancel appointment (patients can cancel without reason)"""
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if user.role == "USER" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {"status": "CANCELLED"}}
    )
    
    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="CANCELLATION",
        message="Your appointment has been cancelled."
    )
    
    return {"message": "Appointment cancelled successfully"}

@api_router.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment_with_reason(appointment_id: str, data: AppointmentCancel, request: Request, background_tasks: BackgroundTasks):
    """Cancel appointment with required reason (for Doctors/Admins)"""
    user = await require_auth(request)
    
    if user.role not in ["CLINIC_ADMIN", "DOCTOR", "ASSISTANT"]:
        raise HTTPException(status_code=403, detail="Only clinic staff can use this cancellation method")
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify access
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only cancel your own appointments")
    
    if not data.reason or len(data.reason.strip()) < 3:
        raise HTTPException(status_code=400, detail="Cancellation reason is required (minimum 3 characters)")
    
    # Update appointment with cancellation details
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "status": "CANCELLED",
            "cancellation_reason": data.reason.strip(),
            "cancelled_by": user.user_id,
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Get patient and doctor info for email
    patient = await db.users.find_one({"user_id": appointment["patient_id"]}, {"_id": 0})
    doctor = await db.doctors.find_one({"doctor_id": appointment["doctor_id"]}, {"_id": 0})
    clinic = await db.clinics.find_one({"clinic_id": appointment["clinic_id"]}, {"_id": 0})
    
    # Send cancellation notification email to patient
    if patient and patient.get("email"):
        background_tasks.add_task(
            send_cancellation_notification_email,
            patient_email=patient["email"],
            patient_name=patient.get("name", "Patient"),
            doctor_name=doctor.get("name", "Doctor") if doctor else "Doctor",
            clinic_name=clinic.get("name", "Clinic") if clinic else "Clinic",
            appointment_date=appointment["date_time"],
            cancellation_reason=data.reason.strip()
        )
    
    logger.info(f"Appointment {appointment_id} cancelled by {user.email} with reason: {data.reason}")
    
    return {"message": "Appointment cancelled successfully", "reason": data.reason}


def send_cancellation_notification_email(patient_email: str, patient_name: str, doctor_name: str, clinic_name: str, appointment_date: str, cancellation_reason: str):
    """Send cancellation notification email to patient"""
    try:
        from_email = "MediConnect <onboarding@resend.dev>"
        
        # Format date
        try:
            dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y at %H:%M")
        except:
            formatted_date = appointment_date
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">Appointment Cancelled</h1>
</div>
<div style="padding: 40px 30px;">
<p style="color: #4b5563;">Hello {patient_name},</p>
<p style="color: #4b5563;">We regret to inform you that your appointment has been cancelled.</p>

<div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
<p style="margin: 5px 0; color: #374151;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
<p style="margin: 5px 0; color: #374151;"><strong>Clinic:</strong> {clinic_name}</p>
<p style="margin: 5px 0; color: #374151;"><strong>Original Date:</strong> {formatted_date}</p>
</div>

<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0;">
<p style="margin: 0; color: #991b1b;"><strong>Reason for Cancellation:</strong></p>
<p style="margin: 5px 0 0 0; color: #7f1d1d;">{cancellation_reason}</p>
</div>

<p style="color: #4b5563;">Please contact us or book a new appointment at your convenience.</p>
<p style="color: #6b7280; font-size: 14px;">We apologize for any inconvenience caused.</p>
</div>
</div>
</body>
</html>"""
        
        text_content = f"Appointment Cancelled\n\nHello {patient_name},\n\nYour appointment with Dr. {doctor_name} at {clinic_name} on {formatted_date} has been cancelled.\n\nReason: {cancellation_reason}\n\nPlease contact us or book a new appointment at your convenience."
        
        response = resend.Emails.send({
            "from": from_email,
            "to": patient_email,
            "subject": f"Appointment Cancelled - {clinic_name}",
            "html": html_content,
            "text": text_content
        })
        
        logger.info(f"Cancellation email sent to {patient_email}")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== PATIENT HISTORY ROUTES ====================

@api_router.get("/patients/{patient_id}/history")
async def get_patient_history(patient_id: str, request: Request):
    """Get patient history - appointments, prescriptions, medical records"""
    user = await require_auth(request)
    
    # Check access - only admin, doctor with completed appointment, or the patient themselves
    if user.role == "USER" and user.user_id != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user.role == "DOCTOR":
        # Doctor can only see history if they have a completed appointment with this patient
        doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": user.clinic_id}, {"_id": 0})
        if not doctor:
            raise HTTPException(status_code=403, detail="Doctor record not found")
        
        has_appointment = await db.appointments.find_one({
            "patient_id": patient_id,
            "doctor_id": doctor["doctor_id"],
            "status": "COMPLETED"
        }, {"_id": 0})
        
        if not has_appointment:
            raise HTTPException(status_code=403, detail="You can only view history for patients you have treated")
    
    if user.role == "CLINIC_ADMIN":
        # Admin can see patients from their clinic
        patient_in_clinic = await db.appointments.find_one({
            "patient_id": patient_id,
            "clinic_id": user.clinic_id
        }, {"_id": 0})
        if not patient_in_clinic:
            raise HTTPException(status_code=403, detail="Patient not found in your clinic")
    
    # Get patient info
    patient = await db.users.find_one({"user_id": patient_id}, {"_id": 0, "password_hash": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Build query filter based on role
    query_filter = {"patient_id": patient_id}
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        query_filter["doctor_id"] = doctor["doctor_id"]
    elif user.role == "CLINIC_ADMIN":
        query_filter["clinic_id"] = user.clinic_id
    
    # Get appointments history
    appointments = await db.appointments.find(
        query_filter,
        {"_id": 0}
    ).sort("date_time", -1).to_list(100)
    
    # Enrich appointments with doctor names
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"
    
    # Get prescriptions
    prescriptions = await db.prescriptions.find(
        {"patient_id": patient_id} if user.role != "DOCTOR" else {"patient_id": patient_id, "doctor_id": doctor["doctor_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Get medical records (recommendations, letters)
    medical_records = await db.medical_records.find(
        {"patient_id": patient_id} if user.role != "DOCTOR" else {"patient_id": patient_id, "doctor_id": doctor["doctor_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {
        "patient": patient,
        "appointments": appointments,
        "prescriptions": prescriptions,
        "medical_records": medical_records
    }

@api_router.post("/prescriptions")
async def create_prescription(data: PrescriptionCreate, request: Request):
    """Create a prescription for a patient after appointment"""
    user = await require_auth(request)
    
    if user.role not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create prescriptions")
    
    # Verify appointment exists and is completed
    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create prescriptions for your own appointments")
    
    prescription = Prescription(
        appointment_id=data.appointment_id,
        patient_id=appointment["patient_id"],
        doctor_id=appointment["doctor_id"],
        clinic_id=appointment["clinic_id"],
        medications=data.medications,
        notes=data.notes
    )
    
    doc = prescription.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.prescriptions.insert_one(doc)
    
    return prescription

@api_router.post("/medical-records")
async def create_medical_record(data: MedicalRecordCreate, request: Request):
    """Create a medical record (recommendation, letter) for a patient"""
    user = await require_auth(request)
    
    if user.role not in ["CLINIC_ADMIN", "DOCTOR"]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can create medical records")
    
    # Verify appointment exists
    appointment = await db.appointments.find_one({"appointment_id": data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="You can only create records for your own appointments")
    
    record = MedicalRecord(
        appointment_id=data.appointment_id,
        patient_id=appointment["patient_id"],
        doctor_id=appointment["doctor_id"],
        clinic_id=appointment["clinic_id"],
        record_type=data.record_type,
        title=data.title,
        content=data.content
    )
    
    doc = record.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.medical_records.insert_one(doc)
    
    return record

@api_router.get("/appointments/{appointment_id}/records")
async def get_appointment_records(appointment_id: str, request: Request):
    """Get all records (prescriptions, medical records) for an appointment"""
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user.role == "USER" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "CLINIC_ADMIN" and appointment["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower()}, {"_id": 0})
        if not doctor or doctor["doctor_id"] != appointment["doctor_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    prescriptions = await db.prescriptions.find({"appointment_id": appointment_id}, {"_id": 0}).to_list(100)
    medical_records = await db.medical_records.find({"appointment_id": appointment_id}, {"_id": 0}).to_list(100)
    
    return {
        "prescriptions": prescriptions,
        "medical_records": medical_records
    }

# ==================== STATS ROUTES ====================

@api_router.get("/stats")
async def get_stats(request: Request):
    user = await require_auth(request)
    
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        clinic_id = user.clinic_id
        total_appointments = await db.appointments.count_documents({"clinic_id": clinic_id})
        total_doctors = await db.doctors.count_documents({"clinic_id": clinic_id, "is_active": True})
        total_staff = await db.staff.count_documents({"clinic_id": clinic_id, "is_active": True})
        total_services = await db.services.count_documents({"clinic_id": clinic_id, "is_active": True})
        
        now = datetime.now(timezone.utc).isoformat()
        upcoming = await db.appointments.count_documents({
            "clinic_id": clinic_id,
            "date_time": {"$gte": now},
            "status": {"$ne": "CANCELLED"}
        })
        
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
        today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat()
        today_appointments = await db.appointments.count_documents({
            "clinic_id": clinic_id,
            "date_time": {"$gte": today_start, "$lte": today_end},
            "status": {"$ne": "CANCELLED"}
        })
        
        pipeline = [
            {"$match": {"clinic_id": clinic_id}},
            {"$group": {"_id": "$patient_id"}},
            {"$count": "total"}
        ]
        result = await db.appointments.aggregate(pipeline).to_list(1)
        total_patients = result[0]["total"] if result else 0
        
        return {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming,
            "today_appointments": today_appointments,
            "total_doctors": total_doctors,
            "total_staff": total_staff,
            "total_services": total_services,
            "total_patients": total_patients
        }
    else:
        total_appointments = await db.appointments.count_documents({"patient_id": user.user_id})
        now = datetime.now(timezone.utc).isoformat()
        upcoming = await db.appointments.count_documents({
            "patient_id": user.user_id,
            "date_time": {"$gte": now},
            "status": {"$ne": "CANCELLED"}
        })
        
        return {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming
        }

@api_router.get("/stats/revenue")
async def get_revenue_stats(request: Request, period: str = "month"):
    user = await require_clinic_admin(request)
    
    return {
        "period": period,
        "total_revenue": 15000.00,
        "appointments_count": 120,
        "average_per_appointment": 125.00
    }

@api_router.get("/stats/staff")
async def get_staff_stats(request: Request):
    """Get stats for staff dashboard (Doctor/Assistant)"""
    user = await require_staff_or_admin(request)
    
    if not user.clinic_id:
        return {
            "today_appointments": 0,
            "upcoming_appointments": 0,
            "total_patients": 0
        }
    
    clinic_id = user.clinic_id
    now = datetime.now(timezone.utc).isoformat()
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
    today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat()
    
    # For doctors, filter by doctor_id if they have a linked doctor record
    query_filter = {"clinic_id": clinic_id, "status": {"$ne": "CANCELLED"}}
    
    # Check if this user is a doctor with a doctor record
    if user.role == "DOCTOR":
        doctor = await db.doctors.find_one({"email": user.email.lower(), "clinic_id": clinic_id}, {"_id": 0})
        if doctor:
            query_filter["doctor_id"] = doctor["doctor_id"]
    
    today_appointments = await db.appointments.count_documents({
        **query_filter,
        "date_time": {"$gte": today_start, "$lte": today_end}
    })
    
    upcoming = await db.appointments.count_documents({
        **query_filter,
        "date_time": {"$gte": now}
    })
    
    # Get unique patients count
    pipeline = [
        {"$match": query_filter},
        {"$group": {"_id": "$patient_id"}},
        {"$count": "total"}
    ]
    result = await db.appointments.aggregate(pipeline).to_list(1)
    total_patients = result[0]["total"] if result else 0
    
    # Get clinic info
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    
    return {
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming,
        "total_patients": total_patients,
        "clinic_name": clinic.get('name', 'Medical Center') if clinic else 'Medical Center'
    }

# ==================== ROOT ROUTE ==================== 

@api_router.get("/")
async def root():
    return {"message": "MediConnect API v2.0", "status": "healthy"}

# Definim originile pentru dezvoltare locală
origins = [
    "http://localhost:3000",      # React default
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000"],     
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
 
# Include the router
app.include_router(api_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@app.on_event("startup")
async def startup_event():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
            break
        except Exception as e:
            logger.error(f"MongoDB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error("Failed to connect to MongoDB after all retries")
    
    try:
        codes_count = await db.registration_codes.count_documents({})
        if codes_count == 0:
            codes = [
                RegistrationCode(code="CLINIC2025A"),
                RegistrationCode(code="CLINIC2025B"),
                RegistrationCode(code="CLINIC2025C"),
                RegistrationCode(code="MEDICONNECT"),
                RegistrationCode(code="HEALTHCARE"),
            ]
            for code in codes:
                doc = code.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                await db.registration_codes.insert_one(doc)
            logger.info("Created default registration codes")
    except Exception as e:
        logger.error(f"Error creating registration codes: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()