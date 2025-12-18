# Multi-Location API Reference

Quick reference for all new multi-location endpoints.

---

## 🔐 Authentication

All endpoints (except registration and CUI validation) require authentication:

```bash
Authorization: Bearer <session_token>
```

---

## 📍 Organizations

### Register Organization or Request Access

**Endpoint:** `POST /api/organizations/register`

**Description:** Register a new organization with CUI. If CUI exists, creates an access request instead.

**Request Body:**
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

**Response (New Organization):**
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
  "session_token": "token123..."
}
```

**Response (CUI Exists - Access Request):**
```json
{
  "status": "access_request_created",
  "message": "Acest CUI este deja inregistrat. O cerere de acces a fost trimisa...",
  "request_id": "req_ghi789",
  "organization_name": "Medical Group XYZ"
}
```

---

### Validate CUI

**Endpoint:** `POST /api/organizations/validate-cui?cui={cui}`

**Description:** Check if CUI is valid and available for registration.

**Query Parameters:**
- `cui` (required) - CUI to validate

**Response (Available):**
```json
{
  "valid": true,
  "available": true,
  "registered": false,
  "message": "CUI disponibil pentru inregistrare."
}
```

**Response (Already Registered):**
```json
{
  "valid": true,
  "available": false,
  "registered": true,
  "organization_name": "Medical Group XYZ",
  "message": "Acest CUI este deja inregistrat. Puteti solicita acces..."
}
```

**Response (Invalid Format):**
```json
{
  "valid": false,
  "available": false,
  "message": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
}
```

---

### Get My Organization

**Endpoint:** `GET /api/organizations/me`

**Description:** Get the organization details for the current user, including all locations.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "organization_id": "org_xyz789",
  "cui": "12345678",
  "name": "Medical Group XYZ",
  "phone": "+40123456789",
  "email": "contact@medicalgroup.ro",
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
      "is_primary": true
    },
    {
      "location_id": "loc_ghi789",
      "name": "Clinica București",
      "city": "București",
      "is_primary": false
    }
  ]
}
```

---

### Update Organization

**Endpoint:** `PUT /api/organizations/me`

**Description:** Update organization details (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Medical Group",
  "legal_name": "SC Medical Group SRL",
  "phone": "+40123456789",
  "email": "contact@medicalgroup.ro",
  "website": "https://medicalgroup.ro",
  "description": "Leading medical provider",
  "settings": {
    "allow_multi_location_booking": true
  }
}
```

**Response:**
```json
{
  "organization_id": "org_xyz789",
  "cui": "12345678",
  "name": "Updated Medical Group",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 📍 Locations

### List Locations

**Endpoint:** `GET /api/locations`

**Description:** Get all locations the user has access to.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
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
    "working_hours": {
      "monday": { "start": "09:00", "end": "17:00" },
      "tuesday": { "start": "09:00", "end": "17:00" }
    },
    "is_primary": true,
    "is_active": true
  },
  {
    "location_id": "loc_ghi789",
    "name": "Clinica București",
    "city": "București",
    "is_primary": false
  }
]
```

---

### Get Location

**Endpoint:** `GET /api/locations/{location_id}`

**Description:** Get details of a specific location.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
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
  "settings": {
    "allow_online_booking": true,
    "booking_advance_days": 30
  },
  "is_primary": true,
  "is_active": true
}
```

---

### Create Location

**Endpoint:** `POST /api/locations`

**Description:** Create a new location (Super Admin or Location Admin).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Clinica Cluj",
  "address": "Piața Unirii 1",
  "city": "Cluj-Napoca",
  "county": "Cluj",
  "phone": "+40264123456",
  "email": "cluj@medicalgroup.ro",
  "description": "Modern medical facility",
  "working_hours": {
    "monday": { "start": "08:00", "end": "18:00" }
  },
  "settings": {
    "allow_online_booking": true
  }
}
```

**Response:**
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

---

### Update Location

**Endpoint:** `PUT /api/locations/{location_id}`

**Description:** Update location details (Super Admin or Location Admin).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Clinica Timișoara",
  "phone": "+40256999888",
  "working_hours": {
    "monday": { "start": "08:00", "end": "20:00" }
  }
}
```

**Response:**
```json
{
  "location_id": "loc_def456",
  "name": "Updated Clinica Timișoara",
  "phone": "+40256999888",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Delete Location

**Endpoint:** `DELETE /api/locations/{location_id}`

**Description:** Soft delete a location (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Location deleted successfully"
}
```

