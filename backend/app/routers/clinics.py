from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from app.core.database import db
from app.api import deps

router = APIRouter(prefix="/api/clinics", tags=["clinics"])
logger = logging.getLogger(__name__)


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    working_hours: Optional[dict] = None
    settings: Optional[dict] = None


class ReviewCreate(BaseModel):
    clinic_id: str
    rating: int
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    response: str


@router.get("")
async def get_clinics():
    clinics = await db.clinics.find({}, {"_id": 0}).to_list(length=100)
    return clinics


@router.get("/{clinic_id}")
async def get_clinic(clinic_id: str):
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.put("/{clinic_id}")
async def update_clinic(clinic_id: str, data: ClinicUpdate, request: Request):
    user = await deps.require_clinic_admin(request)
    if user.get("clinic_id") != clinic_id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    new_name = update_data.get('name', clinic.get('name') if clinic else None)
    new_address = update_data.get('address', clinic.get('address') if clinic else None)
    if new_name and new_address:
        update_data['is_profile_complete'] = True

    await db.clinics.update_one({"clinic_id": clinic_id}, {"$set": update_data})
    updated = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    return updated


@router.get("/{clinic_id}/reviews")
async def get_clinic_reviews(clinic_id: str):
    reviews = await db.reviews.find({"clinic_id": clinic_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return reviews


@router.post("/{clinic_id}/reviews")
async def create_review(clinic_id: str, data: ReviewCreate, request: Request):
    user = await deps.require_auth(request)

    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    existing_review = await db.reviews.find_one({
        "clinic_id": clinic_id,
        "user_id": user["user_id"],
    }, {"_id": 0})
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this clinic")

    review = {
        "review_id": f"rev_{datetime.now(timezone.utc).timestamp()}",
        "clinic_id": clinic_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", "User"),
        "rating": data.rating,
        "comment": data.comment,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.reviews.insert_one(review)
    review.pop("_id", None)
    return review


@router.post("/{clinic_id}/reviews/{review_id}/respond")
async def respond_to_review(clinic_id: str, review_id: str, data: ReviewResponse, request: Request):
    user = await deps.require_clinic_admin(request)
    if user.get("clinic_id") != clinic_id:
        raise HTTPException(status_code=403, detail="You can only respond to reviews for your clinic")

    review = await db.reviews.find_one({"review_id": review_id, "clinic_id": clinic_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    clinic_name = clinic.get('name', 'Medical Center') if clinic else 'Medical Center'

    formatted_response = f"{clinic_name} thank you for your comment"
    if data.response and data.response.strip():
        formatted_response = data.response.strip()

    await db.reviews.update_one(
        {"review_id": review_id},
        {"$set": {
            "admin_response": formatted_response,
            "admin_response_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    updated = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    return updated


@router.get("/{clinic_id}/stats")
async def get_clinic_stats(clinic_id: str):
    pipeline = [
        {"$match": {"clinic_id": clinic_id}},
        {"$group": {"_id": None, "average_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}}
    ]
    result = await db.reviews.aggregate(pipeline).to_list(1)
    if result:
        return {
            "average_rating": round(result[0]["average_rating"], 1),
            "review_count": result[0]["review_count"]
        }
    return {"average_rating": 0, "review_count": 0}
