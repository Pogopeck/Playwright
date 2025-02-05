import logging
import pyautogui
import playwright
from playwright.sync_api import sync_playwright
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    chrome_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\chrome-win\\chrome.exe"
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    combined_cert_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\cramer_combine.crt"

    # Verify Chrome and combined certificate exist
    if not os.path.exists(edge_path):
        logger.error(f"Edge browser not found at: {edge_path}")
        return

    if not os.path.exists(combined_cert_path):
        logger.error(f"Combined certificate not found at: {combined_cert_path}")
        return

    logger.info("Setting up environment variables")
    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path

    with sync_playwright() as p:
        try:
            logger.info("Launching browser")
            browser = p.chromium.launch(
                executable_path=edge_path,
                headless=False
            )
            page = browser.new_page()
            logger.info("Browser launched successfully")

            # Set up dialog handler
            page.on("dialog", lambda dialog: dialog.accept())
            logger.info("Dialog handler configured")

            # Navigate to the Cramer
            logger.info("Navigating to Cramer page...")
            page.goto("https://cramer.vodafone.com:8811/")
            time.sleep(2)

            logger.info("Clicking navigation elements")
            page.click("#headline-start > h1:nth-child(3) > a")
            time.sleep(2)
            page.click("#headline-start > a:nth-child(3)")

            logger.info("Waiting for login form")
            time.sleep(2)

            logger.info("Entering login credentials")
            pyautogui.typewrite('chandan.sahoo1@vodafone.com', interval=0.1)
            pyautogui.press('tab')
            pyautogui.typewrite('LaxmiPogo96!234', interval=0.1)
            pyautogui.press("enter")

            logger.info("Login submitted, waiting for page load")
            time.sleep(20)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}", exc_info=True)

        finally:
            if 'browser' in locals():
                logger.info("Closing browser")
                browser.close()
                logger.info("Browser closed successfully")


if __name__ == "__main__":
    logger.info("Starting automation script")
    main()
    logger.info("Script execution completed")
