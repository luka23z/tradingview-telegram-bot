import schedule
import time
import logging
from tv_screenshot import capture_and_send_screenshot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("Running scheduled screenshot job...")
    capture_and_send_screenshot()
    logger.info("Screenshot job completed.")

# Schedule jobs for 2:00 AM and 2:00 PM CEST
schedule.every().day.at("02:00").do(job)
schedule.every().day.at("14:00").do(job)

logger.info("Scheduler started. Jobs scheduled for 2:00 AM and 2:00 PM CEST daily.")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
