import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_and_send_screenshot(chart_url=None):
    """Capture TradingView chart screenshot and send to Telegram"""
    
    logger.info("=" * 50)
    logger.info("Starting TradingView screenshot capture job")
    logger.info("=" * 50)
    
    if chart_url is None:
        chart_url = os.getenv('TRADINGVIEW_CHART_URL')
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not all([chart_url, bot_token, chat_id]):
        logger.error("Missing required environment variables")
        return
    
    driver = None
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')  # Consistent window size
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize WebDriver
        logger.info("====== WebDriver manager ======")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Browser initialized successfully")
        
        # Navigate to TradingView
        logger.info(f"Navigating to: {chart_url}")
        driver.get(chart_url)
        
        # Wait for the page to load (40 seconds)
        logger.info("Waiting for chart to fully load (40 seconds)...")
        time.sleep(40)  # Wait 40 seconds for chart and indicators to render
        
        # Hide sidebars and panels using JavaScript
        logger.info("Hiding sidebars and extra panels...")
        hide_elements_script = """
        // Hide left sidebar
        var leftPanel = document.querySelector('div[data-name="left-toolbar"]');
        if (leftPanel) leftPanel.style.display = 'none';
        
        // Hide right sidebar
        var rightPanel = document.querySelector('div.widgetbar-widgetbar');
        if (rightPanel) rightPanel.style.display = 'none';
        
        // Hide top header
        var header = document.querySelector('div.header-chart-panel');
        if (header) header.style.display = 'none';
        
        // Hide bottom time bar
        var timeBar = document.querySelector('div.chart-controls-bar');
        if (timeBar) timeBar.style.display = 'none';
        
        // Hide legend sidebar (watchlist)
        var legend = document.querySelector('div.widgetbar-pages');
        if (legend) legend.style.display = 'none';
        
        // Make chart container full width
        var chartContainer = document.querySelector('div.chart-container');
        if (chartContainer) {
            chartContainer.style.left = '0';
            chartContainer.style.right = '0';
            chartContainer.style.width = '100%';
        }
        """
        
        driver.execute_script(hide_elements_script)
        logger.info("Sidebars hidden, waiting for layout adjustment...")
        time.sleep(2)  # Wait for layout to adjust
        
        # Take screenshot
        logger.info("Taking screenshot...")
        screenshot = driver.get_screenshot_as_png()
        
        # Send to Telegram
        logger.info("Sending screenshot to Telegram...")
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        files = {'photo': ('chart.png', screenshot, 'image/png')}
        data = {
            'chat_id': chat_id, 
            'caption': f'📊 TradingView Chart - {time.strftime("%Y-%m-%d %H:%M CEST")}'
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            logger.info("Screenshot sent to Telegram successfully!")
        else:
            logger.error(f"Failed to send screenshot: {response.text}")
            
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    capture_and_send_screenshot()
