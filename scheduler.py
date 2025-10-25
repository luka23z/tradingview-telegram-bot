from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from tv_screenshot import TradingViewScreenshotBot
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_screenshot_job():
    """Wrapper function to run the bot"""
    try:
        bot = TradingViewScreenshotBot()
        bot.run()
    except Exception as e:
        logger.error(f"Job execution failed: {str(e)}")

def main():
    scheduler = BlockingScheduler()
    
    # Schedule for 2:00 AM CEST (Stuttgart)
    # 2:00 AM CEST = 00:00 UTC
    scheduler.add_job(
        run_screenshot_job,
        CronTrigger(hour=0, minute=0),
        id='screenshot_2am',
        name='TradingView Screenshot 2AM CEST'
    )
    
    # Schedule for 2:00 PM CEST (Stuttgart)
    # 2:00 PM CEST = 12:00 UTC
    scheduler.add_job(
        run_screenshot_job,
        CronTrigger(hour=12, minute=0),
        id='screenshot_2pm',
        name='TradingView Screenshot 2PM CEST'
    )
    
    logger.info("Scheduler started. Jobs scheduled for 2:00 AM and 2:00 PM CEST daily.")
    logger.info("Press Ctrl+C to exit")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()
