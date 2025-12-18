# 🐳 Docker Rebuild Guide - Deploy New Multi-Location Features

## Current Situation
Your app is running with `docker-compose up -d --build`, but the new multi-location features need to be deployed.

---

## 🚀 Quick Rebuild (Recommended)

### Step 1: Stop Current Containers
```bash
cd /workspaces/MediConnect
docker-compose down
```

### Step 2: Rebuild with No Cache (Ensures Fresh Build)
```bash
docker-compose build --no-cache
```

### Step 3: Start Containers
```bash
docker-compose up -d
```

### Step 4: Check Status
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND             STATUS              PORTS
mediconnect-backend   "python server.py"  Up              0.0.0.0:8000->8000/tcp
mediconnect-frontend  "npm start"         Up              0.0.0.0:3000->3000/tcp
mediconnect-db        "postgres"          Up              5432/tcp
```

---

## 🔄 Alternative: One-Command Rebuild

```bash
cd /workspaces/MediConnect
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

---

## 📊 Verify Everything is Running

### Check Container Logs

**Backend Logs:**
```bash
docker-compose logs -f backend
```
**Expected:** `Uvicorn running on http://0.0.0.0:8000`

**Frontend Logs:**
```bash
docker-compose logs -f frontend
```
**Expected:** `webpack compiled successfully`

**Database Logs:**
```bash
docker-compose logs -f db
```
**Expected:** `database system is ready to accept connections`

---

## 🗄️ Run Database Migrations

After containers are up, run migrations to add new tables:

```bash
# Option 1: If you have a migration script
docker-compose exec backend python migrations/add_multi_location.py

# Option 2: If using Alembic
docker-compose exec backend alembic upgrade head

# Option 3: Manual SQL (if needed)
docker-compose exec db psql -U postgres -d mediconnect -f /path/to/migration.sql
```

---

## ✅ Verify New Features Are Available

### Test 1: Check Backend API
```bash
curl http://localhost:8000/docs
```
**Expected:** Swagger UI with new endpoints:
- `/organizations/*`
- `/locations/*`
- `/access-requests/*`

### Test 2: Check Frontend
Open browser: http://localhost:3000

**Expected:**
- LocationSwitcher in header (after login as admin)
- New routes available:
  - `/locations`
  - `/access-requests`
  - `/access-request-sent`

### Test 3: Check Database Tables
```bash
docker-compose exec db psql -U postgres -d mediconnect -c "\dt"
```

**Expected New Tables:**
- `organizations`
- `locations`
- `access_requests`

---

## 🐛 Troubleshooting

### Issue 1: Containers Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Solution:**
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache

# Start again
docker-compose up -d
```

---

### Issue 2: Database Connection Error

**Check database is running:**
```bash
docker-compose ps db
```

**Restart database:**
```bash
docker-compose restart db
```

**Check connection:**
```bash
docker-compose exec backend python -c "from app.db import engine; print(engine)"
```

---

### Issue 3: Frontend Not Updating

**Clear frontend cache:**
```bash
docker-compose exec frontend rm -rf node_modules/.cache
docker-compose restart frontend
```

**Or rebuild frontend only:**
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

### Issue 4: Backend Not Updating

**Rebuild backend only:**
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

**Check Python packages installed:**
```bash
docker-compose exec backend pip list
```

---

### Issue 5: Port Already in Use

**Check what's using the ports:**
```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # Database
```

**Kill processes:**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Or change ports in docker-compose.yml**

---

## 🔍 Detailed Verification Steps

### Step 1: Check All Containers Running
```bash
docker-compose ps
```
All should show "Up"

### Step 2: Check Backend Health
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "healthy"}`

### Step 3: Check Frontend Loads
```bash
curl http://localhost:3000
```
**Expected:** HTML content

### Step 4: Check Database Connection
```bash
docker-compose exec backend python -c "
from app.db import SessionLocal
db = SessionLocal()
print('Database connected!')
db.close()
"
```

### Step 5: Check New Tables Exist
```bash
docker-compose exec db psql -U postgres -d mediconnect -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organizations', 'locations', 'access_requests');
"
```

**Expected:** All 3 tables listed

---

## 📋 Complete Rebuild Checklist

- [ ] Stop containers: `docker-compose down`
- [ ] Rebuild: `docker-compose build --no-cache`
- [ ] Start: `docker-compose up -d`
- [ ] Check status: `docker-compose ps` (all "Up")
- [ ] Check backend logs: `docker-compose logs backend`
- [ ] Check frontend logs: `docker-compose logs frontend`
- [ ] Run migrations (if needed)
- [ ] Test backend API: `curl http://localhost:8000/docs`
- [ ] Test frontend: Open http://localhost:3000
- [ ] Verify new tables exist
- [ ] Test registration flow
- [ ] Test location switcher
- [ ] Test translations

---

## 🎯 Quick Test After Rebuild

### Test 1: Backend API
```bash
curl http://localhost:8000/docs
```
Should show Swagger UI

### Test 2: Frontend
Open: http://localhost:3000
Should load landing page

### Test 3: Register Admin
1. Go to http://localhost:3000/register-clinic
2. Fill form with test data
3. Should auto-login to dashboard

### Test 4: Check LocationSwitcher
After login, check header for location dropdown

### Test 5: Check Translations
Click language switcher, select Romanian

**If all 5 pass → ✅ Rebuild successful!**

---

## 🔄 Development Workflow

### For Code Changes:

**Backend changes:**
```bash
docker-compose restart backend
```

**Frontend changes:**
```bash
docker-compose restart frontend
```

**Database changes:**
```bash
docker-compose restart db
```

**Full rebuild (after major changes):**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Monitor Containers

### Real-time logs (all services):
```bash
docker-compose logs -f
```

### Real-time logs (specific service):
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Check resource usage:
```bash
docker stats
```

---

## 🗑️ Clean Everything (Nuclear Option)

If nothing works, clean everything and start fresh:

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose rm -f

# Remove dangling images
docker image prune -a -f

# Remove volumes
docker volume prune -f

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## ✅ Success Indicators

After rebuild, you should see:

**Backend:**
- ✅ Uvicorn running on http://0.0.0.0:8000
- ✅ No errors in logs
- ✅ Swagger UI accessible at /docs
- ✅ New endpoints visible

**Frontend:**
- ✅ Webpack compiled successfully
- ✅ No errors in logs
- ✅ App loads at http://localhost:3000
- ✅ LocationSwitcher visible (after login)

**Database:**
- ✅ Database system ready
- ✅ New tables created
- ✅ Connections working

---

## 🎊 You're Ready!

After successful rebuild:
1. ✅ All new features are deployed
2. ✅ Multi-location system active
3. ✅ Translations available
4. �� Ready for testing

**Next:** Follow `START_TESTING_NOW.md` to test everything!

---

## 📞 Quick Reference

**Stop:** `docker-compose down`  
**Build:** `docker-compose build --no-cache`  
**Start:** `docker-compose up -d`  
**Logs:** `docker-compose logs -f`  
**Status:** `docker-compose ps`  
**Restart:** `docker-compose restart [service]`  

**One-liner rebuild:**
```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

---

**Ready to rebuild? Copy the commands above! 🚀**
