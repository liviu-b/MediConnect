# MediConnect - Complete Project Overview

**Version:** 2.0  
**Last Updated:** January 2024  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Getting Started](#getting-started)
5. [Multi-Location System](#multi-location-system)
6. [User Roles & Permissions](#user-roles--permissions)
7. [Development Workflow](#development-workflow)
8. [Testing Guide](#testing-guide)
9. [Project Structure](#project-structure)
10. [Deployment](#deployment)

---

## 🏥 Project Overview

MediConnect is a comprehensive healthcare appointment and clinic management platform that facilitates connections between patients and medical clinics. The system enables seamless appointment booking, doctor management, and multi-location clinic administration.

### What Makes MediConnect Special?

- **Multi-Location Support**: Medical organizations can manage multiple clinic branches from a single account
- **Organization-Based Access**: Uses Romanian CUI (Fiscal Code) for organization identification
- **Secure Access Control**: Role-based permissions with access request workflow
- **Multilingual**: Full support for English and Romanian
- **Modern Architecture**: FastAPI backend with React frontend, fully containerized

---

## 🚀 Key Features

### For Patients

- **User Accounts**: Secure registration and login (Email/Password & Google OAuth)
- **Appointment Booking**: Search for clinics or doctors and book appointments based on real-time availability
- **Dashboard**: View upcoming and past appointments
- **Notifications**: Email notifications for booking confirmations and cancellations
- **Multi-Location Access**: Book appointments at any location within an organization

### For Clinics & Medical Organizations

- **Organization Management**: 
  - Register organization using Romanian CUI
  - Manage multiple clinic locations from one account
  - Centralized organization settings
  
- **Location Management**:
  - Create and manage multiple clinic branches
  - Location-specific settings and working hours
  - Location switcher for easy navigation
  
- **Staff Management**:
  - Manage doctors and reception staff across locations
  - Role-based access control (Super Admin, Location Admin, Staff, Doctor, Assistant)
  - Staff invitation and access request system
  
- **Doctor Profiles**:
  - Detailed profiles with specialties, bios, and consultation fees
  - Availability scheduler with granular control
  - Recurring availability patterns
  
- **Service Management**:
  - Define medical services, durations, and prices
  - Location-specific service offerings
  
- **Analytics**:
  - Dashboard with statistics on appointments, revenue, and patient volume
  - Location-specific and organization-wide analytics

### Access Request System

When someone tries to register with an existing CUI:
1. System creates an access request instead of a new organization
2. Existing Super Admins receive notification
3. Super Admin reviews and approves/rejects the request
4. Upon approval, new user account is created with assigned role and locations
5. New user receives email notification and can log in

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: MongoDB (via Motor async driver)
- **Validation**: Pydantic v2
- **Authentication**: JWT & OAuth2
- **Email**: Resend API integration
- **Server**: Uvicorn with auto-reload

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Components**: Radix UI / shadcn-ui
- **Calendar**: FullCalendar
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Internationalization**: i18next (EN/RO support)
- **Build Tool**: Create React App with CRACO

### DevOps
- **Containerization**: Docker & Docker Compose
- **Development**: Live reload enabled for both frontend and backend
- **Package Managers**: Pip (Python), Yarn (Node.js)

---

## 📦 Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.9+, Node.js 16+, MongoDB (for manual setup)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mediconnect.git
   cd mediconnect
   ```

2. **Create environment variables**
   
   Create `.env` file in `backend/` directory:
   ```env
   MONGO_URL=mongodb://mongo:27017/mediconnect
   SECRET_KEY=your_secure_secret_key_here
   RESEND_API_KEY=your_resend_api_key_here
   ```

3. **Start the application**
   ```bash
   # First time - build everything
   docker-compose up -d --build
   
   # Subsequent runs - just start
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

### Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with MongoDB connection
echo "MONGO_URL=mongodb://localhost:27017/mediconnect" > .env
echo "SECRET_KEY=change-this-secret-key" >> .env

# Start server
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend Setup
```bash
cd frontend
yarn install

# Create .env file
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env

# Start development server
yarn start
```

---

## 🏢 Multi-Location System

### Core Concepts

#### 1. Organization (Parent Entity)
- Identified by **CUI** (Cod Unic de Înregistrare - Romanian Fiscal Code)
- One CUI = One Organization
- Contains multiple locations (clinic branches)
- Has one or more Super Admins

#### 2. Location (Child Entity)
- Physical clinic/branch within an organization
- Each location has its own:
  - Address and contact information
  - Working hours
  - Staff assignments
  - Services offered
  - Settings

#### 3. Access Request Workflow
When someone tries to register with an existing CUI:
```
User Registration → CUI Check → Already Exists? 
  ↓ No                          ↓ Yes
Create Organization          Create Access Request
  ↓                              ↓
Auto-login                   Notify Super Admins
                                 ↓
                            Super Admin Reviews
                                 ↓
                         Approve or Reject
                                 ↓
                         Create User Account
                                 ↓
                         Email Notification
```

### Registration Flows

#### Flow 1: First Organization Registration
1. Admin visits registration page
2. Enters CUI + organization details + first location + admin credentials
3. System validates CUI (not registered)
4. Creates:
   - Organization (with CUI)
   - First Location (marked as primary)
   - Super Admin user
5. Admin auto-logs in → sees dashboard with 1 location

#### Flow 2: Access Request (CUI Already Exists)
1. New admin tries to register with existing CUI
2. System detects CUI is registered
3. Creates Access Request (status: PENDING)
4. Sends notification to existing Super Admins
5. Super Admin reviews request in dashboard
6. Super Admin approves:
   - Optionally creates new location
   - Assigns role (SUPER_ADMIN / LOCATION_ADMIN / STAFF)
   - Assigns specific locations (or all)
7. New user receives approval email
8. New user can now log in

#### Flow 3: Location Switching
1. User logs in (has access to multiple locations)
2. Dashboard shows Location Switcher dropdown in header
3. User selects location from dropdown
4. Frontend stores active_location_id in state
5. All subsequent API calls include X-Location-ID header
6. Backend filters data by selected location
7. User switches location → context changes instantly

---

## 👥 User Roles & Permissions

### Role Hierarchy

| Role | Access Level | Permissions |
|------|--------------|-------------|
| **SUPER_ADMIN** | Organization-wide | • Full access to organization settings<br>• Create/edit/delete locations<br>• Approve access requests<br>• Manage all staff across all locations<br>• View all data |
| **LOCATION_ADMIN** | Assigned locations | • Manage assigned locations<br>• View other locations (read-only)<br>• Manage staff in assigned locations<br>• View location-specific data |
| **STAFF** | Assigned locations | • View/edit operational data<br>• Manage appointments and schedules<br>• Switch between assigned locations |
| **DOCTOR** | Assigned locations | • Manage appointments<br>• Access medical records<br>• Manage availability<br>• Location-specific access |
| **ASSISTANT** | Assigned locations | • Support role<br>• Manage appointments and schedules<br>• Limited administrative access |
| **USER** | N/A | • Regular patient account<br>• Book appointments<br>• View own medical records |

### Permission Examples

**Super Admin Can:**
- ✅ Create new locations
- ✅ Delete locations
- ✅ Approve/reject access requests
- ✅ Manage organization settings
- ✅ Access all locations
- ✅ Assign roles to users

**Location Admin Can:**
- ✅ Manage assigned locations
- ✅ Add staff to assigned locations
- ✅ View other locations (read-only)
- ❌ Delete locations
- ❌ Approve access requests
- ❌ Change organization settings

**Staff/Doctor Can:**
- ✅ View assigned locations
- ✅ Manage appointments in assigned locations
- ✅ Switch between assigned locations
- ❌ Create locations
- ❌ Manage other staff
- ❌ Access unassigned locations

---

## 💻 Development Workflow

### Live Reload Setup

MediConnect is configured for **live reload** during development - see your changes instantly without rebuilding!

#### How It Works

**Backend (FastAPI)**
- Auto-reload enabled with `uvicorn --reload`
- Volume mounted: `./backend` → `/app`
- Changes to Python files automatically restart the server

**Frontend (React)**
- Hot Module Replacement (HMR) enabled
- Volume mounted: `./frontend` → `/app`
- File watching with polling for Docker compatibility

### Daily Development

```bash
# Morning: Start your dev environment
docker-compose up -d

# Work on features - changes auto-reload!
# Edit: backend/app/routers/appointments.py
# Save → Backend auto-reloads in ~1-2 seconds

# Edit: frontend/src/pages/Appointments.js  
# Save → Browser auto-refreshes immediately

# View logs in real-time
docker-compose logs -f

# End of day: Stop containers
docker-compose down
```

### When to Rebuild

Only rebuild when you change dependencies:

```bash
# Added Python package to requirements.txt
docker-compose up -d --build backend

# Added npm package to package.json
docker-compose up -d --build frontend

# Changed Docker configuration
docker-compose up -d --build
```

### Useful Commands

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend

# Execute commands inside containers
docker-compose exec backend python -m pytest
docker-compose exec frontend yarn test

# View container status
docker-compose ps

# Follow logs with timestamps
docker-compose logs -f --timestamps backend
```

---

## 🧪 Testing Guide

### Quick Test Checklist

#### Backend API Tests
```bash
# Check API documentation
curl http://localhost:8001/docs

# Test health endpoint
curl http://localhost:8001/health

# Test CUI validation
curl -X POST "http://localhost:8001/api/organizations/validate-cui?cui=12345678"
```

#### Registration Flow Test
1. Go to http://localhost:3000/register-clinic
2. Fill form with test data:
   - CUI: 12345678
   - Organization Name: Test Medical Group
   - Location Name: Test Clinic
   - City: Timișoara
   - Admin credentials
3. Submit → Should auto-login to dashboard
4. Check location switcher in header

#### Access Request Test
1. Try registering again with same CUI
2. Should show "Access Request Sent" page
3. Login as Super Admin
4. Navigate to Access Requests page
5. Approve the request
6. New user should receive email and can login

#### Location Management Test
1. Login as Super Admin
2. Navigate to Locations page
3. Create new location
4. Edit location details
5. Switch between locations using header dropdown
6. Verify data filters by selected location

#### Translation Test
1. Click language switcher in header
2. Select Romanian
3. Verify all text translates
4. Switch back to English
5. Verify translations persist across page navigation

### Testing with curl

```bash
# Register new organization
curl -X POST http://localhost:8001/api/organizations/register \
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

# Get locations (requires auth token)
curl -X GET http://localhost:8001/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create new location
curl -X POST http://localhost:8001/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Clinic",
    "city": "Cluj-Napoca",
    "address": "Str. Test 123"
  }'
```

---

## 📂 Project Structure

```
mediconnect/
├── backend/
│   ├── app/
│   │   ├── routers/              # API endpoints
│   │   │   ├── organizations.py  # Organization management
│   │   │   ├── locations.py      # Location management
│   │   │   ├── access_requests.py # Access request workflow
│   │   │   ├── appointments.py   # Appointment booking
│   │   │   ├── doctors.py        # Doctor management
│   │   │   ├── auth.py           # Authentication
│   │   │   └── ...
│   │   ├── schemas/              # Pydantic models
│   │   │   ├── organization.py
│   │   │   ├── location.py
│   │   │   ├── access_request.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── services/             # Business logic
│   │   │   ├── email.py
│   │   │   └── notifications.py
│   │   ├── config.py             # Configuration
│   │   ├── db.py                 # Database connection
│   │   ├── main.py               # FastAPI app
│   │   └── security.py           # Auth utilities
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py                 # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/               # Reusable UI components
│   │   │   ├── LocationSwitcher.jsx
│   │   │   ├── LanguageSwitcher.js
│   │   │   └── ...
│   │   ├── pages/                # Application pages
│   │   │   ├── Dashboard.js
│   │   │   ├── Locations.js
│   │   │   ├── AccessRequests.js
│   │   │   ├── RegisterClinic.js
│   │   │   └── ...
│   │   ├── i18n/                 # Internationalization
│   │   │   ├── locales/
│   │   │   │   ├── en.json
│   │   │   │   └── ro.json
│   │   │   └── index.js
│   │   ├── lib/                  # Utilities
│   │   ├── App.js                # Main React component
│   │   └── index.js              # Entry point
│   ├── public/
│   ├── Dockerfile
│   └── package.json
���
├── docker-compose.yml            # Container orchestration
├── MEDICONNECT_OVERVIEW.md       # This file
├── TECHNICAL_REFERENCE.md        # Technical documentation
└── README.md                     # Quick start guide
```

---

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d --build

# Or use existing docker-compose.yml with production settings
docker-compose up -d --build
```

### Environment Variables

**Backend (.env)**
```env
MONGO_URL=mongodb://mongo:27017/mediconnect
SECRET_KEY=your-super-secure-secret-key-change-this
RESEND_API_KEY=re_your_resend_api_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

**Frontend (.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Production Considerations

1. **Security**:
   - Change SECRET_KEY to a strong random value
   - Use HTTPS in production
   - Set secure CORS origins
   - Enable rate limiting

2. **Database**:
   - Use MongoDB Atlas or managed MongoDB
   - Enable authentication
   - Set up backups
   - Create indexes for performance

3. **Email**:
   - Configure Resend API key
   - Set up email templates
   - Configure sender domain

4. **Monitoring**:
   - Set up logging
   - Monitor container health
   - Track API performance
   - Set up alerts

5. **Scaling**:
   - Use load balancer for multiple instances
   - Separate database server
   - CDN for static assets
   - Redis for session management

---

## 📊 Database Collections

### Core Collections

**organizations**
- Stores organization details
- Identified by unique CUI
- Contains super admin IDs
- Organization-wide settings

**locations**
- Physical clinic branches
- Linked to organization via organization_id
- Location-specific settings
- Working hours and contact info

**users**
- User accounts (patients, staff, admins)
- Linked to organization via organization_id
- Role-based access control
- Location assignments

**access_requests**
- Pending access requests
- Created when CUI already exists
- Approval workflow tracking
- Temporary password storage

**appointments**
- Patient appointments
- Linked to location
- Doctor and service information
- Status tracking

**doctors**
- Doctor profiles
- Linked to organization and locations
- Specialties and availability
- Consultation fees

**services**
- Medical services offered
- Location-specific
- Duration and pricing
- Service categories

---

## 🌍 Internationalization

MediConnect supports English and Romanian languages:

- **Frontend**: i18next with language switcher
- **Backend**: Multilingual error messages
- **Database**: Supports multilingual content
- **Translations**: Comprehensive coverage of all UI elements

### Adding New Languages

1. Create new locale file: `frontend/src/i18n/locales/[lang].json`
2. Add translations for all keys
3. Import in `frontend/src/i18n/index.js`
4. Add language option to LanguageSwitcher component

---

## 📞 Support & Resources

### Documentation
- **This File**: Complete project overview
- **TECHNICAL_REFERENCE.md**: Detailed API and architecture documentation
- **README.md**: Quick start guide

### API Documentation
- Interactive Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### External Resources
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- MongoDB: https://docs.mongodb.com/
- Tailwind CSS: https://tailwindcss.com/
- Radix UI: https://www.radix-ui.com/

---

## 🎯 Next Steps

### For New Developers
1. ✅ Read this overview document
2. ✅ Set up development environment
3. ✅ Run the application locally
4. ✅ Test basic features
5. ✅ Review TECHNICAL_REFERENCE.md
6. ✅ Start contributing!

### For Project Managers
1. ✅ Understand multi-location system
2. ✅ Review user roles and permissions
3. ✅ Plan deployment strategy
4. ✅ Set up monitoring and analytics
5. ✅ Train staff on the system

### For DevOps
1. ✅ Review deployment section
2. ✅ Set up production environment
3. ✅ Configure monitoring
4. ✅ Set up CI/CD pipeline
5. ✅ Plan backup strategy

---

## ✅ Project Status

**Current Version**: 2.0  
**Backend**: ✅ Production Ready  
**Frontend**: ✅ Production Ready  
**Multi-Location**: ✅ Complete  
**Internationalization**: ✅ Complete  
**Documentation**: ✅ Complete  

---

## 🎉 Summary

MediConnect is a modern, scalable healthcare management platform with:

- ✅ Complete multi-location support
- ✅ Secure organization-based access control
- ✅ Role-based permissions
- ✅ Multilingual support (EN/RO)
- ✅ Modern tech stack (FastAPI + React)
- ✅ Fully containerized with Docker
- ✅ Live reload for development
- ✅ Comprehensive documentation
- ✅ Production ready

**Ready to transform healthcare management! 🏥**

---

**Last Updated**: January 2024  
**Maintained By**: MediConnect Development Team  
**License**: MIT
