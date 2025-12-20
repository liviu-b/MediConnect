"""
Clear Database Script
Deletes all users, staff, doctors, appointments, and related data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URL, DB_NAME

async def clear_database():
    """Clear all data from the database"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🗑️  Starting database cleanup...")
    print(f"Database: {DB_NAME}")
    print("-" * 50)
    
    # Collections to clear - EVERYTHING
    collections_to_clear = [
        'users',
        'staff',
        'doctors',
        'appointments',
        'prescriptions',
        'medical_records',
        'sessions',
        'audit_logs',
        'notifications',
        'organizations',
        'locations', 
        'clinics',
        'services',
        'permissions',
        'reviews',
        'access_requests'
    ]
    
    total_deleted = 0
    
    for collection_name in collections_to_clear:
        try:
            collection = db[collection_name]
            count = await collection.count_documents({})
            if count > 0:
                result = await collection.delete_many({})
                print(f"✅ Deleted {result.deleted_count} documents from '{collection_name}'")
                total_deleted += result.deleted_count
            else:
                print(f"⚪ Collection '{collection_name}' is already empty")
        except Exception as e:
            print(f"❌ Error clearing '{collection_name}': {e}")
    
    print("-" * 50)
    print(f"🎉 Database cleanup complete!")
    print(f"📊 Total documents deleted: {total_deleted}")
    print()
    print("💥 ALL DATA HAS BEEN DELETED!")
    print("   The database is now completely empty.")
    
    client.close()

if __name__ == "__main__":
    print()
    print("=" * 50)
    print("  DATABASE CLEANUP SCRIPT - FULL WIPE")
    print("=" * 50)
    print()
    print("⚠️  WARNING: This will delete EVERYTHING:")
    print("   - Users, Staff, Doctors")
    print("   - Appointments, Prescriptions, Medical Records")
    print("   - Organizations, Locations, Clinics")
    print("   - Services, Permissions")
    print("   - Audit Logs, Sessions, Notifications")
    print("   - Reviews, Access Requests")
    print()
    print("💥 THE DATABASE WILL BE COMPLETELY EMPTY!")
    print()
    
    confirm = input("Type 'YES' to confirm FULL deletion: ")
    
    if confirm == "YES":
        print()
        asyncio.run(clear_database())
        print()
        print("✨ You can now register new users and start fresh!")
        print()
    else:
        print()
        print("❌ Cleanup cancelled. No data was deleted.")
        print()
