from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from ..db import db
from ..schemas.review import Review, ReviewCreate, ReviewResponse
from ..security import require_auth, require_clinic_admin

router = APIRouter(prefix="/clinics/{clinic_id}/reviews", tags=["reviews"])


@router.get("")
async def get_clinic_reviews(clinic_id: str):
    reviews = await db.reviews.find({"clinic_id": clinic_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return reviews


@router.post("")
async def create_review(clinic_id: str, data: ReviewCreate, request: Request):
    user = await require_auth(request)
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    existing_review = await db.reviews.find_one({"clinic_id": clinic_id, "user_id": user.user_id}, {"_id": 0})
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this clinic")
    review = Review(clinic_id=clinic_id, user_id=user.user_id, user_name=user.name, rating=data.rating, comment=data.comment)
    doc = review.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.reviews.insert_one(doc)
    return review


@router.post("/{review_id}/respond")
async def respond_to_review(clinic_id: str, review_id: str, data: ReviewResponse, request: Request):
    user = await require_clinic_admin(request)
    if user.clinic_id != clinic_id:
        raise HTTPException(status_code=403, detail="You can only respond to reviews for your clinic")
    review = await db.reviews.find_one({"review_id": review_id, "clinic_id": clinic_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    clinic = await db.clinics.find_one({"clinic_id": clinic_id}, {"_id": 0})
    clinic_name = clinic.get('name', 'Medical Center') if clinic else 'Medical Center'
    formatted_response = data.response.strip() if data.response and data.response.strip() else f"{clinic_name} thank you for your comment"
    await db.reviews.update_one({"review_id": review_id}, {"$set": {
        "admin_response": formatted_response,
        "admin_response_at": datetime.now(timezone.utc).isoformat()
    }})
    updated_review = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    return updated_review
