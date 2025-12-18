# ✅ Simple Testing Checklist - Print & Check Off

## 🚀 Setup
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:3000)
- [ ] No console errors on startup

---

## 👤 PATIENT TESTS

### Registration & Login
- [ ] Can register as patient
- [ ] Can login as patient
- [ ] Can logout
- [ ] Redirected to patient dashboard

### Dashboard (English)
- [ ] Welcome message shows
- [ ] Stats display correctly
- [ ] Quick actions work
- [ ] Profile tab works
- [ ] Can edit profile
- [ ] Can save changes

### Dashboard (Romanian)
- [ ] Switch to Romanian works
- [ ] All text translated
- [ ] "Panou" shows
- [ ] "Programări Viitoare" shows
- [ ] All buttons in Romanian

### Features
- [ ] Can browse medical centers
- [ ] Can search centers
- [ ] Can filter by location
- [ ] Can view center details
- [ ] Can book appointment
- [ ] Can view appointments
- [ ] Can cancel appointment
- [ ] Can view history

---

## 👨‍⚕️ ADMIN TESTS (Single Location)

### Registration
- [ ] Can register with NEW CUI
- [ ] CUI validation works
- [ ] Auto-login after registration
- [ ] Redirected to dashboard

### Dashboard (English)
- [ ] Welcome message shows
- [ ] All stats display
- [ ] Quick actions work
- [ ] Today's schedule shows

### Dashboard (Romanian)
- [ ] All text translated
- [ ] "Gestionează Medici" shows
- [ ] "Gestionează Personal" shows
- [ ] Stats in Romanian

### Manage Doctors
- [ ] Can add doctor
- [ ] Can edit doctor
- [ ] Can delete doctor
- [ ] Doctor list shows
- [ ] Specialty dropdown works
- [ ] Currency selection works

### Manage Doctors (Romanian)
- [ ] "Medici" title shows
- [ ] "Adaugă Medic" button
- [ ] Specialties in Romanian
- [ ] Form labels translated

### Manage Staff
- [ ] Can invite staff
- [ ] Can edit staff
- [ ] Can delete staff
- [ ] Status shows correctly
- [ ] Can resend invitation

### Manage Services
- [ ] Can add service
- [ ] Can edit service
- [ ] Can delete service
- [ ] Service list shows

### Manage Appointments
- [ ] Can view appointments
- [ ] Can filter by status
- [ ] Can search appointments
- [ ] Can complete appointment
- [ ] Can cancel appointment
- [ ] Can add prescription
- [ ] Can add medical record

### Settings
- [ ] Can edit clinic details
- [ ] Can set operating hours
- [ ] Can toggle online booking
- [ ] Can save changes
- [ ] Success message shows

---

## 🏢 SUPER ADMIN TESTS (Multi-Location)

### Create Locations
- [ ] Can access "Manage Locations"
- [ ] Can add location
- [ ] Can edit location
- [ ] Can delete location
- [ ] Primary badge shows
- [ ] Location grid displays

### Location Switcher
- [ ] Switcher appears in header
- [ ] Shows current location
- [ ] Dropdown opens
- [ ] Shows all locations
- [ ] Primary has star icon
- [ ] Can select location
- [ ] Page refreshes
- [ ] Data updates

### Organization Settings
- [ ] Can access org settings
- [ ] Can edit org name
- [ ] Can edit legal name
- [ ] CUI is read-only
- [ ] Can edit registration number
- [ ] Can edit contact info
- [ ] Can save changes
- [ ] Success message shows

### Access Requests
- [ ] Can view pending requests
- [ ] Can approve request
- [ ] Role selection works
- [ ] Location assignment works
- [ ] Can create proposed location
- [ ] Can reject request
- [ ] Rejection reason required
- [ ] Tabs work (PENDING/APPROVED/REJECTED)

### Multi-Location Data
- [ ] Switch to Location A
- [ ] Note stats
- [ ] Switch to Location B
- [ ] Stats change
- [ ] Doctors list changes
- [ ] Appointments change
- [ ] Switch back works

---

## 👨‍💼 STAFF TESTS

### Accept Invitation
- [ ] Invitation link works
- [ ] Shows organization name
- [ ] Shows role
- [ ] Can set password
- [ ] Account created
- [ ] Redirected to dashboard

### Staff Dashboard
- [ ] Welcome message shows
- [ ] Shows assigned location
- [ ] Today's appointments show
- [ ] Can view appointments
- [ ] Can manage schedule

### Multiple Locations
- [ ] Switcher shows assigned locations only
- [ ] Can switch between assigned
- [ ] Cannot access unassigned
- [ ] Data updates per location

---

## 🌐 TRANSLATION TESTS

### Landing Page
- [ ] English: "Modern Healthcare"
- [ ] Romanian: "Sănătate Modernă"

### Login Page
- [ ] English: "Welcome Back"
- [ ] Romanian: "Bine ai Revenit"

