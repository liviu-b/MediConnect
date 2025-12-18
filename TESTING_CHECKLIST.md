# 🧪 MediConnect Multi-Location - Complete Testing Checklist

## Overview
This document provides a comprehensive testing checklist to verify all features work correctly across different user roles, languages, and scenarios.

---

## 🚀 Pre-Testing Setup

### 1. Start the Application

**Backend:**
```bash
cd /workspaces/MediConnect/backend
python server.py
```

**Frontend:**
```bash
cd /workspaces/MediConnect/frontend
npm start
```

**Verify:**
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] No console errors on startup

---

## 👤 Test Scenario 1: Patient User

### A. Registration & Login
- [ ] Navigate to http://localhost:3000
- [ ] Click "Register as Patient"
- [ ] Fill in registration form
- [ ] Submit and verify account created
- [ ] Log out
- [ ] Log in with patient credentials
- [ ] Verify redirected to patient dashboard

### B. Patient Dashboard (English)
- [ ] Welcome message shows patient name
- [ ] Stats show: Total Appointments, Upcoming
- [ ] Quick actions: Book Appointment, View Appointments, Browse Clinics
- [ ] Profile tab works
- [ ] Can edit name and phone
- [ ] Email is disabled (cannot change)
- [ ] Save profile works

### C. Patient Dashboard (Romanian)
- [ ] Click language switcher (top right)
- [ ] Select "Română"
- [ ] Verify all text translated:
  - [ ] "Panou" (Dashboard)
  - [ ] "Setări Profil" (Profile Settings)
  - [ ] "Bine ai revenit" (Welcome back)
  - [ ] "Programări Viitoare" (Upcoming Appointments)
  - [ ] All buttons and labels in Romanian

### D. Browse Medical Centers
- [ ] Click "Browse Medical Centers"
- [ ] Verify centers list loads
- [ ] Search functionality works
- [ ] Filter by location works
- [ ] Click on a center to view details
- [ ] Reviews section visible

### E. Book Appointment
- [ ] Click "Book Appointment" or Calendar
- [ ] Select medical center
- [ ] Select doctor
- [ ] Select date
- [ ] Select time slot
- [ ] Add notes (optional)
- [ ] Submit booking
- [ ] Verify appointment created
- [ ] Check it appears in dashboard

### F. View Appointments
- [ ] Navigate to Appointments page
- [ ] Verify appointments list shows
- [ ] Filter by status works (All, Scheduled, Confirmed, Completed, Cancelled)
- [ ] Search appointments works
- [ ] Can cancel appointment
- [ ] Cancellation reason modal appears
- [ ] Appointment status updates

### G. Patient History
- [ ] Navigate to "My History"
- [ ] Verify completed appointments show
- [ ] Prescriptions section visible
- [ ] Medical records section visible
- [ ] Can view prescription details
- [ ] Can download PDF (if available)

### H. Logout
- [ ] Click profile icon or menu
- [ ] Click "Sign Out"
- [ ] Verify redirected to login page
- [ ] Verify cannot access protected pages

---

## 👨‍⚕️ Test Scenario 2: Clinic Admin (Single Location)

### A. Registration & Login
- [ ] Navigate to http://localhost:3000/register-clinic
- [ ] Enter NEW CUI (e.g., 12345678)
- [ ] Verify CUI validation shows "available"
- [ ] Fill organization name (optional)
- [ ] Fill location name (required)
- [ ] Fill location city
- [ ] Fill admin details (name, email, password)
- [ ] Submit registration
- [ ] Verify auto-login as Super Admin
- [ ] Verify redirected to dashboard

### B. Admin Dashboard (English)
- [ ] Welcome message shows admin name
- [ ] Stats show: Today's Appointments, Upcoming, Doctors, Patients
- [ ] Quick actions: View Appointments, Manage Doctors, Manage Staff, Manage Services
- [ ] Extra stats: Total Staff, Total Services, Total Appointments
- [ ] Today's schedule shows appointments

