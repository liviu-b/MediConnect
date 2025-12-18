# 🚀 START TESTING NOW - Copy & Paste Commands

## Step 1: Open Two Terminals

### Terminal 1 - Start Backend
```bash
cd /workspaces/MediConnect/backend
python server.py
```

**Wait for:** `Uvicorn running on http://0.0.0.0:8000`

---

### Terminal 2 - Start Frontend
```bash
cd /workspaces/MediConnect/frontend
npm start
```

**Wait for:** Browser opens at `http://localhost:3000`

---

## Step 2: Quick Test (Copy these test credentials)

### Test 1: Register as Admin
**URL:** http://localhost:3000/register-clinic

**Test Data:**
```
CUI: 12345678
Organization Name: Medical Group Test
Location Name: Clinica Timișoara
City: Timișoara
Admin Name: Dr. Test Admin
Admin Email: admin@test.com
Admin Password: password123
Confirm Password: password123
```

**Expected:** ✅ Auto-login → Dashboard

---

### Test 2: Add a Doctor
**Navigate to:** Doctors page

**Test Data:**
```
Name: Dr. John Smith
Email: doctor@test.com
Phone: +40 712 345 678
Specialty: Cardiology (select from dropdown)
Duration: 30
Fee: 150
Currency: LEI
Bio: Experienced cardiologist
```

**Expected:** ✅ Doctor appears in list

---

### Test 3: Create Second Location
**Navigate to:** Manage Locations

**Test Data:**
```
Location Name: Clinica București
Address: Bd. Unirii 1
City: București
County: București
Phone: +40 21 123 4567
Email: bucuresti@test.com
```

**Expected:** ✅ Location appears, can switch

---

### Test 4: Switch Language
**Action:** Click language switcher (top right) → Select "Română"

**Expected:** ✅ All text in Romanian

---

### Test 5: Logout and Register Patient
**Action:** Logout → Register as Patient

**Test Data:**
```
Name: Test Patient
Email: patient@test.com
Password: password123
Confirm Password: password123
```

**Expected:** ✅ Patient dashboard

---

## Step 3: Test Translations

### Switch to Romanian and verify:
- [ ] Dashboard → "Panou"
- [ ] Doctors → "Medici"
- [ ] Appointments → "Programări"
- [ ] Settings → "Setări"
- [ ] Quick Actions → "Acțiuni Rapide"

---

## Step 4: Test Multi-Location

### As Admin:
1. Click LocationSwitcher (header)
2. Select "Clinica București"
3. Verify data updates
4. Switch back to "Clinica Timișoara"
5. Verify data updates again

---

## 🎯 Success Criteria

✅ **All 5 tests pass** = System is working!

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
cd /workspaces/MediConnect/backend
pip install -r requirements.txt
python server.py
```

### Frontend won't start?
```bash
cd /workspaces/MediConnect/frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Port already in use?
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database error?
Check `backend/app/config.py` for database connection settings

---

## 📊 Quick Status Check

```
✅ Backend running?     YES / NO
✅ Frontend running?    YES / NO
✅ Can register admin?  YES / NO
✅ Can add doctor?      YES / NO
✅ Can switch language? YES / NO
✅ Can create location? YES / NO
✅ Can switch location? YES / NO

ALL YES? → ✅ SYSTEM WORKING!
```

---

## 📁 Testing Documents

After quick test, use these for comprehensive testing:

1. **QUICK_TEST_GUIDE.md** - 5-10 minute test
2. **TESTING_CHECKLIST.md** - Full comprehensive test
3. **TESTING_CHECKLIST_SIMPLE.md** - Printable checklist

---

## 🎉 Ready to Test!

**Estimated Time:**
- Quick Test: 5-10 minutes
- Full Test: 30-60 minutes

**Start with:** Quick Test → If passes → Full Test

---

## 📞 Need Help?

**Check these first:**
1. Browser console (F12) - any errors?
2. Backend terminal - any errors?
3. Frontend terminal - any errors?
4. Network tab - failed requests?

**Common Issues:**
- Clear browser cache (Ctrl+Shift+R)
- Restart backend server
- Restart frontend server
- Check database connection

---

**Let's start testing! 🚀**

**Commands ready above ⬆️**  
**Just copy and paste! 📋**
