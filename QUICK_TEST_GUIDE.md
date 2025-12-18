# 🚀 Quick Test Guide - Start Testing in 5 Minutes!

## Step 1: Start the Application (2 minutes)

### Terminal 1 - Backend:
```bash
cd /workspaces/MediConnect/backend
python server.py
```
**Expected:** Server running on http://localhost:8000

### Terminal 2 - Frontend:
```bash
cd /workspaces/MediConnect/frontend
npm start
```
**Expected:** App opens at http://localhost:3000

---

## Step 2: Quick Smoke Test (3 minutes)

### Test 1: Register as Admin ✅
1. Go to http://localhost:3000
2. Click "Register as Medical Center"
3. Fill in:
   - CUI: `12345678`
   - Organization Name: `Test Medical Group`
   - Location Name: `Test Clinic Timișoara`
   - City: `Timișoara`
   - Admin Name: `Dr. Test Admin`
   - Email: `admin@test.com`
   - Password: `password123`
   - Confirm Password: `password123`
4. Click "Register Medical Center"

**Expected:** ✅ Auto-login → Dashboard shows

### Test 2: Check Dashboard ✅
**Expected:**
- Welcome message with your name
- Stats showing (Today: 0, Upcoming: 0, Doctors: 0, Patients: 0)
- Quick Actions buttons
- No console errors

### Test 3: Switch Language ✅
1. Click language switcher (top right)
2. Select "Română"

**Expected:**
- "Dashboard" → "Panou"
- "Quick Actions" → "Acțiuni Rapide"
- All text in Romanian

### Test 4: Add a Doctor ✅
1. Click "Doctors" in sidebar
2. Click "Add Doctor" (or "Adaugă Medic" in Romanian)
3. Fill in:
   - Name: `John Smith`
   - Email: `doctor@test.com`
   - Specialty: Select any
   - Duration: `30`
   - Fee: `100`
4. Click "Save"

**Expected:** ✅ Doctor appears in list

### Test 5: Create Second Location ✅
1. Click "Manage Locations" in sidebar
2. Click "Add Location"
3. Fill in:
   - Location Name: `Test Clinic București`
   - City: `București`
   - County: `București`
4. Click "Add"

**Expected:** ✅ Location appears in grid

### Test 6: Switch Locations ✅
1. Look at header - find LocationSwitcher dropdown
2. Click it - should show both locations
3. Select "Test Clinic București"

**Expected:**
- Page refreshes
- Dashboard stats update
- Doctors list updates (should be empty for new location)

---

## Step 3: Test Patient Flow (2 minutes)

### Test 7: Logout and Register as Patient ✅
1. Click profile icon → "Sign Out"
2. Click "Register as Patient"
3. Fill in:
   - Name: `Test Patient`
   - Email: `patient@test.com`
   - Password: `password123`
4. Submit

**Expected:** ✅ Patient dashboard shows

### Test 8: Patient Dashboard ✅
**Expected:**
- Different dashboard (patient view)
- Can see "Book Appointment" button
- Can see "Browse Medical Centers"
- Stats show: Total Appointments: 0, Upcoming: 0

### Test 9: Browse Clinics ✅
1. Click "Browse Medical Centers"

**Expected:**
- List of medical centers shows
- Can search and filter
- Your test clinic appears

---

## Step 4: Test Translations (1 minute)

### Test 10: Check All Pages in Romanian ✅
1. Switch to Romanian (Română)
2. Navigate through:
   - Dashboard → "Panou" ✅
   - Appointments → "Programări" ✅
   - Medical Centers → "Centre Medicale" ✅
   - Settings → "Setări" ✅

**Expected:** All text in Romanian, no English

---

## ✅ Quick Test Results

If all 10 tests pass:
- ✅ **System is working!**
- ✅ **Multi-location feature works!**
- ✅ **Translations work!**
- ✅ **User roles work!**

---

## 🐛 Common Issues & Solutions

### Issue 1: Backend won't start
**Error:** `ModuleNotFoundError`
**Solution:**
```bash
cd /workspaces/MediConnect/backend
pip install -r requirements.txt
python server.py
```

### Issue 2: Frontend won't start
**Error:** `npm ERR!`
**Solution:**
```bash
cd /workspaces/MediConnect/frontend
npm install
npm start
```

### Issue 3: Database error
**Error:** `database connection failed`
**Solution:**
```bash
# Check if PostgreSQL is running
# Update database connection in backend/app/config.py
```

### Issue 4: CUI already exists
**Solution:** Use a different CUI number (e.g., 87654321)

### Issue 5: Translation not showing
**Solution:**
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check browser console for errors

---

## 📊 Test Status Template

```
✅ Test 1: Register Admin - PASS
✅ Test 2: Dashboard - PASS
✅ Test 3: Language Switch - PASS
✅ Test 4: Add Doctor - PASS
✅ Test 5: Create Location - PASS
✅ Test 6: Switch Location - PASS
✅ Test 7: Register Patient - PASS
✅ Test 8: Patient Dashboard - PASS
✅ Test 9: Browse Clinics - PASS
✅ Test 10: Translations - PASS

OVERALL: ✅ ALL TESTS PASSED
```

---

## 🎯 Next Steps

After quick test passes:
1. ✅ Run full testing checklist (TESTING_CHECKLIST.md)
2. ✅ Test all user roles
3. ✅ Test all CRUD operations
4. ✅ Test error scenarios
5. ✅ Test on different browsers

---

## 📞 Need Help?

**Check:**
1. Browser console (F12) for errors
2. Backend terminal for errors
3. Network tab for failed requests

**Common Checks:**
- Backend running? ✅
- Frontend running? ✅
- Database connected? ✅
- No console errors? ✅

---

**Ready to test? Let's go! 🚀**

**Estimated Time:** 5-10 minutes for quick test  
**Full Test:** 30-60 minutes for comprehensive testing