---

## 📋 Access Requests

### List Access Requests

**Endpoint:** `GET /api/access-requests?status={status}`

**Description:** Get all access requests for the organization (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional) - Filter by status: PENDING, APPROVED, REJECTED

**Response:**
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

### Get Access Request

**Endpoint:** `GET /api/access-requests/{request_id}`

**Description:** Get details of a specific access request (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "request_id": "req_ghi789",
  "organization_id": "org_xyz789",
  "requester_name": "Jane Smith",
  "requester_email": "jane@example.com",
  "proposed_location_name": "Clinica București",
  "status": "PENDING",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### Approve Access Request

**Endpoint:** `POST /api/access-requests/{request_id}/approve`

**Description:** Approve an access request and create user account (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "role": "LOCATION_ADMIN",
  "assigned_location_ids": ["loc_def456", "loc_ghi789"],
  "create_new_location": false
}
```

**Options:**
- `role`: "SUPER_ADMIN" | "LOCATION_ADMIN" | "STAFF" | "DOCTOR" | "ASSISTANT"
- `assigned_location_ids`: Array of location IDs (null = all locations)
- `create_new_location`: If true, creates the proposed location

**Response:**
```json
{
  "message": "Access request approved successfully",
  "user_id": "user_new123",
  "new_location_id": null
}
```

---

### Reject Access Request

**Endpoint:** `POST /api/access-requests/{request_id}/reject`

**Description:** Reject an access request (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "rejection_reason": "Invalid credentials provided"
}
```

**Response:**
```json
{
  "message": "Access request rejected successfully"
}
```

---

### Delete Access Request

**Endpoint:** `DELETE /api/access-requests/{request_id}`

**Description:** Delete a rejected access request (Super Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Access request deleted successfully"
}
```

---

## 🔑 User Roles

| Role | Value | Description |
|------|-------|-------------|
| Super Admin | `SUPER_ADMIN` | Full access to organization and all locations |
| Location Admin | `LOCATION_ADMIN` | Manage assigned locations |
| Staff | `STAFF` | Operational access to assigned locations |
| Doctor | `DOCTOR` | Medical staff with patient access |
| Assistant | `ASSISTANT` | Support staff |
| User | `USER` | Regular patient account |

---

## 📊 Status Values

### Access Request Status:
- `PENDING` - Waiting for approval
- `APPROVED` - Request approved, user created
- `REJECTED` - Request rejected

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "CUI invalid. CUI-ul trebuie sa contina intre 2 si 10 cifre."
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Only Super Admins can approve access requests"
}
```

### 404 Not Found
```json
{
  "detail": "Location not found"
}
```

---

## 🧪 Testing Examples

### Test Registration Flow

```bash
# 1. Validate CUI
curl -X POST "http://localhost:8000/api/organizations/validate-cui?cui=12345678"

# 2. Register new organization
curl -X POST http://localhost:8000/api/organizations/register \
  -H "Content-Type: application/json" \
  -d '{
    "cui": "12345678",
    "organization_name": "Test Medical",
    "location_name": "Test Clinic",
    "location_city": "Timișoara",
    "admin_name": "Test Admin",
    "admin_email": "admin@test.com",
    "admin_password": "testpass123"
  }'

# 3. Try registering with same CUI (creates access request)
curl -X POST http://localhost:8000/api/organizations/register \
  -H "Content-Type: application/json" \
  -d '{
    "cui": "12345678",
    "location_name": "Another Clinic",
    "admin_name": "Another Admin",
    "admin_email": "another@test.com",
    "admin_password": "testpass123"
  }'
```

### Test Location Management

```bash
# Get all locations
curl -X GET http://localhost:8000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create new location
curl -X POST http://localhost:8000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Clinic",
    "city": "Cluj-Napoca",
    "address": "Str. Test 123"
  }'
```

### Test Access Requests

```bash
# List pending requests
curl -X GET "http://localhost:8000/api/access-requests?status=PENDING" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Approve request
curl -X POST http://localhost:8000/api/access-requests/req_abc123/approve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "LOCATION_ADMIN",
    "assigned_location_ids": ["loc_def456"]
  }'
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- CUI must be 2-10 digits
- Passwords must be at least 8 characters
- Session tokens expire after 30 days
- Soft deletes preserve data (is_active = false)

---

**For more details, see:** `MULTI_LOCATION_ARCHITECTURE.md`
