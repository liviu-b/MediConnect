"""Migration script to add multilingual fields to existing services."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mediconnect_db")


async def migrate_services():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("Starting service migration...")
    
    services = await db.services.find({
        "$or": [
            {"name_en": {"$exists": False}},
            {"name_ro": {"$exists": False}}
        ]
    }).to_list(None)
    
    print(f"Found {len(services)} services to migrate")
    
    for service in services:
        service_id = service.get("service_id")
        name = service.get("name", "")
        description = service.get("description", "")
        
        update_data = {}
        
        if "name_en" not in service:
            update_data["name_en"] = name
        if "name_ro" not in service:
            update_data["name_ro"] = name
        if "description_en" not in service and description:
            update_data["description_en"] = description
        if "description_ro" not in service and description:
            update_data["description_ro"] = description
        
        if update_data:
            await db.services.update_one(
                {"service_id": service_id},
                {"$set": update_data}
            )
            print(f"✓ Migrated service: {name} (ID: {service_id})")
    
    print(f"\n✅ Migration complete! {len(services)} services updated.")
    print("\nNote: All services now have both EN and RO fields with the same content.")
    print("Admins should edit services to provide proper translations for each language.")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_services())
