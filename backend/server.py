from fastapi import FastAPI, APIRouter, HTTPException, Response, Request, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from passlib.context import CryptContext
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'mediconnect_db')]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    picture: Optional[str] = None
    password_hash: Optional[str] = None  # None for Google OAuth users
    auth_provider: str = "email"  # email, google
    role: str = "USER"  # USER, CLINIC_ADMIN
    clinic_id: Optional[str] = None  # For CLINIC_ADMIN
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class ClinicRegistration(BaseModel):
    registration_code: str
    clinic_name: str
    address: str
    phone: str
    email: str
    description: Optional[str] = None
    admin_name: str
    admin_email: str
    admin_password: str
    admin_phone: Optional[str] = None

class Clinic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clinic_id: str = Field(default_factory=lambda: f"clinic_{uuid.uuid4().hex[:12]}")
    name: str
    address: str
    phone: str
    email: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    registration_code: str  # Unique code used to register
    is_verified: bool = False
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

class RegistrationCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str
    is_used: bool = False
    used_by_clinic_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))

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

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    role: str = "RECEPTIONIST"  # RECEPTIONIST, NURSE, ADMIN
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StaffCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "RECEPTIONIST"

class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    clinic_id: str
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int = 30
    price: float = 0.0

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
    
    user_data = {k: v for k, v in doc.items() if k != 'password_hash'}
    return {"user": user_data, "session_token": session_token}

@api_router.post("/auth/login")
async def login_user(data: UserLogin, response: Response):
    """Login with email/password"""
    user_doc = await db.users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user_doc.get('password_hash'):
        raise HTTPException(status_code=401, detail="Please use Google login for this account")
    
    if not verify_password(data.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    session_token = await create_session(user_doc['user_id'], response)
    
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash'}
    return {"user": user_data, "session_token": session_token}

@api_router.post("/auth/register-clinic")
async def register_clinic(data: ClinicRegistration, response: Response):
    """Register a new clinic with unique registration code"""
    # Validate registration code
    code_doc = await db.registration_codes.find_one(
        {"code": data.registration_code, "is_used": False},
        {"_id": 0}
    )
    if not code_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired registration code")
    
    expires_at = code_doc.get('expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Registration code has expired")
    
    # Check if admin email exists
    existing_user = await db.users.find_one({"email": data.admin_email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    # Create clinic
    clinic_id = f"clinic_{uuid.uuid4().hex[:12]}"
    clinic = Clinic(
        clinic_id=clinic_id,
        name=data.clinic_name,
        address=data.address,
        phone=data.phone,
        email=data.email.lower(),
        description=data.description,
        registration_code=data.registration_code,
        is_verified=True
    )
    clinic_doc = clinic.model_dump()
    clinic_doc['created_at'] = clinic_doc['created_at'].isoformat()
    await db.clinics.insert_one(clinic_doc)
    
    # Create clinic admin user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    admin_user = User(
        user_id=user_id,
        email=data.admin_email.lower(),
        name=data.admin_name,
        phone=data.admin_phone,
        password_hash=hash_password(data.admin_password),
        auth_provider="email",
        role="CLINIC_ADMIN",
        clinic_id=clinic_id
    )
    user_doc = admin_user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.users.insert_one(user_doc)
    
    # Mark registration code as used
    await db.registration_codes.update_one(
        {"code": data.registration_code},
        {"$set": {"is_used": True, "used_by_clinic_id": clinic_id}}
    )
    
    session_token = await create_session(user_id, response)
    
    # Remove _id fields that MongoDB adds
    user_data = {k: v for k, v in user_doc.items() if k != 'password_hash' and k != '_id'}
    clinic_data = {k: v for k, v in clinic_doc.items() if k != '_id'}
    return {"user": user_data, "clinic": clinic_data, "session_token": session_token}

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
    
    # If clinic admin, include clinic info
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        user_dict['clinic'] = clinic
    
    return user_dict

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out successfully"}

@api_router.post("/auth/validate-code")
async def validate_registration_code(code: str):
    """Validate a registration code before clinic registration"""
    code_doc = await db.registration_codes.find_one(
        {"code": code, "is_used": False},
        {"_id": 0}
    )
    if not code_doc:
        return {"valid": False, "message": "Invalid registration code"}
    
    expires_at = code_doc.get('expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return {"valid": False, "message": "Registration code has expired"}
    
    return {"valid": True, "message": "Valid registration code"}

# ==================== CLINIC MANAGEMENT ROUTES ====================

@api_router.get("/clinics")
async def get_clinics(request: Request):
    user = await get_current_user(request)
    if user and user.role == "CLINIC_ADMIN" and user.clinic_id:
        # Clinic admin sees only their clinic
        clinic = await db.clinics.find_one({"clinic_id": user.clinic_id}, {"_id": 0})
        return [clinic] if clinic else []
    
    # Public - see all verified clinics
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
    
    await db.clinics.update_one({"clinic_id": clinic_id}, {"$set": update_data})
    return await get_clinic(clinic_id)

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
    
    # Enrich with clinic name
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
        availability_schedule=data.availability_schedule or Doctor().availability_schedule
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

# ==================== STAFF MANAGEMENT ROUTES ====================

@api_router.get("/staff")
async def get_staff(request: Request):
    user = await require_clinic_admin(request)
    staff = await db.staff.find({"clinic_id": user.clinic_id, "is_active": True}, {"_id": 0}).to_list(100)
    return staff

@api_router.post("/staff")
async def create_staff(data: StaffCreate, request: Request):
    user = await require_clinic_admin(request)
    
    staff = StaffMember(
        clinic_id=user.clinic_id,
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        role=data.role
    )
    doc = staff.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.staff.insert_one(doc)
    
    return staff

@api_router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str, request: Request):
    user = await require_clinic_admin(request)
    
    staff = await db.staff.find_one({"staff_id": staff_id}, {"_id": 0})
    if not staff or staff["clinic_id"] != user.clinic_id:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    await db.staff.update_one({"staff_id": staff_id}, {"$set": {"is_active": False}})
    return {"message": "Staff removed successfully"}

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
        price=data.price
    )
    doc = service.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.services.insert_one(doc)
    
    return service

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
    
    if user.role == "CLINIC_ADMIN" and user.clinic_id:
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
    
    # Enrich with doctor and patient info
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        apt["doctor_name"] = doctor.get("name") if doctor else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"
        
        if user.role == "CLINIC_ADMIN":
            patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
            apt["patient_name"] = apt.get("patient_name") or (patient.get("name") if patient else "Unknown")
            apt["patient_email"] = apt.get("patient_email") or (patient.get("email") if patient else "Unknown")
    
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
    
    # Check access
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
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
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
        
        # Unique patients
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
    
    # Mock revenue data for now
    return {
        "period": period,
        "total_revenue": 15000.00,
        "appointments_count": 120,
        "average_per_appointment": 125.00
    }

# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "MediConnect API v2.0", "status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Create some registration codes on startup if none exist
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
            doc['expires_at'] = doc['expires_at'].isoformat()
            await db.registration_codes.insert_one(doc)
        logger.info("Created default registration codes")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
