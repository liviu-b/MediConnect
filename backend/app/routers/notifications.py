from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
from datetime import datetime, timezone

from ..db import db
from ..schemas.notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate,
    NotificationPreferences,
    NotificationPreferencesUpdate,
    NotificationStats,
    NotificationType,
    NotificationPriority
)
from ..security import require_auth

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=List[Notification])
async def get_my_notifications(
    request: Request,
    unread_only: bool = False,
    limit: int = 50,
    skip: int = 0
):
    """Get current user's notifications"""
    user = await require_auth(request)
    
    query = {"user_id": user.user_id}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return notifications


@router.get("/me/stats", response_model=NotificationStats)
async def get_notification_stats(request: Request):
    """Get notification statistics for current user"""
    user = await require_auth(request)
    
    # Get all notifications
    all_notifications = await db.notifications.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).to_list(1000)
    
    # Calculate stats
    total = len(all_notifications)
    unread = sum(1 for n in all_notifications if not n.get("is_read", False))
    read = total - unread
    
    # Group by type
    by_type = {}
    for n in all_notifications:
        n_type = n.get("type", "UNKNOWN")
        by_type[n_type] = by_type.get(n_type, 0) + 1
    
    # Group by priority
    by_priority = {}
    for n in all_notifications:
        priority = n.get("priority", NotificationPriority.MEDIUM)
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    return NotificationStats(
        total_notifications=total,
        unread_count=unread,
        read_count=read,
        by_type=by_type,
        by_priority=by_priority
    )


@router.put("/{notification_id}")
async def update_notification(
    notification_id: str,
    data: NotificationUpdate,
    request: Request
):
    """Update notification (mark as read/unread)"""
    user = await require_auth(request)
    
    # Check if notification belongs to user
    notification = await db.notifications.find_one(
        {"notification_id": notification_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # If marking as read, set read_at timestamp
    if update_data.get("is_read") is True and not notification.get("is_read"):
        update_data["read_at"] = datetime.now(timezone.utc).isoformat()
    
    # If marking as unread, clear read_at
    if update_data.get("is_read") is False:
        update_data["read_at"] = None
    
    await db.notifications.update_one(
        {"notification_id": notification_id},
        {"$set": update_data}
    )
    
    updated = await db.notifications.find_one(
        {"notification_id": notification_id},
        {"_id": 0}
    )
    
    return updated


@router.post("/mark-all-read")
async def mark_all_notifications_read(request: Request):
    """Mark all notifications as read for current user"""
    user = await require_auth(request)
    
    result = await db.notifications.update_many(
        {"user_id": user.user_id, "is_read": False},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "All notifications marked as read",
        "updated_count": result.modified_count
    }


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, request: Request):
    """Delete a notification"""
    user = await require_auth(request)
    
    # Check if notification belongs to user
    notification = await db.notifications.find_one(
        {"notification_id": notification_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.notifications.delete_one({"notification_id": notification_id})
    
    return {"message": "Notification deleted successfully"}


@router.delete("/clear-all")
async def clear_all_notifications(request: Request):
    """Clear all notifications for current user"""
    user = await require_auth(request)
    
    result = await db.notifications.delete_many({"user_id": user.user_id})
    
    return {
        "message": "All notifications cleared",
        "deleted_count": result.deleted_count
    }


# ============= NOTIFICATION PREFERENCES =============

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(request: Request):
    """Get user's notification preferences"""
    user = await require_auth(request)
    
    preferences = await db.notification_preferences.find_one(
        {"user_id": user.user_id},
        {"_id": 0}
    )
    
    if not preferences:
        # Create default preferences
        default_prefs = NotificationPreferences(user_id=user.user_id)
        await db.notification_preferences.insert_one(default_prefs.model_dump())
        return default_prefs
    
    return preferences


@router.put("/preferences")
async def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    request: Request
):
    """Update user's notification preferences"""
    user = await require_auth(request)
    
    # Check if preferences exist
    existing = await db.notification_preferences.find_one(
        {"user_id": user.user_id},
        {"_id": 0}
    )
    
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    if not existing:
        # Create new preferences
        new_prefs = NotificationPreferences(user_id=user.user_id, **update_data)
        await db.notification_preferences.insert_one(new_prefs.model_dump())
        return new_prefs
    else:
        # Update existing preferences
        await db.notification_preferences.update_one(
            {"user_id": user.user_id},
            {"$set": update_data}
        )
        
        updated = await db.notification_preferences.find_one(
            {"user_id": user.user_id},
            {"_id": 0}
        )
        return updated


# ============= ADMIN ENDPOINTS =============

@router.post("/send", response_model=Notification)
async def create_notification(data: NotificationCreate, request: Request):
    """
    Create and send a notification (Admin/System use)
    This is typically called by the system, not directly by users
    """
    user = await require_auth(request)
    
    # Only staff can create notifications for other users
    if user.role not in ["SUPER_ADMIN", "LOCATION_ADMIN", "RECEPTIONIST", "DOCTOR"]:
        if data.user_id != user.user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only create notifications for yourself"
            )
    
    # Validate notification type
    if data.type not in NotificationType.ALL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification type. Must be one of: {', '.join(NotificationType.ALL_TYPES)}"
        )
    
    # Create notification
    notification = Notification(**data.model_dump())
    
    # Convert datetime fields to ISO format
    doc = notification.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('scheduled_for'):
        doc['scheduled_for'] = doc['scheduled_for'].isoformat()
    if doc.get('read_at'):
        doc['read_at'] = doc['read_at'].isoformat()
    if doc.get('sent_at'):
        doc['sent_at'] = doc['sent_at'].isoformat()
    
    await db.notifications.insert_one(doc)
    
    # TODO: Send actual notification via email/push/sms based on user preferences
    # This will be handled by the notification service
    
    return notification
