"""
Appointment Reminder Service

This service handles automatic appointment reminders:
- 24 hours before appointment
- 1 hour before appointment
- Custom reminder times based on user preferences

Run this as a background task or scheduled job.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import logging

from ..db import db
from ..schemas.notification import (
    Notification,
    NotificationType,
    NotificationPriority
)
from .email import send_appointment_reminder_email

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing appointment reminders"""
    
    @staticmethod
    async def get_user_preferences(user_id: str) -> Dict:
        """Get user's notification preferences"""
        prefs = await db.notification_preferences.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not prefs:
            # Return default preferences
            return {
                "email_enabled": True,
                "email_appointment_reminders": True,
                "push_enabled": True,
                "push_appointment_reminders": True,
                "sms_enabled": False,
                "sms_appointment_reminders": False,
                "reminder_24h_before": True,
                "reminder_1h_before": True,
                "quiet_hours_enabled": False
            }
        
        return prefs
    
    @staticmethod
    async def is_in_quiet_hours(user_id: str) -> bool:
        """Check if current time is in user's quiet hours"""
        prefs = await ReminderService.get_user_preferences(user_id)
        
        if not prefs.get("quiet_hours_enabled", False):
            return False
        
        now = datetime.now(timezone.utc)
        current_time = now.strftime("%H:%M")
        
        start = prefs.get("quiet_hours_start", "22:00")
        end = prefs.get("quiet_hours_end", "08:00")
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            return current_time >= start or current_time <= end
        else:
            return start <= current_time <= end
    
    @staticmethod
    async def create_notification(
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        appointment_id: str = None,
        priority: str = NotificationPriority.MEDIUM,
        metadata: Dict = None
    ) -> Notification:
        """Create a notification in the database"""
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            appointment_id=appointment_id,
            priority=priority,
            metadata=metadata or {}
        )
        
        doc = notification.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc.get('scheduled_for'):
            doc['scheduled_for'] = doc['scheduled_for'].isoformat()
        if doc.get('read_at'):
            doc['read_at'] = doc['read_at'].isoformat()
        if doc.get('sent_at'):
            doc['sent_at'] = doc['sent_at'].isoformat()
        
        await db.notifications.insert_one(doc)
        
        return notification
    
    @staticmethod
    async def send_reminder(
        appointment: Dict,
        reminder_type: str,
        hours_before: int
    ):
        """Send a reminder for an appointment"""
        
        user_id = appointment.get("patient_id")
        appointment_id = appointment.get("appointment_id")
        
        # Check user preferences
        prefs = await ReminderService.get_user_preferences(user_id)
        
        # Check if reminders are enabled
        if not prefs.get("email_appointment_reminders", True):
            logger.info(f"Reminders disabled for user {user_id}")
            return
        
        # Check quiet hours
        if await ReminderService.is_in_quiet_hours(user_id):
            logger.info(f"User {user_id} is in quiet hours, skipping reminder")
            return
        
        # Check if reminder already sent
        existing = await db.notifications.find_one({
            "user_id": user_id,
            "appointment_id": appointment_id,
            "type": reminder_type
        })
        
        if existing:
            logger.info(f"Reminder already sent for appointment {appointment_id}")
            return
        
        # Get appointment details
        doctor = await db.doctors.find_one(
            {"doctor_id": appointment.get("doctor_id")},
            {"_id": 0}
        )
        
        clinic = await db.clinics.find_one(
            {"clinic_id": appointment.get("clinic_id")},
            {"_id": 0}
        )
        
        doctor_name = doctor.get("name", "Unknown") if doctor else "Unknown"
        clinic_name = clinic.get("name", "Unknown") if clinic else "Unknown"
        clinic_address = clinic.get("address", "") if clinic else ""
        
        appointment_date = appointment.get("date_time")
        
        # Create notification title and message
        if hours_before == 24:
            title = "Reminder: Appointment Tomorrow"
            message = f"You have an appointment with Dr. {doctor_name} tomorrow at {clinic_name}."
        elif hours_before == 1:
            title = "Reminder: Appointment in 1 Hour"
            message = f"Your appointment with Dr. {doctor_name} is in 1 hour at {clinic_name}."
        else:
            title = f"Reminder: Appointment in {hours_before} Hours"
            message = f"You have an appointment with Dr. {doctor_name} in {hours_before} hours at {clinic_name}."
        
        # Create in-app notification
        await ReminderService.create_notification(
            user_id=user_id,
            notification_type=reminder_type,
            title=title,
            message=message,
            appointment_id=appointment_id,
            priority=NotificationPriority.HIGH if hours_before == 1 else NotificationPriority.MEDIUM,
            metadata={
                "doctor_name": doctor_name,
                "clinic_name": clinic_name,
                "appointment_date": appointment_date,
                "hours_before": hours_before
            }
        )
        
        # Send email if enabled
        if prefs.get("email_enabled", True) and prefs.get("email_appointment_reminders", True):
            try:
                send_appointment_reminder_email(
                    patient_email=appointment.get("patient_email", ""),
                    patient_name=appointment.get("patient_name", ""),
                    doctor_name=doctor_name,
                    clinic_name=clinic_name,
                    appointment_date=appointment_date,
                    appointment_id=appointment_id,
                    clinic_address=clinic_address,
                    hours_before=hours_before
                )
                
                # Mark notification as sent via email
                await db.notifications.update_one(
                    {
                        "user_id": user_id,
                        "appointment_id": appointment_id,
                        "type": reminder_type
                    },
                    {
                        "$set": {
                            "sent_email": True,
                            "sent_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                logger.info(f"Reminder email sent for appointment {appointment_id}")
            except Exception as e:
                logger.error(f"Failed to send reminder email: {str(e)}")
        
        # TODO: Send push notification if enabled
        # TODO: Send SMS if enabled
    
    @staticmethod
    async def process_24h_reminders():
        """Process reminders for appointments 24 hours from now"""
        
        logger.info("Processing 24-hour reminders...")
        
        # Calculate time window (24 hours from now, +/- 5 minutes)
        now = datetime.now(timezone.utc)
        target_time = now + timedelta(hours=24)
        start_window = target_time - timedelta(minutes=5)
        end_window = target_time + timedelta(minutes=5)
        
        # Find appointments in the time window
        appointments = await db.appointments.find({
            "date_time": {
                "$gte": start_window.isoformat(),
                "$lte": end_window.isoformat()
            },
            "status": {"$in": ["SCHEDULED", "CONFIRMED"]}
        }, {"_id": 0}).to_list(1000)
        
        logger.info(f"Found {len(appointments)} appointments for 24h reminders")
        
        # Send reminders
        for appointment in appointments:
            try:
                await ReminderService.send_reminder(
                    appointment=appointment,
                    reminder_type=NotificationType.APPOINTMENT_REMINDER_24H,
                    hours_before=24
                )
            except Exception as e:
                logger.error(f"Failed to send 24h reminder for appointment {appointment.get('appointment_id')}: {str(e)}")
        
        logger.info(f"Processed {len(appointments)} 24-hour reminders")
    
    @staticmethod
    async def process_1h_reminders():
        """Process reminders for appointments 1 hour from now"""
        
        logger.info("Processing 1-hour reminders...")
        
        # Calculate time window (1 hour from now, +/- 2 minutes)
        now = datetime.now(timezone.utc)
        target_time = now + timedelta(hours=1)
        start_window = target_time - timedelta(minutes=2)
        end_window = target_time + timedelta(minutes=2)
        
        # Find appointments in the time window
        appointments = await db.appointments.find({
            "date_time": {
                "$gte": start_window.isoformat(),
                "$lte": end_window.isoformat()
            },
            "status": {"$in": ["SCHEDULED", "CONFIRMED"]}
        }, {"_id": 0}).to_list(1000)
        
        logger.info(f"Found {len(appointments)} appointments for 1h reminders")
        
        # Send reminders
        for appointment in appointments:
            try:
                await ReminderService.send_reminder(
                    appointment=appointment,
                    reminder_type=NotificationType.APPOINTMENT_REMINDER_1H,
                    hours_before=1
                )
            except Exception as e:
                logger.error(f"Failed to send 1h reminder for appointment {appointment.get('appointment_id')}: {str(e)}")
        
        logger.info(f"Processed {len(appointments)} 1-hour reminders")
    
    @staticmethod
    async def run_reminder_check():
        """Run both reminder checks"""
        try:
            await ReminderService.process_24h_reminders()
            await ReminderService.process_1h_reminders()
        except Exception as e:
            logger.error(f"Error in reminder check: {str(e)}")


# Standalone function for running as a scheduled task
async def check_and_send_reminders():
    """Main function to check and send reminders"""
    await ReminderService.run_reminder_check()


if __name__ == "__main__":
    # For testing purposes
    asyncio.run(check_and_send_reminders())
