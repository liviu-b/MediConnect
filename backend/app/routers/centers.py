from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..db import db
from ..schemas.center import MedicalCenterCreate, MedicalCenterUpdate, MedicalCenterResponse
import re

router = APIRouter(prefix="/centers", tags=["centers"])


@router.get("")
async def get_centers(
    search_term: Optional[str] = Query(None, description="Search by name or description"),
    county_filter: Optional[str] = Query(None, description="Filter by county (use 'all' for national search)"),
    city_filter: Optional[str] = Query(None, description="Filter by city within county")
):
    """
    Get medical centers (clinics) with optional filtering by search term, county, and city.
    
    - If county_filter is 'all' or empty: search nationally
    - If county_filter is specified: filter by that county
    - If city_filter is also specified: filter by both county and city
    - search_term matches against name or description (case-insensitive)
    """
    # Build the query filter
    query_filter = {}
    
    # Handle search term (case-insensitive regex for name or description)
    if search_term and search_term.strip():
        search_pattern = re.escape(search_term.strip())
        query_filter["$or"] = [
            {"name": {"$regex": search_pattern, "$options": "i"}},
            {"description": {"$regex": search_pattern, "$options": "i"}}
        ]
    
    # Handle county filter
    if county_filter and county_filter.strip() and county_filter.lower() != "all":
        # Exact match for county (case-insensitive)
        query_filter["county"] = {"$regex": f"^{re.escape(county_filter.strip())}$", "$options": "i"}
    
    # Handle city filter (only if county is also specified or if searching all)
    if city_filter and city_filter.strip() and city_filter.lower() != "all":
        # Exact match for city (case-insensitive)
        query_filter["city"] = {"$regex": f"^{re.escape(city_filter.strip())}$", "$options": "i"}
    
    # Execute query on clinics collection
    centers = await db.clinics.find(query_filter, {"_id": 0}).to_list(length=1000)
    
    return {
        "count": len(centers),
        "county_filter": county_filter if county_filter and county_filter.lower() != "all" else "all",
        "city_filter": city_filter if city_filter and city_filter.lower() != "all" else "all",
        "search_term": search_term,
        "results": centers
    }


@router.get("/{center_id}")
async def get_center(center_id: str):
    """Get a specific medical center by ID"""
    center = await db.medical_centers.find_one({"center_id": center_id}, {"_id": 0})
    if not center:
        raise HTTPException(status_code=404, detail="Medical center not found")
    return center


@router.post("")
async def create_center(center: MedicalCenterCreate):
    """Create a new medical center"""
    from ..schemas.center import MedicalCenter
    
    # Create center with generated ID
    center_data = MedicalCenter(**center.model_dump())
    
    # Insert into database
    await db.medical_centers.insert_one(center_data.model_dump())
    
    # Return created center
    created = await db.medical_centers.find_one({"center_id": center_data.center_id}, {"_id": 0})
    return created


@router.put("/{center_id}")
async def update_center(center_id: str, data: MedicalCenterUpdate):
    """Update a medical center"""
    # Check if center exists
    center = await db.medical_centers.find_one({"center_id": center_id})
    if not center:
        raise HTTPException(status_code=404, detail="Medical center not found")
    
    # Build update data (only include fields that were provided)
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Update the center
    await db.medical_centers.update_one({"center_id": center_id}, {"$set": update_data})
    
    # Return updated center
    updated = await db.medical_centers.find_one({"center_id": center_id}, {"_id": 0})
    return updated


@router.delete("/{center_id}")
async def delete_center(center_id: str):
    """Delete a medical center"""
    result = await db.medical_centers.delete_one({"center_id": center_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Medical center not found")
    
    return {"message": "Medical center deleted successfully"}


@router.get("/cities/list")
async def get_cities():
    """Get a list of all unique cities from medical centers"""
    cities = await db.medical_centers.distinct("city")
    return {"cities": sorted(cities)}
