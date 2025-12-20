"""
Appointment Reminder Scheduler

This script runs continuously and checks for appointments that need reminders.
It should be run as a background service or scheduled task.

Usage:
    python run_reminders.py

The script will:
- Check every 5 minutes for appointments needing reminders
- Send 24-hour reminders
- Send 1-hour reminders
- Respect user notification preferences
- Log all activities
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.reminder_service import ReminderService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reminders.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def run_reminder_loop():
    """Main loop that checks for reminders every 5 minutes"""
    
    logger.info("=" * 60)
    logger.info("🔔 Appointment Reminder Service Started")
    logger.info("=" * 60)
    logger.info("Checking for reminders every 5 minutes...")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"⏰ [{current_time}] Checking for appointments needing reminders...")
            
            # Run reminder checks
            await ReminderService.run_reminder_check()
            
            logger.info(f"✅ Reminder check completed. Next check in 5 minutes.")
            logger.info("-" * 60)
            
            # Wait 5 minutes before next check
            await asyncio.sleep(300)  # 300 seconds = 5 minutes
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Reminder service stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in reminder loop: {str(e)}", exc_info=True)
            logger.info("⏳ Waiting 1 minute before retry...")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


async def run_once():
    """Run reminder check once (useful for testing or cron jobs)"""
    logger.info("🔔 Running one-time reminder check...")
    try:
        await ReminderService.run_reminder_check()
        logger.info("✅ Reminder check completed successfully")
    except Exception as e:
        logger.error(f"❌ Error in reminder check: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Check if running in "once" mode (for cron jobs)
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        asyncio.run(run_once())
    else:
        # Run continuous loop
        try:
            asyncio.run(run_reminder_loop())
        except KeyboardInterrupt:
            logger.info("\n👋 Goodbye!")
