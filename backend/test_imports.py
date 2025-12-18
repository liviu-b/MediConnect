#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import os
import sys

# Set required environment variables for testing
os.environ['MONGO_URL'] = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
os.environ['DB_NAME'] = os.getenv('DB_NAME', 'mediconnect_test')
os.environ['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
os.environ['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:3000')

print("🔧 Testing MediConnect Backend Imports...")
print(f"   MONGO_URL: {os.environ['MONGO_URL']}")
print(f"   DB_NAME: {os.environ['DB_NAME']}")
print(f"   CORS_ORIGINS: {os.environ['CORS_ORIGINS']}")
print()

try:
    # Test config
    print("📦 Importing config...")
    from app.config import MONGO_URL, DB_NAME, CORS_ORIGINS
    print(f"   ✅ Config loaded successfully")
    print(f"      - Database: {DB_NAME}")
    print(f"      - CORS: {CORS_ORIGINS}")
    print()
    
    # Test schemas
    print("📦 Importing schemas...")
    from app.schemas.organization import Organization, OrganizationRegistration
    from app.schemas.location import Location, LocationCreate
    from app.schemas.access_request import AccessRequest
    from app.schemas.user import User
    from app.schemas.staff import StaffMember
    print("   ✅ All schemas imported successfully")
    print()
    
    # Test routers
    print("📦 Importing routers...")
    from app.routers.organizations import router as org_router
    from app.routers.locations import router as loc_router
    from app.routers.access_requests import router as req_router
    print("   ✅ All new routers imported successfully")
    print()
    
    # Test main app
    print("📦 Importing main app...")
    from app.main import app
    print("   ✅ FastAPI app created successfully")
    print()
    
    # List all routes
    print("📋 Available API Routes:")
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            routes.append(f"   {methods:20} {route.path}")
    
    # Filter and show new routes
    new_routes = [r for r in routes if any(x in r for x in ['/organizations', '/locations', '/access-requests'])]
    if new_routes:
        print("\n🆕 New Multi-Location Routes:")
        for route in sorted(new_routes):
            print(route)
    
    print("\n" + "="*60)
    print("✅ ALL IMPORTS SUCCESSFUL!")
    print("="*60)
    print("\n🎉 Backend is ready for multi-location support!")
    print("\n📝 Next steps:")
    print("   1. Run migration: python migrate_to_organizations.py")
    print("   2. Start server: python server.py")
    print("   3. Test endpoints with curl or Postman")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Import failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
