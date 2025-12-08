from fastapi import FastAPI, APIRouter, HTTPException, Response, Request, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'mediconnect_db')]

# Create the main app without a prefix
app = FastAPI(title="MediConnect API", version="1.0.0")

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
    picture: Optional[str] = None
    role: str = "USER"  # USER or ADMIN
    clinic_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "USER"

class Clinic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clinic_id: str = Field(default_factory=lambda: f"clinic_{uuid.uuid4().hex[:12]}")
    name: str
    address: str
    phone: str
    email: str
    description: Optional[str] = None
    working_hours: dict = Field(default_factory=lambda: {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": None
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClinicCreate(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    description: Optional[str] = None
    working_hours: Optional[dict] = None

class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    doctor_id: str = Field(default_factory=lambda: f"doctor_{uuid.uuid4().hex[:12]}")
    user_id: str
    clinic_id: str
    specialty: str
    bio: Optional[str] = None
    consultation_duration: int = 30  # minutes
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
    user_id: str
    clinic_id: str
    specialty: str
    bio: Optional[str] = None
    consultation_duration: int = 30
    availability_schedule: Optional[dict] = None

class DoctorPublic(BaseModel):
    doctor_id: str
    user_id: str
    clinic_id: str
    specialty: str
    bio: Optional[str] = None
    consultation_duration: int
    availability_schedule: dict
    name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None

class RecurrencePattern(BaseModel):
    pattern_type: str = "NONE"  # NONE, DAILY, WEEKLY, MONTHLY
    interval: int = 1  # every X days/weeks/months
    end_date: Optional[datetime] = None
    days_of_week: List[int] = []  # 0-6 for WEEKLY

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    appointment_id: str = Field(default_factory=lambda: f"apt_{uuid.uuid4().hex[:12]}")
    patient_id: str
    doctor_id: str
    clinic_id: str
    date_time: datetime
    duration: int = 30  # minutes
    status: str = "SCHEDULED"  # SCHEDULED, CONFIRMED, CANCELLED, COMPLETED
    notes: Optional[str] = None
    recurrence: Optional[RecurrencePattern] = None
    parent_appointment_id: Optional[str] = None  # for recurring instances
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppointmentCreate(BaseModel):
    patient_id: Optional[str] = None  # Will be set from auth for patients
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
    notification_type: str  # BOOKING_CONFIRMATION, CANCELLATION, REMINDER
    status: str = "SENT"  # SENT, FAILED
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== AUTH HELPERS ====================

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session token in cookie or header"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        return None
    
    # Check expiry with timezone awareness
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        return None
    
    return User(**user_doc)

async def require_auth(request: Request) -> User:
    """Require authentication - raises 401 if not authenticated"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def require_admin(request: Request) -> User:
    """Require admin role - raises 403 if not admin"""
    user = await require_auth(request)
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== MOCK EMAIL SERVICE ====================

async def send_notification_email(user_id: str, appointment_id: str, notification_type: str, message: str):
    """Mock email notification - logs to database instead of sending"""
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

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token after Google OAuth"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")
    
    # Call Emergent auth service to get user data
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session ID")
            
            user_data = auth_response.json()
        except Exception as e:
            logger.error(f"Auth service error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")
    
    # Check if user exists
    existing_user = await db.users.find_one(
        {"email": user_data["email"]},
        {"_id": 0}
    )
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": user_data["name"],
                "picture": user_data.get("picture")
            }}
        )
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = User(
            user_id=user_id,
            email=user_data["email"],
            name=user_data["name"],
            picture=user_data.get("picture"),
            role="USER"
        )
        doc = new_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    
    # Create session
    session_token = user_data.get("session_token", f"session_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Delete existing sessions for this user
    await db.user_sessions.delete_many({"user_id": user_id})
    
    # Create new session
    session = UserSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    session_doc = session.model_dump()
    session_doc['expires_at'] = session_doc['expires_at'].isoformat()
    session_doc['created_at'] = session_doc['created_at'].isoformat()
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    # Get full user data
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    return {"user": user_doc, "session_token": session_token}

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.model_dump()

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    return {"message": "Logged out successfully"}

@api_router.put("/auth/role")
async def update_user_role(request: Request, user_id: str, role: str):
    """Update user role (admin only)"""
    admin = await require_admin(request)
    
    if role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"Role updated to {role}"}

# ==================== CLINIC ROUTES ====================

@api_router.get("/clinics", response_model=List[Clinic])
async def get_clinics():
    """Get all clinics"""
    clinics = await db.clinics.find({}, {"_id": 0}).to_list(100)
    return clinics

@api_router.get("/clinics/{clinic_id}")
async def get_clinic(clinic_id: str):
    """Get clinic by ID"""
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

@api_router.post("/clinics", response_model=Clinic)
async def create_clinic(clinic_data: ClinicCreate, request: Request):
    """Create a new clinic (admin only)"""
    admin = await require_admin(request)
    
    clinic = Clinic(**clinic_data.model_dump())
    doc = clinic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.clinics.insert_one(doc)
    return clinic

@api_router.put("/clinics/{clinic_id}")
async def update_clinic(clinic_id: str, clinic_data: ClinicCreate, request: Request):
    """Update clinic (admin only)"""
    admin = await require_admin(request)
    
    result = await db.clinics.update_one(
        {"clinic_id": clinic_id},
        {"$set": clinic_data.model_dump(exclude_unset=True)}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    return await get_clinic(clinic_id)

@api_router.delete("/clinics/{clinic_id}")
async def delete_clinic(clinic_id: str, request: Request):
    """Delete clinic (admin only)"""
    admin = await require_admin(request)
    
    result = await db.clinics.delete_one({"clinic_id": clinic_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    return {"message": "Clinic deleted successfully"}

# ==================== DOCTOR ROUTES ====================

@api_router.get("/doctors", response_model=List[DoctorPublic])
async def get_doctors(clinic_id: Optional[str] = None):
    """Get all doctors, optionally filtered by clinic"""
    query = {}
    if clinic_id:
        query["clinic_id"] = clinic_id
    
    doctors = await db.doctors.find(query, {"_id": 0}).to_list(100)
    
    # Enrich with user data
    enriched_doctors = []
    for doc in doctors:
        user = await db.users.find_one({"user_id": doc["user_id"]}, {"_id": 0})
        if user:
            doc["name"] = user.get("name")
            doc["email"] = user.get("email")
            doc["picture"] = user.get("picture")
        enriched_doctors.append(doc)
    
    return enriched_doctors

@api_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    """Get doctor by ID"""
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Enrich with user data
    user = await db.users.find_one({"user_id": doctor["user_id"]}, {"_id": 0})
    if user:
        doctor["name"] = user.get("name")
        doctor["email"] = user.get("email")
        doctor["picture"] = user.get("picture")
    
    return doctor

@api_router.post("/doctors", response_model=Doctor)
async def create_doctor(doctor_data: DoctorCreate, request: Request):
    """Create a new doctor (admin only)"""
    admin = await require_admin(request)
    
    # Verify user exists
    user = await db.users.find_one({"user_id": doctor_data.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify clinic exists
    clinic = await db.clinics.find_one({"clinic_id": doctor_data.clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    # Update user role to ADMIN (doctors are admins)
    await db.users.update_one(
        {"user_id": doctor_data.user_id},
        {"$set": {"role": "ADMIN"}, "$addToSet": {"clinic_ids": doctor_data.clinic_id}}
    )
    
    doctor = Doctor(**doctor_data.model_dump())
    doc = doctor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.doctors.insert_one(doc)
    return doctor

@api_router.put("/doctors/{doctor_id}")
async def update_doctor(doctor_id: str, doctor_data: DoctorCreate, request: Request):
    """Update doctor (admin only)"""
    admin = await require_admin(request)
    
    result = await db.doctors.update_one(
        {"doctor_id": doctor_id},
        {"$set": doctor_data.model_dump(exclude_unset=True)}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return await get_doctor(doctor_id)

@api_router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str, request: Request):
    """Delete doctor (admin only)"""
    admin = await require_admin(request)
    
    result = await db.doctors.delete_one({"doctor_id": doctor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {"message": "Doctor deleted successfully"}

@api_router.get("/doctors/{doctor_id}/availability")
async def get_doctor_availability(doctor_id: str, date: str):
    """Get available time slots for a doctor on a specific date"""
    doctor = await db.doctors.find_one({"doctor_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Parse the date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get day of week
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = day_names[target_date.weekday()]
    
    # Get doctor's schedule for this day
    schedule = doctor.get("availability_schedule", {}).get(day_name, [])
    if not schedule:
        return {"date": date, "available_slots": []}
    
    # Get existing appointments for this doctor on this date
    start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    existing_appointments = await db.appointments.find({
        "doctor_id": doctor_id,
        "date_time": {
            "$gte": start_of_day.isoformat(),
            "$lte": end_of_day.isoformat()
        },
        "status": {"$ne": "CANCELLED"}
    }, {"_id": 0}).to_list(100)
    
    # Build booked times set
    booked_times = set()
    for apt in existing_appointments:
        apt_time = datetime.fromisoformat(apt["date_time"].replace("Z", "+00:00"))
        booked_times.add(apt_time.strftime("%H:%M"))
    
    # Generate available slots
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
                # Only show future slots for today
                if target_date > datetime.now(timezone.utc).date() or slot_datetime > datetime.now(timezone.utc):
                    available_slots.append({
                        "time": time_str,
                        "datetime": slot_datetime.isoformat()
                    })
            current += timedelta(minutes=duration)
    
    return {"date": date, "available_slots": available_slots, "duration": duration}

# ==================== APPOINTMENT ROUTES ====================

@api_router.get("/appointments")
async def get_appointments(
    request: Request,
    clinic_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    """Get appointments with filters"""
    user = await require_auth(request)
    
    query = {}
    
    # Non-admins can only see their own appointments
    if user.role != "ADMIN":
        query["patient_id"] = user.user_id
    elif patient_id:
        query["patient_id"] = patient_id
    
    if clinic_id:
        query["clinic_id"] = clinic_id
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
    enriched = []
    for apt in appointments:
        doctor = await db.doctors.find_one({"doctor_id": apt["doctor_id"]}, {"_id": 0})
        patient = await db.users.find_one({"user_id": apt["patient_id"]}, {"_id": 0})
        doctor_user = None
        if doctor:
            doctor_user = await db.users.find_one({"user_id": doctor["user_id"]}, {"_id": 0})
        
        apt["doctor_name"] = doctor_user.get("name") if doctor_user else "Unknown"
        apt["doctor_specialty"] = doctor.get("specialty") if doctor else "Unknown"
        apt["patient_name"] = patient.get("name") if patient else "Unknown"
        apt["patient_email"] = patient.get("email") if patient else "Unknown"
        enriched.append(apt)
    
    return enriched

@api_router.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str, request: Request):
    """Get appointment by ID"""
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user.role != "ADMIN" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return appointment

@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(apt_data: AppointmentCreate, request: Request):
    """Create a new appointment"""
    user = await require_auth(request)
    
    # Set patient_id
    patient_id = apt_data.patient_id if apt_data.patient_id and user.role == "ADMIN" else user.user_id
    
    # Verify doctor exists
    doctor = await db.doctors.find_one({"doctor_id": apt_data.doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Verify clinic exists
    clinic = await db.clinics.find_one({"clinic_id": apt_data.clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    # Check for double booking (atomic operation)
    apt_datetime = apt_data.date_time
    if apt_datetime.tzinfo is None:
        apt_datetime = apt_datetime.replace(tzinfo=timezone.utc)
    
    existing = await db.appointments.find_one({
        "doctor_id": apt_data.doctor_id,
        "date_time": apt_datetime.isoformat(),
        "status": {"$ne": "CANCELLED"}
    })
    
    if existing:
        raise HTTPException(status_code=409, detail="This time slot is already booked")
    
    # Create appointment
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=apt_data.doctor_id,
        clinic_id=apt_data.clinic_id,
        date_time=apt_datetime,
        duration=apt_data.duration or doctor.get("consultation_duration", 30),
        notes=apt_data.notes,
        recurrence=apt_data.recurrence
    )
    
    doc = appointment.model_dump()
    doc['date_time'] = doc['date_time'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('recurrence') and doc['recurrence'].get('end_date'):
        doc['recurrence']['end_date'] = doc['recurrence']['end_date'].isoformat()
    
    await db.appointments.insert_one(doc)
    
    # Handle recurring appointments
    if apt_data.recurrence and apt_data.recurrence.pattern_type != "NONE":
        await create_recurring_instances(appointment, apt_data.recurrence)
    
    # Send confirmation notification (mocked)
    doctor_user = await db.users.find_one({"user_id": doctor["user_id"]}, {"_id": 0})
    doctor_name = doctor_user.get("name", "Doctor") if doctor_user else "Doctor"
    await send_notification_email(
        user_id=patient_id,
        appointment_id=appointment.appointment_id,
        notification_type="BOOKING_CONFIRMATION",
        message=f"Your appointment with {doctor_name} on {apt_datetime.strftime('%B %d, %Y at %H:%M')} has been confirmed."
    )
    
    return appointment

async def create_recurring_instances(parent_appointment: Appointment, recurrence: RecurrencePattern):
    """Create recurring appointment instances"""
    if not recurrence.end_date:
        # Default to 3 months if no end date
        end_date = parent_appointment.date_time + timedelta(days=90)
    else:
        end_date = recurrence.end_date
    
    current_date = parent_appointment.date_time
    instances = []
    
    while current_date < end_date:
        if recurrence.pattern_type == "DAILY":
            current_date += timedelta(days=recurrence.interval)
        elif recurrence.pattern_type == "WEEKLY":
            current_date += timedelta(weeks=recurrence.interval)
        elif recurrence.pattern_type == "MONTHLY":
            # Add months (simplified)
            month = current_date.month + recurrence.interval
            year = current_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                current_date = current_date.replace(year=year, month=month)
            except ValueError:
                # Handle month end edge cases
                break
        else:
            break
        
        if current_date >= end_date:
            break
        
        # Check for conflicts
        existing = await db.appointments.find_one({
            "doctor_id": parent_appointment.doctor_id,
            "date_time": current_date.isoformat(),
            "status": {"$ne": "CANCELLED"}
        })
        
        if not existing:
            instance = Appointment(
                patient_id=parent_appointment.patient_id,
                doctor_id=parent_appointment.doctor_id,
                clinic_id=parent_appointment.clinic_id,
                date_time=current_date,
                duration=parent_appointment.duration,
                notes=parent_appointment.notes,
                parent_appointment_id=parent_appointment.appointment_id
            )
            doc = instance.model_dump()
            doc['date_time'] = doc['date_time'].isoformat()
            doc['created_at'] = doc['created_at'].isoformat()
            instances.append(doc)
    
    if instances:
        await db.appointments.insert_many(instances)

@api_router.put("/appointments/{appointment_id}")
async def update_appointment(appointment_id: str, apt_data: AppointmentUpdate, request: Request):
    """Update appointment"""
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user.role != "ADMIN" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = apt_data.model_dump(exclude_unset=True)
    if "date_time" in update_data and update_data["date_time"]:
        # Check for double booking
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
    
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": update_data}
    )
    
    return await get_appointment(appointment_id, request)

@api_router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str, request: Request):
    """Cancel appointment"""
    user = await require_auth(request)
    
    appointment = await db.appointments.find_one({"appointment_id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user.role != "ADMIN" and appointment["patient_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": {"status": "CANCELLED"}}
    )
    
    # Send cancellation notification
    await send_notification_email(
        user_id=appointment["patient_id"],
        appointment_id=appointment_id,
        notification_type="CANCELLATION",
        message=f"Your appointment has been cancelled."
    )
    
    return {"message": "Appointment cancelled successfully"}

# ==================== USER ROUTES ====================

@api_router.get("/users")
async def get_users(request: Request):
    """Get all users (admin only)"""
    admin = await require_admin(request)
    users = await db.users.find({}, {"_id": 0}).to_list(100)
    return users

@api_router.get("/users/{user_id}")
async def get_user(user_id: str, request: Request):
    """Get user by ID"""
    current_user = await require_auth(request)
    
    if current_user.role != "ADMIN" and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# ==================== NOTIFICATION ROUTES ====================

@api_router.get("/notifications")
async def get_notifications(request: Request):
    """Get notifications for current user"""
    user = await require_auth(request)
    
    notifications = await db.notification_logs.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return notifications

# ==================== STATS ROUTES ====================

@api_router.get("/stats")
async def get_stats(request: Request):
    """Get dashboard statistics"""
    user = await require_auth(request)
    
    if user.role == "ADMIN":
        total_appointments = await db.appointments.count_documents({})
        total_patients = await db.users.count_documents({"role": "USER"})
        total_doctors = await db.doctors.count_documents({})
        total_clinics = await db.clinics.count_documents({})
        
        # Upcoming appointments
        now = datetime.now(timezone.utc).isoformat()
        upcoming = await db.appointments.count_documents({
            "date_time": {"$gte": now},
            "status": {"$ne": "CANCELLED"}
        })
        
        return {
            "total_appointments": total_appointments,
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_clinics": total_clinics,
            "upcoming_appointments": upcoming
        }
    else:
        # Patient stats
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

# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "MediConnect API v1.0", "status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
