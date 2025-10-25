import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TRADINGVIEW_CHART_URL = os.getenv('TRADINGVIEW_CHART_URL')
SCREENSHOT_DIR = 'screenshots'
LOG_DIR = 'logs'

# Create directories if they don't exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingViewScreenshotBot:
    def __init__(self):
        """Initialize the bot with Selenium and Telegram configurations"""
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chart_url = TRADINGVIEW_CHART_URL
        self.screenshot_path = None
        
    def setup_browser(self):
        """Configure and return a headless Chrome browser"""
        chrome_options = Options()
        
        # Headless mode (no GUI)
        chrome_options.add_argument('--headless=new')
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Set window size for consistent screenshots
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Disable notifications
        chrome_options.add_argument('--disable-notifications')
        
        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Browser initialized successfully")
        return driver
    
    def capture_tradingview_chart(self):
        """Navigate to TradingView and capture screenshot"""
        driver = None
        try:
            driver = self.setup_browser()
            logger.info(f"Navigating to: {self.chart_url}")
            
            # Load TradingView chart
            driver.get(self.chart_url)
            
            # Wait for chart to load
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'canvas')))
            
            # Additional wait to ensure chart is fully rendered
            time.sleep(5)
            
            logger.info("Chart loaded successfully")
            
            # Generate timestamp-based filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.screenshot_path = f'{SCREENSHOT_DIR}/tv_chart_{timestamp}.png'
            
            # Take screenshot
            driver.save_screenshot(self.screenshot_path)
            logger.info(f"Screenshot saved: {self.screenshot_path}")
            
            # Optional: Optimize image size
            self._optimize_image()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            return False
            
        finally:
            if driver:
                driver.quit()
                logger.info("Browser closed")
    
    def _optimize_image(self):
        """Compress image to reduce file size for Telegram"""
        try:
            img = Image.open(self.screenshot_path)
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Save with optimization
            img.save(self.screenshot_path, 'PNG', optimize=True, quality=85)
            logger.info("Image optimized")
            
        except Exception as e:
            logger.warning(f"Image optimization failed: {str(e)}")
    
    def send_to_telegram(self, caption=None):
        """Send screenshot to Telegram chat"""
        try:
            if not self.screenshot_path or not os.path.exists(self.screenshot_path):
                logger.error("Screenshot file not found")
                return False
            
            # Generate caption
            if caption is None:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                caption = f"📊 TradingView Chart Update\n🕒 {current_time}"
            
            # Send photo to Telegram
            with open(self.screenshot_path, 'rb') as photo_file:
                self.bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=photo_file,
                    caption=caption
                )
            
            logger.info(f"Screenshot sent to Telegram chat: {TELEGRAM_CHAT_ID}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send to Telegram: {str(e)}")
            return False
    
    def cleanup_old_screenshots(self, keep_last=5):
        """Remove old screenshots to save disk space"""
        try:
            files = sorted(
                [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png')],
                key=lambda x: os.path.getmtime(os.path.join(SCREENSHOT_DIR, x)),
                reverse=True
            )
            
            # Delete all except the most recent 'keep_last' files
            for file in files[keep_last:]:
                file_path = os.path.join(SCREENSHOT_DIR, file)
                os.remove(file_path)
                logger.info(f"Deleted old screenshot: {file}")
                
        except Exception as e:
            logger.warning(f"Cleanup failed: {str(e)}")
    
    def run(self):
        """Main execution method"""
        logger.info("=" * 50)
        logger.info("Starting TradingView screenshot capture job")
        logger.info("=" * 50)
        
        try:
            # Step 1: Capture screenshot
            if not self.capture_tradingview_chart():
                logger.error("Screenshot capture failed. Aborting.")
                return False
            
            # Step 2: Send to Telegram
            if not self.send_to_telegram():
                logger.error("Failed to send to Telegram")
                return False
            
            # Step 3: Cleanup
            self.cleanup_old_screenshots(keep_last=5)
            
            logger.info("Job completed successfully ✓")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False


def main():
    """Entry point for the script"""
    bot = TradingViewScreenshotBot()
    bot.run()


if __name__ == "__main__":
    main()