### C. Admin Dashboard (Romanian)
- [ ] Switch to Romanian language
- [ ] Verify all text translated:
  - [ ] "Panou" (Dashboard)
  - [ ] "Programări Azi" (Today's Appointments)
  - [ ] "Gestionează Medici" (Manage Doctors)
  - [ ] "Gestionează Personal" (Manage Staff)
  - [ ] All stats and labels in Romanian

### D. Manage Doctors
- [ ] Navigate to Doctors page
- [ ] Click "Add Doctor"
- [ ] Fill doctor details:
  - [ ] Name
  - [ ] Email
  - [ ] Phone
  - [ ] Specialty (select from dropdown)
  - [ ] Consultation duration
  - [ ] Consultation fee
  - [ ] Currency (LEI or EURO)
  - [ ] Bio
- [ ] Submit and verify doctor created
- [ ] Doctor appears in list
- [ ] Edit doctor works
- [ ] Delete doctor works (with confirmation)

### E. Manage Doctors (Romanian)
- [ ] Switch to Romanian
- [ ] Verify page title: "Medici"
- [ ] Verify "Adaugă Medic" button
- [ ] Verify specialty names in Romanian
- [ ] All form labels translated

### F. Manage Staff
- [ ] Navigate to Staff page
- [ ] Click "Invite Staff"
- [ ] Fill staff details:
  - [ ] Name
  - [ ] Email
  - [ ] Phone
  - [ ] Role (select: Receptionist, Nurse, Admin, Doctor, Assistant)
- [ ] Submit invitation
- [ ] Verify staff appears with "Pending" status
- [ ] Can resend invitation
- [ ] Can edit staff details
- [ ] Can delete staff

### G. Manage Services
- [ ] Navigate to Services page
- [ ] Click "Add Service"
- [ ] Fill service details:
  - [ ] Service name
  - [ ] Description
  - [ ] Duration (minutes)
  - [ ] Price
  - [ ] Currency
- [ ] Submit and verify service created
- [ ] Edit service works
- [ ] Delete service works

### H. Manage Appointments
- [ ] Navigate to Appointments page
- [ ] View all appointments
- [ ] Filter by status works
- [ ] Search appointments works
- [ ] Can view patient details
- [ ] Can complete appointment
- [ ] Can cancel appointment with reason
- [ ] Can add prescription
- [ ] Can add medical record

### I. Settings
- [ ] Navigate to Settings page
- [ ] Verify clinic settings form shows
- [ ] Can edit clinic name
- [ ] Can edit address
- [ ] Can edit phone and email
- [ ] Can edit description
- [ ] Can toggle online booking
- [ ] Can set operating hours
- [ ] Save changes works
- [ ] Success message appears

---

## 🏢 Test Scenario 3: Super Admin (Multi-Location)

### A. Create Additional Locations
- [ ] Navigate to "Manage Locations" (in navigation)
- [ ] Click "Add Location"
- [ ] Fill location details:
  - [ ] Location name (e.g., "Clinica București")
  - [ ] Address
  - [ ] City (e.g., "București")
  - [ ] County (e.g., "București")
  - [ ] Phone
  - [ ] Email
  - [ ] Set as primary (checkbox)
- [ ] Submit and verify location created
- [ ] Location appears in grid
- [ ] Primary badge shows if selected
- [ ] Edit location works
- [ ] Delete location works (with confirmation)

### B. Location Switcher
- [ ] Verify LocationSwitcher appears in header
- [ ] Shows current location name
- [ ] Click to open dropdown
- [ ] Shows all locations
- [ ] Primary location has star icon
- [ ] Select different location
- [ ] Verify page refreshes
- [ ] Verify data updates to new location
- [ ] Dashboard stats change
- [ ] Doctors list changes
- [ ] Appointments list changes

### C. Organization Settings
- [ ] Navigate to Settings page
- [ ] Verify "Organization Settings" tab shows (for Super Admin)
- [ ] Can edit organization name
- [ ] Can edit legal name
- [ ] Can edit description
- [ ] CUI field is disabled (read-only)
- [ ] Can edit registration number
- [ ] Can edit tax registration
- [ ] Can edit legal address
- [ ] Can edit phone, email, website
- [ ] Save changes works
- [ ] Success message appears

### D. Access Requests Management
- [ ] Navigate to "Access Requests" (in navigation)
- [ ] Verify tabs: PENDING, APPROVED, REJECTED
- [ ] Can view pending requests
- [ ] Click "Approve" on a request
- [ ] Modal opens with:
  - [ ] Role selection dropdown
  - [ ] Location assignment checkboxes
  - [ ] Option to create proposed location
- [ ] Select role and locations
- [ ] Submit approval
- [ ] Request moves to APPROVED tab
- [ ] Can reject request with reason
- [ ] Rejection reason is required
- [ ] Request moves to REJECTED tab

### E. Multi-Location Data Filtering
- [ ] Switch to Location A
- [ ] Note doctors count
- [ ] Note appointments count
- [ ] Switch to Location B
- [ ] Verify doctors count changes
- [ ] Verify appointments count changes
- [ ] Verify stats update
- [ ] Switch back to Location A
- [ ] Verify data returns to Location A context

---

## 👨‍💼 Test Scenario 4: Staff Member

### A. Accept Invitation
- [ ] Staff receives invitation email
- [ ] Click invitation link
- [ ] Verify invitation page loads
- [ ] Shows organization name
- [ ] Shows role
- [ ] Shows email (disabled)
- [ ] Enter password
- [ ] Confirm password
- [ ] Submit
- [ ] Verify account created
- [ ] Redirected to staff dashboard

### B. Staff Dashboard
- [ ] Welcome message shows staff name
- [ ] Shows assigned clinic/location
- [ ] Today's appointments visible
- [ ] Upcoming appointments visible
- [ ] Total patients stat
- [ ] Account info section
- [ ] My Availability section

### C. Staff Appointments
- [ ] Navigate to Appointments
- [ ] Can view appointments
- [ ] Can filter by status
- [ ] Can search appointments
- [ ] Can view patient history
- [ ] Can add prescription (if doctor)
- [ ] Can add medical record (if doctor)
- [ ] Can complete appointment
- [ ] Can cancel appointment

### D. Staff with Multiple Locations
- [ ] Staff assigned to multiple locations
- [ ] LocationSwitcher appears in header
- [ ] Can switch between assigned locations
- [ ] Data updates per location
- [ ] Cannot access unassigned locations

---

## 🌐 Test Scenario 5: Translation Coverage

### A. Landing Page
**English:**
- [ ] "Modern Healthcare"
- [ ] "Appointment Scheduling"
- [ ] "Sign In" / "Get Started"
- [ ] "Why Choose MediConnect?"

**Romanian:**
- [ ] "Sănătate Modernă"
- [ ] "Programare Consultații"
- [ ] "Autentificare" / "Începe Acum"
- [ ] "De Ce MediConnect?"

### B. Login Page
**English:**
- [ ] "Welcome Back"
- [ ] "Sign in to your account"
- [ ] "Email" / "Password"
- [ ] "Forgot password?"
- [ ] "Don't have an account?"

**Romanian:**
- [ ] "Bine ai Revenit"
- [ ] "Conectează-te la contul tău"
- [ ] "Email" / "Parolă"
- [ ] "Ai uitat parola?"
- [ ] "Nu ai cont?"

### C. Registration Page
**English:**
- [ ] "Register Your Medical Center"
- [ ] "CUI (Unique Registration Code)"
- [ ] "Organization Name"
- [ ] "Location Name"
- [ ] "Administrator Name"

**Romanian:**
- [ ] "Înregistrează Centrul Medical"
- [ ] "CUI (Cod Unic de Înregistrare)"
- [ ] "Numele Organizației"
- [ ] "Numele Locației"
- [ ] "Numele Administratorului"

### D. Dashboard
**English:**
- [ ] "Welcome back, [Name]!"
- [ ] "Quick Actions"
- [ ] "Upcoming Appointments"
- [ ] "Today's Schedule"
- [ ] All stat labels

**Romanian:**
- [ ] "Bine ai revenit, [Name]!"
- [ ] "Acțiuni Rapide"
- [ ] "Programări Viitoare"
- [ ] "Programul de Azi"
- [ ] All stat labels

### E. Doctors Page
**English:**
- [ ] "Doctors"
- [ ] "Add Doctor"
- [ ] "Doctor Name"
- [ ] "Specialty"
- [ ] "Consultation Duration"
- [ ] "Consultation Fee"

**Romanian:**
- [ ] "Medici"
- [ ] "Adaugă Medic"
- [ ] "Numele Medicului"
- [ ] "Specialitate"
- [ ] "Durată (min)"
- [ ] "Tarif"

### F. Appointments Page
**English:**
- [ ] "Appointments"
- [ ] "Scheduled" / "Confirmed" / "Completed" / "Cancelled"
- [ ] "Cancel Appointment"
- [ ] "View Patient History"

**Romanian:**
- [ ] "Programări"
- [ ] "Programate" / "Confirmate" / "Finalizate" / "Anulate"
- [ ] "Anulează Programarea"
- [ ] "Vezi Istoricul Pacientului"

### G. Settings Page
**English:**
- [ ] "Settings"
- [ ] "Medical Center Settings"
- [ ] "Operating Hours"
- [ ] "Allow Online Booking"

**Romanian:**
- [ ] "Setări"
- [ ] "Setări Centru Medical"
- [ ] "Program de Funcționare"
- [ ] "Permite Programări Online"

### H. Locations Page
**English:**
- [ ] "Manage Locations"
- [ ] "Add Location"
- [ ] "Location Name"
- [ ] "Primary"
- [ ] "Set as primary location"

**Romanian:**
- [ ] "Gestionează Locațiile"
- [ ] "Adaugă Locație"
- [ ] "Numele Locației"
- [ ] "Principală"
- [ ] "Setează ca locație principală"

### I. Organization Settings
**English:**
- [ ] "Organization Settings"
- [ ] "Basic Information"
- [ ] "Legal Information"
- [ ] "Contact Information"
- [ ] "CUI cannot be changed after registration"

**Romanian:**
- [ ] "Setări Organizație"
- [ ] "Informații de Bază"
- [ ] "Informații Legale"
- [ ] "Informații de Contact"
- [ ] "CUI nu poate fi schimbat după înregistrare"

---

## 🔄 Test Scenario 6: Access Request Workflow

### A. Request Access (Existing CUI)
- [ ] Navigate to /register-clinic
- [ ] Enter EXISTING CUI
- [ ] Verify message: "This CUI is already registered"
- [ ] Button changes to "Request Access"
- [ ] Fill requester details
- [ ] Fill proposed location name and city
- [ ] Submit request
- [ ] Redirected to confirmation page
- [ ] Shows request ID
- [ ] Shows organization name
- [ ] Shows "What Happens Next" section

### B. Admin Approves Request
- [ ] Login as Super Admin
- [ ] Navigate to Access Requests
- [ ] See pending request
- [ ] Click "Approve"
- [ ] Select role from dropdown
- [ ] Check locations to assign
- [ ] Optionally create proposed location
- [ ] Submit approval
- [ ] Request moves to APPROVED
- [ ] User receives email notification

### C. Admin Rejects Request
- [ ] Click "Reject" on a request
- [ ] Modal opens
- [ ] Enter rejection reason (required)
- [ ] Submit rejection
- [ ] Request moves to REJECTED
- [ ] User receives email with reason

### D. New User Logs In
- [ ] User receives approval email
- [ ] Logs in with credentials
- [ ] Sees assigned locations in LocationSwitcher
- [ ] Can access assigned locations only
- [ ] Cannot access unassigned locations

---

## 🔐 Test Scenario 7: Security & Permissions

### A. Role-Based Access
**Patient:**
- [ ] Cannot access /doctors
- [ ] Cannot access /staff
- [ ] Cannot access /services
- [ ] Cannot access /settings
- [ ] Cannot access /locations
- [ ] Cannot access /access-requests
- [ ] Can access /calendar
- [ ] Can access /appointments (own only)
- [ ] Can access /clinics

**Clinic Admin (Single Location):**
- [ ] Can access /doctors
- [ ] Can access /staff
- [ ] Can access /services
- [ ] Can access /settings (location settings)
- [ ] Cannot access /locations
- [ ] Cannot access /access-requests
- [ ] Cannot access organization settings

**Super Admin:**
- [ ] Can access everything
- [ ] Can access /locations
- [ ] Can access /access-requests
- [ ] Can access organization settings
- [ ] Can manage all locations
- [ ] Can approve/reject requests

**Staff:**
- [ ] Can access /appointments
- [ ] Can access /calendar (own schedule)
- [ ] Cannot access /doctors (manage)
- [ ] Cannot access /staff (manage)
- [ ] Cannot access /settings
- [ ] Can view assigned locations only

### B. Location Access Control
- [ ] User assigned to Location A only
- [ ] Cannot switch to Location B
- [ ] LocationSwitcher shows only Location A
- [ ] API calls filtered by Location A
- [ ] Cannot manually access Location B data

### C. CUI Protection
- [ ] CUI field is read-only after registration
- [ ] Cannot edit CUI in organization settings
- [ ] Help text shows: "CUI cannot be changed"
- [ ] Field is visually disabled

---

## 🐛 Test Scenario 8: Error Handling

### A. Network Errors
- [ ] Disconnect internet
- [ ] Try to load dashboard
- [ ] Verify error message shows
- [ ] Reconnect internet
- [ ] Verify data loads

### B. Invalid Data
- [ ] Try to submit empty form
- [ ] Verify validation errors show
- [ ] Try invalid email format
- [ ] Verify email validation works
- [ ] Try password mismatch
- [ ] Verify password validation works

### C. 404 Errors
- [ ] Navigate to /invalid-page
- [ ] Verify 404 page shows
- [ ] Can navigate back to home

### D. Unauthorized Access
- [ ] Logout
- [ ] Try to access /dashboard directly
- [ ] Verify redirected to login
- [ ] Login as patient
- [ ] Try to access /doctors
- [ ] Verify access denied message

---

## ✅ Final Verification Checklist

### Functionality
- [ ] All user roles work correctly
- [ ] All CRUD operations work
- [ ] All forms validate properly
- [ ] All buttons and links work
- [ ] All modals open and close
- [ ] All dropdowns populate correctly

### Translations
- [ ] All pages translated (EN + RO)
- [ ] Language switcher works everywhere
- [ ] No hardcoded English text in RO mode
- [ ] No missing translation keys
- [ ] Placeholders translated
- [ ] Error messages translated

### Multi-Location
- [ ] LocationSwitcher appears for multi-location users
- [ ] Location switching works smoothly
- [ ] Data updates per location
- [ ] Stats filtered by location
- [ ] Appointments filtered by location
- [ ] Doctors filtered by location

### Performance
- [ ] Pages load quickly
- [ ] No console errors
- [ ] No console warnings
- [ ] Smooth transitions
- [ ] Responsive on mobile
- [ ] Works on different browsers

### UI/UX
- [ ] Consistent styling
- [ ] Proper spacing
- [ ] Readable fonts
- [ ] Good color contrast
- [ ] Loading states show
- [ ] Success messages show
- [ ] Error messages clear

---

## 📊 Testing Summary Template

```
Date: _______________
Tester: _______________
Environment: Development / Staging / Production

RESULTS:
✅ Passed: ___ / ___
❌ Failed: ___ / ___
⚠️  Warnings: ___ / ___

CRITICAL ISSUES:
1. _______________
2. _______________

MINOR ISSUES:
1. _______________
2. _______________

NOTES:
_______________
_______________

OVERALL STATUS: ✅ PASS / ❌ FAIL / ⚠️ NEEDS REVIEW
```

---

## 🎯 Quick Test (5 Minutes)

If you need a quick smoke test:

1. **Login as Admin** → Dashboard loads → Stats show
2. **Add Doctor** → Form works → Doctor appears
3. **Switch Language** → All text translates
4. **Create Location** → Location appears → Can switch
5. **Logout** → Redirected to login

If all 5 pass → ✅ System is working!

---

## 📞 Support

If you find any issues during testing:
1. Note the exact steps to reproduce
2. Take screenshots if possible
3. Check browser console for errors
4. Document the expected vs actual behavior

---

**Happy Testing! 🧪**
