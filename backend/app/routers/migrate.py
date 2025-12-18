"""
Migration endpoint for database updates.
This should be protected and only accessible by admins.
"""

from fastapi import APIRouter, Request, HTTPException
from ..db import db
from ..security import require_clinic_admin

router = APIRouter(prefix="/migrate", tags=["migration"])


@router.post("/services-multilingual")
async def migrate_services_multilingual(request: Request):
    """
    Migrate existing services to support multilingual names.
    Copies existing 'name' and 'description' to both EN and RO fields.
    """
    # Require admin authentication
    user = await require_clinic_admin(request)
    
    # Find all services that don't have multilingual fields
    services = await db.services.find({
        "$or": [
            {"name_en": {"$exists": False}},
            {"name_ro": {"$exists": False}}
        ]
    }).to_list(None)
    
    migrated_count = 0
    
    for service in services:
        service_id = service.get("service_id")
        name = service.get("name", "")
        description = service.get("description", "")
        
        # Update with multilingual fields
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
            migrated_count += 1
    
    return {
        "message": "Migration completed successfully",
        "services_migrated": migrated_count,
        "note": "All services now have both EN and RO fields. Please edit services to provide proper translations."
    }
