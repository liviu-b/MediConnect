"""
Migration script to convert existing clinics to the new Organization/Location model.

This script:
1. Creates an Organization for each existing Clinic (using CUI)
2. Converts each Clinic to a Location
3. Updates Users to link to Organizations instead of Clinics
4. Updates Staff to link to Organizations
5. Preserves all existing data and relationships

Run this script ONCE before deploying the new multi-location feature.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "mediconnect")

async def migrate():
    print("🚀 Starting migration to Organization/Location model...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Step 1: Get all existing clinics
        clinics = await db.clinics.find({}, {"_id": 0}).to_list(1000)
        print(f"📋 Found {len(clinics)} clinics to migrate")
        
        if len(clinics) == 0:
            print("✅ No clinics to migrate. Database is ready for new model.")
            return
        
        # Step 2: Create Organizations and Locations
        organizations_created = 0
        locations_created = 0
        
        for clinic in clinics:
            clinic_id = clinic['clinic_id']
            cui = clinic['cui']
            
            print(f"\n📍 Processing clinic: {clinic.get('name', clinic_id)}")
            
            # Check if organization already exists for this CUI
            existing_org = await db.organizations.find_one({"cui": cui})
            
            if existing_org:
                organization_id = existing_org['organization_id']
                print(f"   ℹ️  Organization already exists: {organization_id}")
            else:
                # Create new organization from clinic data
                organization_id = f"org_{clinic_id.replace('clinic_', '')}"
                
                # Find the admin user for this clinic to set as super admin
                admin_user = await db.users.find_one(
                    {"clinic_id": clinic_id, "role": "CLINIC_ADMIN"},
                    {"_id": 0}
                )
                
                super_admin_ids = [admin_user['user_id']] if admin_user else []
                
                organization = {
                    "organization_id": organization_id,
                    "cui": cui,
                    "name": clinic.get('name', f"Organization {cui}"),
                    "legal_name": clinic.get('name'),
                    "phone": clinic.get('phone'),
                    "email": clinic.get('email'),
                    "description": clinic.get('description'),
                    "logo_url": clinic.get('logo_url'),
                    "super_admin_ids": super_admin_ids,
                    "settings": {
                        "allow_multi_location_booking": True,
                        "centralized_billing": False,
                        "shared_patient_records": True
                    },
                    "is_active": True,
                    "is_verified": clinic.get('is_verified', True),
                    "created_at": clinic.get('created_at', datetime.now(timezone.utc).isoformat())
                }
                
                await db.organizations.insert_one(organization)
                organizations_created += 1
                print(f"   ✅ Created organization: {organization_id}")
            
            # Create location from clinic
            location_id = f"loc_{clinic_id.replace('clinic_', '')}"
            
            # Check if location already exists
            existing_location = await db.locations.find_one({"location_id": location_id})
            
            if not existing_location:
                location = {
                    "location_id": location_id,
                    "organization_id": organization_id,
                    "name": clinic.get('name', f"Location {clinic.get('city', 'Main')}"),
                    "address": clinic.get('address'),
                    "city": clinic.get('city'),
                    "county": clinic.get('county'),
                    "phone": clinic.get('phone'),
                    "email": clinic.get('email'),
                    "description": clinic.get('description'),
                    "working_hours": clinic.get('working_hours', {
                        "monday": {"start": "09:00", "end": "17:00"},
                        "tuesday": {"start": "09:00", "end": "17:00"},
                        "wednesday": {"start": "09:00", "end": "17:00"},
                        "thursday": {"start": "09:00", "end": "17:00"},
                        "friday": {"start": "09:00", "end": "17:00"},
                        "saturday": {"start": "10:00", "end": "14:00"},
                        "sunday": None
                    }),
                    "settings": clinic.get('settings', {
                        "allow_online_booking": True,
                        "booking_advance_days": 30,
                        "cancellation_hours": 24,
                        "reminder_hours": 24
                    }),
                    "is_active": True,
                    "is_primary": True,  # First location is primary
                    "created_at": clinic.get('created_at', datetime.now(timezone.utc).isoformat())
                }
                
                await db.locations.insert_one(location)
                locations_created += 1
                print(f"   ✅ Created location: {location_id}")
            else:
                print(f"   ℹ️  Location already exists: {location_id}")
            
            # Update users linked to this clinic
            users_updated = await db.users.update_many(
                {"clinic_id": clinic_id},
                {"$set": {
                    "organization_id": organization_id,
                    "assigned_location_ids": None  # Full access to all locations
                }}
            )
            
            # Update CLINIC_ADMIN role to SUPER_ADMIN
            await db.users.update_many(
                {"clinic_id": clinic_id, "role": "CLINIC_ADMIN"},
                {"$set": {"role": "SUPER_ADMIN"}}
            )
            
            print(f"   ✅ Updated {users_updated.modified_count} users")
            
            # Update staff linked to this clinic
            staff_updated = await db.staff.update_many(
                {"clinic_id": clinic_id},
                {"$set": {
                    "organization_id": organization_id,
                    "assigned_location_ids": None  # Full access to all locations
                }}
            )
            
            print(f"   ✅ Updated {staff_updated.modified_count} staff members")
        
        print(f"\n" + "="*60)
        print(f"✅ Migration completed successfully!")
        print(f"   📊 Organizations created: {organizations_created}")
        print(f"   📊 Locations created: {locations_created}")
        print(f"   📊 Total clinics processed: {len(clinics)}")
        print(f"="*60)
        
        # Step 3: Create indexes for new collections
        print("\n📑 Creating indexes...")
        
        await db.organizations.create_index("cui", unique=True)
        await db.organizations.create_index("organization_id", unique=True)
        print("   ✅ Organizations indexes created")
        
        await db.locations.create_index("location_id", unique=True)
        await db.locations.create_index("organization_id")
        print("   ✅ Locations indexes created")
        
        await db.access_requests.create_index("request_id", unique=True)
        await db.access_requests.create_index("organization_id")
        await db.access_requests.create_index("status")
        print("   ✅ Access requests indexes created")
        
        print("\n✅ All done! Your database is now ready for multi-location support.")
        print("\n⚠️  Note: Old 'clinics' collection is preserved for backup.")
        print("   You can safely delete it after verifying everything works correctly.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
