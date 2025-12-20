from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone

from ..db import db
from ..schemas.health_stats import (
    VitalSign,
    VitalSignCreate,
    LabResult,
    LabResultCreate,
    LabResultUpdate,
    HealthStats
)
from ..security import require_auth

router = APIRouter(prefix="/health", tags=["health-stats"])


# ==================== VITAL SIGNS ====================

@router.get("/vitals", response_model=List[VitalSign])
async def get_vital_signs(
    request: Request,
    type: Optional[str] = None,
    limit: int = 50
):
    """Get user's vital signs"""
    user = await require_auth(request)
    
    query = {"user_id": user.user_id}
    if type:
        query["type"] = type
    
    vitals = await db.vital_signs.find(
        query,
        {"_id": 0}
    ).sort("measured_at", -1).limit(limit).to_list(limit)
    
    return vitals


@router.post("/vitals", response_model=VitalSign)
async def add_vital_sign(data: VitalSignCreate, request: Request):
    """Add a vital sign measurement"""
    user = await require_auth(request)
    
    vital = VitalSign(
        user_id=user.user_id,
        type=data.type,
        value=data.value,
        value_secondary=data.value_secondary,
        unit=data.unit,
        notes=data.notes,
        measured_by="self",
        measured_at=data.measured_at or datetime.now(timezone.utc)
    )
    
    doc = vital.model_dump()
    doc['measured_at'] = doc['measured_at'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.vital_signs.insert_one(doc)
    
    return vital


@router.delete("/vitals/{measurement_id}")
async def delete_vital_sign(measurement_id: str, request: Request):
    """Delete a vital sign measurement"""
    user = await require_auth(request)
    
    result = await db.vital_signs.delete_one({
        "measurement_id": measurement_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    return {"message": "Measurement deleted"}


# ==================== LAB RESULTS ====================

@router.get("/lab-results", response_model=List[LabResult])
async def get_lab_results(
    request: Request,
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get user's lab results"""
    user = await require_auth(request)
    
    query = {"user_id": user.user_id}
    if status:
        query["status"] = status
    if category:
        query["test_category"] = category
    
    results = await db.lab_results.find(
        query,
        {"_id": 0}
    ).sort("test_date", -1).limit(limit).to_list(limit)
    
    return results


@router.post("/lab-results", response_model=LabResult)
async def add_lab_result(data: LabResultCreate, request: Request):
    """Add a lab result (doctors only)"""
    user = await require_auth(request)
    
    # Check if user is a doctor
    if user.role not in ['DOCTOR', 'CLINIC_ADMIN']:
        raise HTTPException(status_code=403, detail="Only doctors can add lab results")
    
    # Get patient_id from request or use current user
    # For now, doctors add results for their patients
    # You might want to add a patient_id parameter
    
    result = LabResult(
        user_id=user.user_id,  # This should be patient_id in real scenario
        test_name=data.test_name,
        test_category=data.test_category,
        result_value=data.result_value,
        result_unit=data.result_unit,
        reference_range=data.reference_range,
        status=data.status,
        file_url=data.file_url,
        file_type=data.file_type,
        notes=data.notes,
        interpretation=data.interpretation,
        ordered_by=user.user_id,
        ordered_by_name=user.name,
        lab_name=data.lab_name,
        test_date=data.test_date,
        result_date=data.result_date
    )
    
    doc = result.model_dump()
    doc['test_date'] = doc['test_date'].isoformat()
    if doc.get('result_date'):
        doc['result_date'] = doc['result_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.lab_results.insert_one(doc)
    
    return result


@router.post("/lab-results/{patient_id}", response_model=LabResult)
async def add_lab_result_for_patient(
    patient_id: str,
    data: LabResultCreate,
    request: Request
):
    """Add a lab result for a specific patient (doctors only)"""
    user = await require_auth(request)
    
    # Check if user is a doctor
    if user.role not in ['DOCTOR', 'CLINIC_ADMIN']:
        raise HTTPException(status_code=403, detail="Only doctors can add lab results")
    
    # Verify patient exists
    patient = await db.users.find_one({"user_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    result = LabResult(
        user_id=patient_id,
        test_name=data.test_name,
        test_category=data.test_category,
        result_value=data.result_value,
        result_unit=data.result_unit,
        reference_range=data.reference_range,
        status=data.status,
        file_url=data.file_url,
        file_type=data.file_type,
        notes=data.notes,
        interpretation=data.interpretation,
        ordered_by=user.user_id,
        ordered_by_name=user.name,
        lab_name=data.lab_name,
        test_date=data.test_date,
        result_date=data.result_date
    )
    
    doc = result.model_dump()
    doc['test_date'] = doc['test_date'].isoformat()
    if doc.get('result_date'):
        doc['result_date'] = doc['result_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.lab_results.insert_one(doc)
    
    return result


@router.put("/lab-results/{result_id}", response_model=LabResult)
async def update_lab_result(
    result_id: str,
    data: LabResultUpdate,
    request: Request
):
    """Update a lab result"""
    user = await require_auth(request)
    
    # Find the result
    result = await db.lab_results.find_one({"result_id": result_id})
    if not result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    
    # Check permissions
    if user.role not in ['DOCTOR', 'CLINIC_ADMIN'] and result['user_id'] != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = data.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    if 'result_date' in update_data and update_data['result_date']:
        update_data['result_date'] = update_data['result_date'].isoformat()
    
    await db.lab_results.update_one(
        {"result_id": result_id},
        {"$set": update_data}
    )
    
    updated = await db.lab_results.find_one({"result_id": result_id}, {"_id": 0})
    return updated


@router.delete("/lab-results/{result_id}")
async def delete_lab_result(result_id: str, request: Request):
    """Delete a lab result"""
    user = await require_auth(request)
    
    # Find the result
    result = await db.lab_results.find_one({"result_id": result_id})
    if not result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    
    # Check permissions
    if user.role not in ['DOCTOR', 'CLINIC_ADMIN'] and result['user_id'] != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.lab_results.delete_one({"result_id": result_id})
    
    return {"message": "Lab result deleted"}


# ==================== HEALTH STATS ====================

@router.get("/stats", response_model=HealthStats)
async def get_health_stats(request: Request):
    """Get user's health statistics summary"""
    user = await require_auth(request)
    
    # Get latest vitals
    latest_bp = await db.vital_signs.find_one(
        {"user_id": user.user_id, "type": "blood_pressure"},
        {"_id": 0}
    ).sort("measured_at", -1)
    
    latest_hr = await db.vital_signs.find_one(
        {"user_id": user.user_id, "type": "heart_rate"},
        {"_id": 0}
    ).sort("measured_at", -1)
    
    latest_temp = await db.vital_signs.find_one(
        {"user_id": user.user_id, "type": "temperature"},
        {"_id": 0}
    ).sort("measured_at", -1)
    
    latest_weight = await db.vital_signs.find_one(
        {"user_id": user.user_id, "type": "weight"},
        {"_id": 0}
    ).sort("measured_at", -1)
    
    latest_height = await db.vital_signs.find_one(
        {"user_id": user.user_id, "type": "height"},
        {"_id": 0}
    ).sort("measured_at", -1)
    
    # Calculate BMI if we have both weight and height
    bmi = None
    if latest_weight and latest_height:
        weight_kg = latest_weight['value']
        height_m = latest_height['value'] / 100  # Convert cm to m
        if height_m > 0:
            bmi = round(weight_kg / (height_m ** 2), 1)
    
    # Count measurements
    total_vitals = await db.vital_signs.count_documents({"user_id": user.user_id})
    total_labs = await db.lab_results.count_documents({"user_id": user.user_id})
    pending_labs = await db.lab_results.count_documents({
        "user_id": user.user_id,
        "status": "PENDING"
    })
    abnormal_labs = await db.lab_results.count_documents({
        "user_id": user.user_id,
        "status": "ABNORMAL"
    })
    
    # Get last measurement dates
    last_vital = await db.vital_signs.find_one(
        {"user_id": user.user_id},
        {"_id": 0, "measured_at": 1}
    ).sort("measured_at", -1)
    
    last_lab = await db.lab_results.find_one(
        {"user_id": user.user_id},
        {"_id": 0, "test_date": 1}
    ).sort("test_date", -1)
    
    return HealthStats(
        user_id=user.user_id,
        latest_blood_pressure=latest_bp,
        latest_heart_rate=latest_hr,
        latest_temperature=latest_temp,
        latest_weight=latest_weight,
        latest_height=latest_height,
        latest_bmi=bmi,
        total_vital_measurements=total_vitals,
        total_lab_results=total_labs,
        pending_lab_results=pending_labs,
        abnormal_lab_results=abnormal_labs,
        last_measurement_date=last_vital.get('measured_at') if last_vital else None,
        last_lab_test_date=last_lab.get('test_date') if last_lab else None
    )


@router.get("/vitals/chart/{type}")
async def get_vitals_chart_data(
    type: str,
    request: Request,
    days: int = 30
):
    """Get vital signs data for charting"""
    user = await require_auth(request)
    
    from datetime import timedelta
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    vitals = await db.vital_signs.find(
        {
            "user_id": user.user_id,
            "type": type,
            "measured_at": {"$gte": start_date.isoformat()}
        },
        {"_id": 0, "measured_at": 1, "value": 1, "value_secondary": 1, "unit": 1}
    ).sort("measured_at", 1).to_list(1000)
    
    return {
        "type": type,
        "data": vitals,
        "count": len(vitals)
    }
