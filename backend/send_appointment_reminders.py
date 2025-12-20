"""
Appointment Reminder Script
Sends email reminders 24 hours before scheduled appointments.

This script should be run daily (e.g., via Windows Task Scheduler or cron).
It finds all appointments scheduled for tomorrow and sends reminder emails to patients.

Usage:
    python send_appointment_reminders.py
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import db
from app.services.email import send_appointment_reminder_email
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("reminder_script")


async def send_reminders():
    """
    Find appointments scheduled for tomorrow and send reminder emails.
    """
    try:
        # Calculate tomorrow's date range (24 hours from now)
        now = datetime.now(timezone.utc)
        tomorrow_start = now + timedelta(hours=23)  # 23 hours from now
        tomorrow_end = now + timedelta(hours=25)    # 25 hours from now
        
        logger.info(f"Searching for appointments between {tomorrow_start} and {tomorrow_end}")
        
        # Find appointments scheduled for tomorrow that are confirmed or scheduled
        query = {
            "date_time": {
                "$gte": tomorrow_start.isoformat(),
                "$lte": tomorrow_end.isoformat()
            },
            "status": {"$in": ["SCHEDULED", "CONFIRMED"]}
        }
        
        appointments = await db.appointments.find(query, {"_id": 0}).to_list(1000)
        
        if not appointments:
            logger.info("No appointments found for tomorrow. No reminders to send.")
            return
        
        logger.info(f"Found {len(appointments)} appointments for tomorrow")
        
        # Send reminder for each appointment
        sent_count = 0
        failed_count = 0
        
        for appointment in appointments:
            try:
                # Get patient email
                patient_email = appointment.get("patient_email")
                patient_name = appointment.get("patient_name", "Patient")
                
                if not patient_email:
                    # Try to get email from user collection
                    patient = await db.users.find_one(
                        {"user_id": appointment["patient_id"]},
                        {"_id": 0, "email": 1, "name": 1}
                    )
                    if patient:
                        patient_email = patient.get("email")
                        patient_name = patient.get("name", patient_name)
                
                if not patient_email:
                    logger.warning(f"No email found for appointment {appointment['appointment_id']}")
                    failed_count += 1
                    continue
                
                # Get doctor info
                doctor = await db.doctors.find_one(
                    {"doctor_id": appointment["doctor_id"]},
                    {"_id": 0, "name": 1}
                )
                doctor_name = doctor.get("name", "Unknown") if doctor else "Unknown"
                
                # Get clinic info
                clinic = await db.clinics.find_one(
                    {"clinic_id": appointment["clinic_id"]},
                    {"_id": 0, "name": 1, "address": 1}
                )
                clinic_name = clinic.get("name", "Unknown") if clinic else "Unknown"
                clinic_address = clinic.get("address") if clinic else None
                
                # Send reminder email
                result = send_appointment_reminder_email(
                    patient_email=patient_email,
                    patient_name=patient_name,
                    doctor_name=doctor_name,
                    clinic_name=clinic_name,
                    appointment_date=appointment["date_time"],
                    clinic_address=clinic_address
                )
                
                if result.get("success"):
                    logger.info(f"✅ Reminder sent to {patient_email} for appointment {appointment['appointment_id']}")
                    sent_count += 1
                else:
                    logger.error(f"❌ Failed to send reminder to {patient_email}: {result.get('error')}")
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing appointment {appointment.get('appointment_id')}: {str(e)}")
                failed_count += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"REMINDER SUMMARY:")
        logger.info(f"  Total appointments found: {len(appointments)}")
        logger.info(f"  Reminders sent successfully: {sent_count}")
        logger.info(f"  Failed to send: {failed_count}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Fatal error in send_reminders: {str(e)}", exc_info=True)
        raise


async def main():
    """
    Main entry point for the reminder script.
    """
    logger.info("=" * 60)
    logger.info("APPOINTMENT REMINDER SCRIPT STARTED")
    logger.info("=" * 60)
    
    try:
        await send_reminders()
        logger.info("✅ Reminder script completed successfully")
        return 0
    except Exception as e:
        logger.error(f"❌ Reminder script failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
