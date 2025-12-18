# MediConnect - Technical Reference

**Version:** 2.0  
**Last Updated:** January 2024  
**For:** Developers, DevOps, Technical Architects

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [API Reference](#api-reference)
4. [Authentication & Security](#authentication--security)
5. [Multi-Location Implementation](#multi-location-implementation)
6. [Frontend Architecture](#frontend-architecture)
7. [Migration Guide](#migration-guide)
8. [Development Setup](#development-setup)
9. [Testing & Debugging](#testing--debugging)
10. [Performance & Optimization](#performance--optimization)

---

## 🏗 Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │    Mobile    │  │   Desktop    │      │
│  │   (React)    │  │   (Future)   │  │   (Future)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS / REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Python)                 │   │
│  │  ┌─────────��──┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Routers   │  │  Schemas   │  │  Services  │     │   │
│  │  │  (API)     │  │ (Pydantic) │  │ (Business) │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Motor (Async Driver)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  ���                    MongoDB                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  orgs    │  │locations │  │  users   │  ...      │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Details

**Backend**
- **FastAPI 0.104+**: Modern async web framework
- **Python 3.9+**: Programming language
- **Motor 3.3+**: Async MongoDB driver
- **Pydantic v2**: Data validation and serialization
- **PyJWT**: JWT token handling
- **Passlib + Bcrypt**: Password hashing
- **Resend**: Email service integration
- **Uvicorn**: ASGI server with auto-reload

**Frontend**
- **React 18**: UI framework
- **Tailwind CSS 3**: Utility-first CSS
- **Radix UI**: Accessible component primitives
- **shadcn/ui**: Pre-built component library
- **React Router v6**: Client-side routing
- **Axios**: HTTP client
- **i18next**: Internationalization
- **React Hook Form**: Form management
- **Zod**: Schema validation
- **FullCalendar**: Calendar component

**Database**
- **MongoDB 6+**: NoSQL document database
- **Collections**: 10+ collections
- **Indexes**: Optimized for common queries
- **Async Operations**: Non-blocking I/O

**DevOps**
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Volume Mounts**: Live reload in development
- **Environment Variables**: Configuration management

---

## 🗄 Database Schema

### Collections Overview

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| organizations | Parent entities (companies) | cui, name, super_admin_ids |
| locations | Clinic branches | organization_id, name, city |
| users | All user accounts | organization_id, role, assigned_location_ids |
| access_requests | Pending access requests | cui, status, requester_email |
| appointments | Patient appointments | location_id, doctor_id, patient_id |
| doctors | Doctor profiles | organization_id, assigned_location_ids |
| services | Medical services | location_id, name, price |
| staff | Staff members | organization_id, assigned_location_ids |
| reviews | Patient reviews | location_id, doctor_id, rating |
| medical_records | Patient records | patient_id, doctor_id, location_id |

### Detailed Schema

#### organizations

```javascript
{
  _id: ObjectId("..."),
  organization_id: "org_abc123",           // Unique identifier
  cui: "12345678",                         // Romanian Fiscal Code (UNIQUE)
  name: "Medical Group XYZ",               // Display name
  legal_name: "SC Medical Group XYZ SRL", // Legal entity name
  phone: "+40123456789",
  email: "contact@medicalgroup.ro",
  website: "https://medicalgroup.ro",
  description: "Leading medical provider",
  
  // Super Admins who manage the organization
  super_admin_ids: ["user_xyz789", "user_abc456"],
  
  // Organization-wide settings
  settings: {
    allow_multi_location_booking: true,    // Patients can book at any location
    centralized_billing: false,            // Single billing for all locations
    shared_patient_records: true,          // Share records across locations
    require_approval_for_new_staff: true,  // Manual approval for staff
    default_appointment_duration: 30,      // Minutes
    booking_advance_days: 30               // How far ahead patients can book
  },
  
  // Status flags
  is_active: true,
  is_verified: true,                       // CUI verified
  
  // Timestamps
  created_at: ISODate("2024-01-01T00:00:00Z"),
  updated_at: ISODate("2024-01-15T10:30:00Z")
}
```

**Indexes:**
```javascript
db.organizations.createIndex({ "cui": 1 }, { unique: true })
db.organizations.createIndex({ "organization_id": 1 }, { unique: true })
db.organizations.createIndex({ "is_active": 1 })
```

#### locations

```javascript
{
  _id: ObjectId("..."),
  location_id: "loc_def456",               // Unique identifier
  organization_id: "org_abc123",           // FK to organization
  
  // Basic information
  name: "Clinica Timișoara",
  address: "Str. Revolutiei 10",
  city: "Timișoara",
  county: "Timiș",
  postal_code: "300001",
  phone: "+40256123456",
  email: "timisoara@medicalgroup.ro",
  description: "Modern medical facility in city center",
  
  // Working hours (24-hour format)
  working_hours: {
    monday: { start: "09:00", end: "17:00", is_closed: false },
    tuesday: { start: "09:00", end: "17:00", is_closed: false },
    wednesday: { start: "09:00", end: "17:00", is_closed: false },
    thursday: { start: "09:00", end: "17:00", is_closed: false },
    friday: { start: "09:00", end: "17:00", is_closed: false },
    saturday: { start: "10:00", end: "14:00", is_closed: false },
    sunday: { start: null, end: null, is_closed: true }
  },
  
  // Location-specific settings
  settings: {
    allow_online_booking: true,
    booking_advance_days: 30,
    require_phone_verification: false,
    send_sms_reminders: true,
    allow_walk_ins: true
  },
  
  // Metadata
  is_primary: true,                        // First location created
  is_active: true,
  display_order: 1,                        // For sorting in UI
  
  // Timestamps
  created_at: ISODate("2024-01-01T00:00:00Z"),
  updated_at: ISODate("2024-01-15T10:30:00Z")
}
```

**Indexes:**
```javascript
db.locations.createIndex({ "location_id": 1 }, { unique: true })
db.locations.createIndex({ "organization_id": 1 })
db.locations.createIndex({ "city": 1 })
db.locations.createIndex({ "is_active": 1 })
```

#### users

```javascript
{
  _id: ObjectId("..."),
  user_id: "user_xyz789",                  // Unique identifier
  email: "admin@medicalgroup.ro",          // UNIQUE
  password_hash: "$2b$12$...",             // Bcrypt hash
  
  // Personal information
  name: "John Doe",
  phone: "+40123456789",
  date_of_birth: "1985-05-15",
  gender: "M",                             // M/F/Other
  
  // Organization & Role
  organization_id: "org_abc123",           // FK to organization (null for patients)
  role: "SUPER_ADMIN",                     // See roles below
  
  // Location access
  assigned_location_ids: null,             // null = all locations, [] = specific locations
  // OR
  assigned_location_ids: ["loc_def456", "loc_ghi789"],
  
  // Legacy field (backward compatibility)
  clinic_id: "clinic_old123",              // DEPRECATED
  
  // OAuth
  google_id: null,                         // Google OAuth ID
  
  // Status flags
  is_active: true,
  is_verified: true,                       // Email verified
  is_staff: true,                          // Has staff privileges
  
  // Preferences
  preferred_language: "ro",                // en/ro
  notification_preferences: {
    email: true,
    sms: false,
    push: false
  },
  
  // Timestamps
  created_at: ISODate("2024-01-01T00:00:00Z"),
  updated_at: ISODate("2024-01-15T10:30:00Z"),
  last_login: ISODate("2024-01-15T09:00:00Z")
}
```

**Roles:**
- `SUPER_ADMIN`: Full organization access
- `LOCATION_ADMIN`: Manage assigned locations
- `STAFF`: Operational access
- `DOCTOR`: Medical staff
- `ASSISTANT`: Support staff
- `USER`: Regular patient

**Indexes:**
```javascript
db.users.createIndex({ "user_id": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "organization_id": 1 })
db.users.createIndex({ "role": 1 })
```

#### access_requests

```javascript
{
  _id: ObjectId("..."),
  request_id: "req_jkl012",                // Unique identifier
  
  // Organization info
  organization_id: "org_abc123",           // FK to organization
  cui: "12345678",                         // CUI they tried to register with
  
  // Requester information
  requester_name: "Jane Smith",
  requester_email: "jane@example.com",
  requester_phone: "+40123456789",
  password_hash: "$2b$12$...",             // Stored temporarily until approved
  
  // Proposed location (optional)
  proposed_location_name: "Clinica București",
  proposed_location_city: "București",
  proposed_location_address: "Str. Victoriei 20",
  proposed_location_phone: "+40211234567",
  
  // Request status
  status: "PENDING",                       // PENDING/APPROVED/REJECTED
  
  // Review information
  reviewed_by: null,                       // user_id of reviewer
  reviewed_at: null,
  rejection_reason: null,
  
  // Approval details (filled when approved)
  approved_role: null,                     // Role assigned
  approved_location_ids: null,             // Locations assigned
  created_location_id: null,               // If new location was created
  
  // Timestamps
  created_at: ISODate("2024-01-15T10:00:00Z"),
  expires_at: ISODate("2024-01-22T23:59:59Z"),  // 7 days expiry
  updated_at: ISODate("2024-01-15T10:30:00Z")
}
```

**Indexes:**
```javascript
db.access_requests.createIndex({ "request_id": 1 }, { unique: true })
db.access_requests.createIndex({ "organization_id": 1 })
db.access_requests.createIndex({ "status": 1 })
db.access_requests.createIndex({ "requester_email": 1 })
db.access_requests.createIndex({ "expires_at": 1 })
```

#### appointments

```javascript
{
  _id: ObjectId("..."),
  appointment_id: "apt_mno345",
  
  // Location & Organization
  location_id: "loc_def456",
  organization_id: "org_abc123",
  
  // Participants
  patient_id: "user_patient123",
  doctor_id: "doc_doctor456",
  
  // Service
  service_id: "srv_service789",
  service_name: "Consultation",
  
  // Timing
  appointment_date: "2024-01-20",
  start_time: "10:00",
  end_time: "10:30",
  duration_minutes: 30,
  
  // Status
  status: "CONFIRMED",                     // PENDING/CONFIRMED/COMPLETED/CANCELLED
  
  // Additional info
  notes: "First visit",
  cancellation_reason: null,
  
  // Timestamps
  created_at: ISODate("2024-01-15T10:00:00Z"),
  updated_at: ISODate("2024-01-15T10:30:00Z")
}
```

**Indexes:**
```javascript
db.appointments.createIndex({ "appointment_id": 1 }, { unique: true })
db.appointments.createIndex({ "location_id": 1, "appointment_date": 1 })
db.appointments.createIndex({ "doctor_id": 1, "appointment_date": 1 })
db.appointments.createIndex({ "patient_id": 1 })
db.appointments.createIndex({ "status": 1 })
```

---

## 🔌 API Reference

### Base URL
```
Development: http://localhost:8001
Production: https://api.mediconnect.ro
```

### Authentication

All endpoints (except registration and CUI validation) require authentication:

```http
Authorization: Bearer <session_token>
```

### Organizations API

#### POST /api/organizations/register

Register a new organization or create access request if CUI exists.

**Request:**
```json
{
  "cui": "12345678",
  "organization_name": "Medical Group XYZ",
  "location_name": "Clinica Timișoara",
  "location_city": "Timișoara",
  "location_county": "Timiș",
  "location_address": "Str. Revolutiei 10",
  "location_phone": "+40256123456",
  "admin_name": "John Doe",
  "admin_email": "admin@example.com",
  "admin_password": "securepass123",
  "admin_phone": "+40123456789"
}
```

**Response (New Organization - 201):**
```json
{
  "status": "success",
  "user": {
    "user_id": "user_abc123",
    "email": "admin@example.com",
    "name": "John Doe",
    "role": "SUPER_ADMIN",
    "organization_id": "org_xyz789"
  },
  "organization": {
    "organization_id": "org_xyz789",
    "cui": "12345678",
    "name": "Medical Group XYZ"
  },
  "location": {
    "location_id": "loc_def456",
    "name": "Clinica Timișoara",
    "city": "Timișoara"
  },
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (CUI Exists - Access Request Created - 200):**
```json
{
  "status": "access_request_created",
  "message": "Acest CUI este deja inregistrat. O cerere de acces a fost trimisa...",
  "request_id": "req_ghi789",
  "organization_name": "Medical Group XYZ"
}
```

**Errors:**
- `400`: Invalid CUI format
- `400`: Missing required fields
- `409`: Email already registered

---

#### POST /api/organizations/validate-cui

Validate CUI format and check availability.

**Query Parameters:**
- `cui` (required): CUI to validate

**Request:**
```http
POST /api/organizations/validate-cui?cui=12345678
```

**Response (Available - 200):**
```json
{
  "valid": true,
  "available": true,
  "registered": false,
  "message": "CUI disponibil pentru inregistrare."
}
```

**Response (Already Registered - 200):**
```json
{
  "valid": true,
  "available": false,
  "registered": true,
  "organization_name": "Medical Group XYZ",
  "message": "Acest CUI este deja inregistrat. Puteti solicita acces..."
}
```

**Response (Invalid Format - 400):**
```json
{
  "valid": false,
  "available": false,
  "message": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
}
```

---

#### GET /api/organizations/me

Get current user's organization with all locations.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "organization_id": "org_xyz789",
  "cui": "12345678",
  "name": "Medical Group XYZ",
  "legal_name": "SC Medical Group XYZ SRL",
  "phone": "+40123456789",
  "email": "contact@medicalgroup.ro",
  "website": "https://medicalgroup.ro",
  "super_admin_ids": ["user_abc123"],
  "settings": {
    "allow_multi_location_booking": true,
    "centralized_billing": false,
    "shared_patient_records": true
  },
  "locations": [
    {
      "location_id": "loc_def456",
      "name": "Clinica Timișoara",
      "city": "Timișoara",
      "is_primary": true,
      "is_active": true
    },
    {
      "location_id": "loc_ghi789",
      "name": "Clinica București",
      "city": "București",
      "is_primary": false,
      "is_active": true
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors:**
- `401`: Not authenticated
- `404`: Organization not found

---

#### PUT /api/organizations/me

Update organization details (Super Admin only).

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Updated Medical Group",
  "legal_name": "SC Medical Group SRL",
  "phone": "+40123456789",
  "email": "contact@medicalgroup.ro",
  "website": "https://medicalgroup.ro",
  "description": "Leading medical provider",
  "settings": {
    "allow_multi_location_booking": true,
    "centralized_billing": false
  }
}
```

**Response (200):**
```json
{
  "organization_id": "org_xyz789",
  "cui": "12345678",
  "name": "Updated Medical Group",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Not a Super Admin
- `404`: Organization not found

---

### Locations API

#### GET /api/locations

Get all locations user has access to.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query Parameters:**
- `is_active` (optional): Filter by active status (true/false)
- `city` (optional): Filter by city

**Response (200):**
```json
[
  {
    "location_id": "loc_def456",
    "organization_id": "org_xyz789",
    "name": "Clinica Timișoara",
    "address": "Str. Revolutiei 10",
    "city": "Timișoara",
    "county": "Timiș",
    "phone": "+40256123456",
    "email": "timisoara@medicalgroup.ro",
    "working_hours": {
      "monday": { "start": "09:00", "end": "17:00" }
    },
    "is_primary": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### GET /api/locations/{location_id}

Get specific location details.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "location_id": "loc_def456",
  "organization_id": "org_xyz789",
  "name": "Clinica Timișoara",
  "address": "Str. Revolutiei 10",
  "city": "Timișoara",
  "county": "Timiș",
  "postal_code": "300001",
  "phone": "+40256123456",
  "email": "timisoara@medicalgroup.ro",
  "description": "Modern medical facility",
  "working_hours": { /* ... */ },
  "settings": {
    "allow_online_booking": true,
    "booking_advance_days": 30
  },
  "is_primary": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: No access to this location
- `404`: Location not found

---

#### POST /api/locations

Create new location (Super Admin or Location Admin).

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Clinica Cluj",
  "address": "Piața Unirii 1",
  "city": "Cluj-Napoca",
  "county": "Cluj",
  "postal_code": "400001",
  "phone": "+40264123456",
  "email": "cluj@medicalgroup.ro",
  "description": "Modern medical facility",
  "working_hours": {
    "monday": { "start": "08:00", "end": "18:00" }
  },
  "settings": {
    "allow_online_booking": true,
    "booking_advance_days": 30
  }
}
```

**Response (201):**
```json
{
  "location_id": "loc_jkl012",
  "organization_id": "org_xyz789",
  "name": "Clinica Cluj",
  "city": "Cluj-Napoca",
  "is_primary": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions
- `400`: Invalid data

---

#### PUT /api/locations/{location_id}

Update location details.

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Updated Clinica Timișoara",
  "phone": "+40256999888",
  "working_hours": {
    "monday": { "start": "08:00", "end": "20:00" }
  }
}
```

**Response (200):**
```json
{
  "location_id": "loc_def456",
  "name": "Updated Clinica Timișoara",
  "phone": "+40256999888",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### DELETE /api/locations/{location_id}

Soft delete location (Super Admin only).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Location deleted successfully"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Only Super Admins can delete locations
- `404`: Location not found
- `400`: Cannot delete primary location

---

### Access Requests API

#### GET /api/access-requests

Get all access requests for organization (Super Admin only).

**Headers:**
```http
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): PENDING, APPROVED, REJECTED

**Response (200):**
```json
[
  {
    "request_id": "req_ghi789",
    "organization_id": "org_xyz789",
    "cui": "12345678",
    "requester_name": "Jane Smith",
    "requester_email": "jane@example.com",
    "requester_phone": "+40123456789",
    "proposed_location_name": "Clinica București",
    "proposed_location_city": "București",
    "status": "PENDING",
    "created_at": "2024-01-15T10:00:00Z",
    "expires_at": "2024-01-22T23:59:59Z"
  }
]
```

---

#### POST /api/access-requests/{request_id}/approve

Approve access request and create user account (Super Admin only).

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "role": "LOCATION_ADMIN",
  "assigned_location_ids": ["loc_def456", "loc_ghi789"],
  "create_new_location": false
}
```

**Options:**
- `role`: SUPER_ADMIN | LOCATION_ADMIN | STAFF | DOCTOR | ASSISTANT
- `assigned_location_ids`: Array of location IDs (null = all locations)
- `create_new_location`: If true, creates the proposed location

**Response (200):**
```json
{
  "message": "Access request approved successfully",
  "user_id": "user_new123",
  "new_location_id": null
}
```

---

#### POST /api/access-requests/{request_id}/reject

Reject access request (Super Admin only).

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "rejection_reason": "Invalid credentials provided"
}
```

**Response (200):**
```json
{
  "message": "Access request rejected successfully"
}
```

---

### Error Responses

All endpoints follow consistent error format:

**400 Bad Request:**
```json
{
  "detail": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Only Super Admins can approve access requests"
}
```

**404 Not Found:**
```json
{
  "detail": "Location not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "cui"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔐 Authentication & Security

### JWT Token Structure

```javascript
{
  "sub": "user_xyz789",              // user_id
  "email": "admin@example.com",
  "role": "SUPER_ADMIN",
  "organization_id": "org_abc123",
  "exp": 1705334400                  // Expiration timestamp
}
```

### Token Generation

```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Access Control

```python
async def check_location_access(user: User, location_id: str):
    """Check if user has access to location"""
    location = await db.locations.find_one({"location_id": location_id})
    
    # Check organization match
    if location['organization_id'] != user.organization_id:
        raise HTTPException(403, "Access denied")
    
    # Check location assignment
    if user.assigned_location_ids is not None:
        if location_id not in user.assigned_location_ids:
            raise HTTPException(403, "No access to this location")
    
    return location
```

### Role-Based Permissions

```python
def require_role(allowed_roles: List[str]):
    """Decorator to check user role"""
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/locations")
@require_role(["SUPER_ADMIN", "LOCATION_ADMIN"])
async def create_location(location: LocationCreate, current_user: User):
    # ...
```

---

## 🏗 Multi-Location Implementation

### Data Model Hierarchy

```
Organization (CUI: 12345678)
├── Location 1: Clinica Timișoara (Primary)
│   ├── Doctors
│   ├── Staff
│   ├── Services
│   └── Appointments
├── Location 2: Clinica București
│   ├── Doctors
│   ├── Staff
│   ├── Services
│   └── Appointments
└── Location 3: Clinica Cluj
    ├── Doctors
    ├── Staff
    ├── Services
    └── Appointments
```

### Location Context in API Calls

**Frontend sends location context:**
```javascript
// Store active location in state/context
const [activeLocationId, setActiveLocationId] = useState(null);

// Include in API calls
const response = await axios.get('/api/appointments', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Location-ID': activeLocationId
  }
});
```

**Backend filters by location:**
```python
@router.get("/appointments")
async def get_appointments(
    location_id: str = Header(None, alias="X-Location-ID"),
    current_user: User = Depends(get_current_user)
):
    # Use location from header or user's default
    active_location = location_id or current_user.assigned_location_ids[0]
    
    # Filter appointments by location
    appointments = await db.appointments.find({
        "location_id": active_location,
        "organization_id": current_user.organization_id
    }).to_list(100)
    
    return appointments
```

### Location Switcher Flow

```
1. User logs in
   ↓
2. Fetch accessible locations: GET /api/locations
   ↓
3. Display LocationSwitcher dropdown
   ↓
4. User selects location
   ↓
5. Store in state: setActiveLocationId(locationId)
   ↓
6. All API calls include X-Location-ID header
   ↓
7. Backend filters data by location
   ↓
8. UI updates with location-specific data
```

---

## 🎨 Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── ui/                      # Reusable UI components (shadcn)
│   │   ├── button.jsx
│   │   ├── dialog.jsx
│   │   ├── select.jsx
│   │   └── ...
│   ├── LocationSwitcher.jsx     # Location dropdown
│   ├── LanguageSwitcher.js      # Language selector
│   └── ...
├── pages/                       # Route components
│   ├── Dashboard.js
│   ├── Locations.js
│   ��── AccessRequests.js
│   ├── RegisterClinic.js
│   └── ...
├── i18n/                        # Internationalization
│   ├── locales/
│   │   ├── en.json
│   │   └── ro.json
│   └── index.js
├── lib/                         # Utilities
│   ├── utils.js
│   └── ro-cities.js
├── hooks/                       # Custom hooks
│   └── use-toast.js
├── App.js                       # Main component
└── index.js                     # Entry point
```

### Location Switcher Implementation

```jsx
// LocationSwitcher.jsx
import { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import axios from 'axios';

export function LocationSwitcher() {
  const [locations, setLocations] = useState([]);
  const [activeLocation, setActiveLocation] = useState(null);

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/locations', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setLocations(response.data);
      
      // Set first location as active
      if (response.data.length > 0) {
        const savedLocation = localStorage.getItem('active_location_id');
        setActiveLocation(savedLocation || response.data[0].location_id);
      }
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    }
  };

  const handleLocationChange = (locationId) => {
    setActiveLocation(locationId);
    localStorage.setItem('active_location_id', locationId);
    
    // Trigger re-fetch of data
    window.dispatchEvent(new CustomEvent('locationChanged', { 
      detail: { locationId } 
    }));
  };

  if (locations.length <= 1) return null;

  return (
    <Select value={activeLocation} onValueChange={handleLocationChange}>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Select location" />
      </SelectTrigger>
      <SelectContent>
        {locations.map(location => (
          <SelectItem key={location.location_id} value={location.location_id}>
            {location.name} - {location.city}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

### API Client with Location Context

```javascript
// lib/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'
});

// Add location context to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  const locationId = localStorage.getItem('active_location_id');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  if (locationId) {
    config.headers['X-Location-ID'] = locationId;
  }
  
  return config;
});

export default api;
```

### Internationalization Setup

```javascript
// i18n/index.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import ro from './locales/ro.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ro: { translation: ro }
    },
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

---

## 🔄 Migration Guide

### Migrating from Old Schema to Multi-Location

If you have existing data in the old schema (clinics collection), run the migration script:

```bash
cd backend
python migrate_to_organizations.py
```

### What the Migration Does

1. **Creates Organizations from Clinics**
   - Uses CUI as unique identifier
   - Converts clinic data to organization data

2. **Converts Clinics to Locations**
   - Moves clinic data to locations collection
   - Links to parent organization
   - Marks first location as primary

3. **Updates Users**
   - Changes `clinic_id` → `organization_id`
   - Adds `assigned_location_ids` field
   - Converts `CLINIC_ADMIN` → `SUPER_ADMIN`

4. **Updates Staff**
   - Changes `clinic_id` → `organization_id`
   - Adds `assigned_location_ids` field

5. **Creates Indexes**
   - Adds performance indexes
   - Ensures data integrity

### Migration Script

```python
# migrate_to_organizations.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

async def migrate():
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db = client.mediconnect
    
    print("Starting migration...")
    
    # 1. Create organizations from clinics
    clinics = await db.clinics.find({}).to_list(None)
    for clinic in clinics:
        org = {
            "organization_id": f"org_{clinic['clinic_id']}",
            "cui": clinic.get('cui', 'MIGRATED'),
            "name": clinic['name'],
            "phone": clinic.get('phone'),
            "email": clinic.get('email'),
            "super_admin_ids": [clinic.get('admin_id')],
            "is_active": True,
            "created_at": clinic.get('created_at', datetime.utcnow())
        }
        await db.organizations.insert_one(org)
        print(f"Created organization: {org['name']}")
    
    # 2. Convert clinics to locations
    for clinic in clinics:
        location = {
            "location_id": f"loc_{clinic['clinic_id']}",
            "organization_id": f"org_{clinic['clinic_id']}",
            "name": clinic['name'],
            "address": clinic.get('address'),
            "city": clinic.get('city'),
            "phone": clinic.get('phone'),
            "is_primary": True,
            "is_active": True,
            "created_at": clinic.get('created_at', datetime.utcnow())
        }
        await db.locations.insert_one(location)
        print(f"Created location: {location['name']}")
    
    # 3. Update users
    await db.users.update_many(
        {"clinic_id": {"$exists": True}},
        [
            {
                "$set": {
                    "organization_id": {"$concat": ["org_", "$clinic_id"]},
                    "assigned_location_ids": None,
                    "role": {
                        "$cond": {
                            "if": {"$eq": ["$role", "CLINIC_ADMIN"]},
                            "then": "SUPER_ADMIN",
                            "else": "$role"
                        }
                    }
                }
            }
        ]
    )
    print("Updated users")
    
    # 4. Create indexes
    await db.organizations.create_index("cui", unique=True)
    await db.locations.create_index("organization_id")
    print("Created indexes")
    
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
```

---

## 🛠 Development Setup

### Environment Variables

**Backend (.env)**
```env
# Database
MONGO_URL=mongodb://mongo:27017/mediconnect

# Security
SECRET_KEY=your-super-secure-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Email
RESEND_API_KEY=re_your_resend_api_key_here

# CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Frontend (.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8001:8001"
    volumes:
      - ./backend:/app
    environment:
      - MONGO_URL=mongodb://mongo:27017/mediconnect
    depends_on:
      - mongo
    command: uvicorn server:app --reload --host 0.0.0.0 --port 8001

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
      - REACT_APP_BACKEND_URL=http://localhost:8001

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

---

## 🧪 Testing & Debugging

### Backend Testing

```bash
# Run all tests
docker-compose exec backend python -m pytest

# Run specific test file
docker-compose exec backend python -m pytest tests/test_organizations.py

# Run with coverage
docker-compose exec backend python -m pytest --cov=app tests/

# Test imports
docker-compose exec backend python test_imports.py
```

### API Testing with curl

```bash
# Test CUI validation
curl -X POST "http://localhost:8001/api/organizations/validate-cui?cui=12345678"

# Register organization
curl -X POST http://localhost:8001/api/organizations/register \
  -H "Content-Type: application/json" \
  -d @test_data/register.json

# Get locations (with auth)
curl -X GET http://localhost:8001/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Debugging Tips

**View Backend Logs:**
```bash
docker-compose logs -f backend
```

**View Frontend Logs:**
```bash
docker-compose logs -f frontend
```

**Access MongoDB:**
```bash
docker-compose exec mongo mongosh mediconnect
```

**Check Database Collections:**
```javascript
// In mongosh
show collections
db.organizations.find().pretty()
db.locations.find().pretty()
db.users.find().pretty()
```

**Python Debugger:**
```python
# Add to code
import pdb; pdb.set_trace()

# Or use breakpoint()
breakpoint()
```

---

## ⚡ Performance & Optimization

### Database Indexes

```javascript
// Critical indexes for performance
db.organizations.createIndex({ "cui": 1 }, { unique: true })
db.organizations.createIndex({ "organization_id": 1 }, { unique: true })

db.locations.createIndex({ "location_id": 1 }, { unique: true })
db.locations.createIndex({ "organization_id": 1 })
db.locations.createIndex({ "city": 1 })

db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "organization_id": 1 })
db.users.createIndex({ "role": 1 })

db.appointments.createIndex({ "location_id": 1, "appointment_date": 1 })
db.appointments.createIndex({ "doctor_id": 1, "appointment_date": 1 })
db.appointments.createIndex({ "patient_id": 1 })
```

### Query Optimization

**Bad:**
```python
# Fetches all appointments, then filters in Python
appointments = await db.appointments.find({}).to_list(None)
filtered = [a for a in appointments if a['location_id'] == location_id]
```

**Good:**
```python
# Filters in database
appointments = await db.appointments.find({
    "location_id": location_id
}).to_list(100)
```

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache organization data
@lru_cache(maxsize=100)
async def get_organization_cached(org_id: str):
    return await db.organizations.find_one({"organization_id": org_id})

# Cache with TTL
cache = {}
CACHE_TTL = timedelta(minutes=5)

async def get_locations_cached(org_id: str):
    cache_key = f"locations_{org_id}"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if datetime.utcnow() - timestamp < CACHE_TTL:
            return data
    
    locations = await db.locations.find({"organization_id": org_id}).to_list(None)
    cache[cache_key] = (locations, datetime.utcnow())
    return locations
```

### Frontend Optimization

```javascript
// Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Locations = lazy(() => import('./pages/Locations'));

// Memoize expensive computations
const filteredAppointments = useMemo(() => {
  return appointments.filter(apt => apt.location_id === activeLocationId);
}, [appointments, activeLocationId]);

// Debounce search
const debouncedSearch = useMemo(
  () => debounce((value) => performSearch(value), 300),
  []
);
```

---

## 📚 Additional Resources

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### External Documentation
- FastAPI: https://fastapi.tiangolo.com/
- MongoDB: https://docs.mongodb.com/
- React: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/

### Code Examples
- See `backend/app/routers/` for API implementations
- See `frontend/src/pages/` for UI implementations
- See `tests/` for test examples

---

**Last Updated**: January 2024  
**Version**: 2.0  
**Maintained By**: MediConnect Development Team