### Registration
- [ ] English: "Register Your Medical Center"
- [ ] Romanian: "Înregistrează Centrul Medical"

### Dashboard
- [ ] English: "Quick Actions"
- [ ] Romanian: "Acțiuni Rapide"

### Doctors
- [ ] English: "Add Doctor"
- [ ] Romanian: "Adaugă Medic"

### Appointments
- [ ] English: "Scheduled"
- [ ] Romanian: "Programate"

### Settings
- [ ] English: "Operating Hours"
- [ ] Romanian: "Program de Funcționare"

### Locations
- [ ] English: "Manage Locations"
- [ ] Romanian: "Gestionează Locațiile"

### Organization
- [ ] English: "Organization Settings"
- [ ] Romanian: "Setări Organizație"

---

## 🔄 ACCESS REQUEST WORKFLOW

### Request Access
- [ ] Enter existing CUI
- [ ] Shows "already registered"
- [ ] Button changes to "Request Access"
- [ ] Can submit request
- [ ] Redirected to confirmation
- [ ] Shows request ID

### Admin Approves
- [ ] Request appears in PENDING
- [ ] Can click "Approve"
- [ ] Modal opens
- [ ] Can select role
- [ ] Can assign locations
- [ ] Can create proposed location
- [ ] Request moves to APPROVED

### Admin Rejects
- [ ] Can click "Reject"
- [ ] Modal opens
- [ ] Reason is required
- [ ] Request moves to REJECTED

### User Logs In
- [ ] Can login with credentials
- [ ] Sees assigned locations
- [ ] Can access assigned only
- [ ] Cannot access unassigned

---

## 🔐 SECURITY TESTS

### Patient Access
- [ ] Cannot access /doctors
- [ ] Cannot access /staff
- [ ] Cannot access /services
- [ ] Cannot access /settings
- [ ] Cannot access /locations
- [ ] Can access /calendar
- [ ] Can access /appointments (own)

### Clinic Admin Access
- [ ] Can access /doctors
- [ ] Can access /staff
- [ ] Can access /services
- [ ] Can access /settings (location)
- [ ] Cannot access /locations
- [ ] Cannot access org settings

### Super Admin Access
- [ ] Can access everything
- [ ] Can access /locations
- [ ] Can access /access-requests
- [ ] Can access org settings

### Location Access
- [ ] User sees assigned locations only
- [ ] Cannot switch to unassigned
- [ ] API filtered by location
- [ ] Cannot manually access other data

### CUI Protection
- [ ] CUI is read-only
- [ ] Cannot edit in org settings
- [ ] Help text shows
- [ ] Field is disabled

---

## 🐛 ERROR HANDLING

### Network Errors
- [ ] Error message shows when offline
- [ ] Data loads when back online

### Invalid Data
- [ ] Empty form shows validation
- [ ] Invalid email shows error
- [ ] Password mismatch shows error

### 404 Errors
- [ ] Invalid URL shows 404
- [ ] Can navigate back

### Unauthorized
- [ ] Redirected to login when logged out
- [ ] Access denied for wrong role

---

## ✅ FINAL CHECKS

### Functionality
- [ ] All user roles work
- [ ] All CRUD operations work
- [ ] All forms validate
- [ ] All buttons work
- [ ] All modals work
- [ ] All dropdowns work

### Translations
- [ ] All pages translated
- [ ] Language switcher works
- [ ] No hardcoded English in RO
- [ ] No missing keys
- [ ] Placeholders translated

### Multi-Location
- [ ] Switcher works
- [ ] Location switching smooth
- [ ] Data updates correctly
- [ ] Stats filtered
- [ ] Appointments filtered
- [ ] Doctors filtered

### Performance
- [ ] Pages load fast
- [ ] No console errors
- [ ] No warnings
- [ ] Smooth transitions
- [ ] Mobile responsive

### UI/UX
- [ ] Consistent styling
- [ ] Good spacing
- [ ] Readable fonts
- [ ] Good contrast
- [ ] Loading states
- [ ] Success messages
- [ ] Clear errors

---

## 📊 SUMMARY

**Total Tests:** _____ / _____  
**Passed:** _____ ✅  
**Failed:** _____ ❌  
**Warnings:** _____ ⚠️  

**Critical Issues:**
1. _____________________
2. _____________________

**Minor Issues:**
1. _____________________
2. _____________________

**OVERALL STATUS:** ✅ PASS / ❌ FAIL / ⚠️ REVIEW

**Tested By:** _____________________  
**Date:** _____________________  
**Time:** _____________________  

---

## 🎯 QUICK 5-MINUTE TEST

If short on time, test these 5 critical items:

1. [ ] Login as Admin → Dashboard loads
2. [ ] Add Doctor → Appears in list
3. [ ] Switch Language → All text translates
4. [ ] Create Location → Can switch locations
5. [ ] Logout → Redirected to login

**If all 5 pass → System is working! ✅**

---

**Print this checklist and check off as you test! 📋**
