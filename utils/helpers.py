# utils/helpers.py
from playwright.sync_api import expect
import time
from config.config import TestConfig
from utils.logger import TestLogger

class TestHelpers:
    def __init__(self, page):
        self.page = page
        self.logger = TestLogger().logger
        self.config = TestConfig()

    async def safe_click(self, selector, timeout=None):
        timeout = timeout or self.config.DEFAULT_TIMEOUT
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.click(selector)
            self.logger.info(f"Clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {str(e)}")
            raise

    async def safe_fill(self, selector, text, timeout=None):
        timeout = timeout or self.config.DEFAULT_TIMEOUT
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.fill(selector, text)
            self.logger.info(f"Filled text in element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to fill text in element {selector}: {str(e)}")
            raise

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{self.config.SCREENSHOT_DIR}/{name}_{timestamp}.png"
        self.page.screenshot(path=filename)
        self.logger.info(f"Screenshot saved: {filename}")
        return filename
