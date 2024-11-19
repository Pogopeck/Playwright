# tests/test_sanity.py
import pytest
from playwright.sync_api import expect

class TestSanity:
    def test_login(self, page, config, helpers, logger):
        try:
            # Navigate to application
            page.goto(config.BASE_URL)
            logger.info(f"Navigated to {config.BASE_URL}")

            # Login flow
            helpers.safe_fill("#username", config.TEST_USER)
            helpers.safe_fill("#password", config.TEST_PASSWORD)
            helpers.safe_click("#login-button")

            # Verify login success
            expect(page.locator(".dashboard")).to_be_visible()
            logger.info("Login successful")

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            helpers.take_screenshot("login_failure")
            raise

    def test_navigation(self, page, config, helpers, logger):
        try:
            # Navigate to main page
            page.goto(f"{config.BASE_URL}/dashboard")
            
            # Test navigation elements
            nav_items = [
                ("Products", ".products-list"),
                ("Orders", ".orders-table"),
                ("Settings", ".settings-panel")
            ]
            
            for nav_name, expected_element in nav_items:
                helpers.safe_click(f"text={nav_name}")
                expect(page.locator(expected_element)).to_be_visible()
                logger.info(f"Successfully navigated to {nav_name}")

        except Exception as e:
            logger.error(f"Navigation test failed: {str(e)}")
            helpers.take_screenshot("navigation_failure")
            raise
