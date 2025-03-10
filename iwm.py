import logging
import os
import asyncio
from playwright.async_api import async_playwright
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pytest
from PIL import Image
import sys
from io import StringIO
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Constants
SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPECTED_FILES = ['homepage.png', 'new_project.png']


def validate_environment():
    """Validate all required environment variables are set"""
    required_vars = [
        'CRAMER_USERNAME',
        'CRAMER_PASSWORD',
        'SMTP_SERVER',
        'SMTP_SENDER',
        'SMTP_RECEIVER',
        'CHROME_PATH',
        'CERT_PATH'
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True


class TestResults:
    def __init__(self):
        self.output = StringIO()
        self.test_passed = False


def run_screenshot_tests():
    """Run pytest tests and capture the output"""
    test_results = TestResults()

    class Plugin:
        def pytest_runtest_logreport(self, report):
            if report.when == 'call':
                test_results.output.write(f"\n{report.nodeid}: {report.outcome}\n")
                if report.outcome == "failed":
                    test_results.output.write(f"    {report.longrepr}\n")

    # Define test functions
    def test_screenshot_files_exist():
        for filename in EXPECTED_FILES:
            file_path = os.path.join(SCREENSHOT_DIR, filename)
            assert os.path.exists(file_path), f"Screenshot {filename} does not exist"

    def test_screenshot_files_not_empty():
        for filename in EXPECTED_FILES:
            file_path = os.path.join(SCREENSHOT_DIR, filename)
            file_size = os.path.getsize(file_path)
            assert file_size > 0, f"Screenshot {filename} is empty"

    def test_screenshot_files_are_valid_images():
        for filename in EXPECTED_FILES:
            file_path = os.path.join(SCREENSHOT_DIR, filename)
            try:
                with Image.open(file_path) as img:
                    assert img.format == "PNG", f"{filename} is not a PNG file"
                    width, height = img.size
                    assert width > 0 and height > 0, f"{filename} has invalid dimensions"
            except Exception as e:
                pytest.fail(f"Failed to open {filename} as an image: {str(e)}")

    pytest.main(["-v", "--tb=short"], plugins=[Plugin()])
    return test_results.output.getvalue()


async def send_email_with_screenshots_and_test_results(test_results):
    """Send an email with attached screenshots and test results."""
    try:
        smtp_server = os.environ['SMTP_SERVER']
        sender_email = os.environ['SMTP_SENDER']
        receiver_email = os.environ['SMTP_RECEIVER']
        subject = f"Automation Screenshots and Test Results - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = "Automation Test Results:\n\n"
        body += test_results
        body += "\n\nPlease find attached screenshots from the automation run."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach screenshots
        for screenshot in EXPECTED_FILES:
            file_path = os.path.join(SCREENSHOT_DIR, screenshot)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data, name=os.path.basename(file_path))
                    msg.attach(image)
                    logger.info(f"Attached {screenshot} to email")
            else:
                logger.warning(f"Screenshot {screenshot} not found")

        # Send the email with TLS
        with smtplib.SMTP(smtp_server) as server:
            server.starttls()
            server.send_message(msg)
            logger.info("Email sent successfully with test results")

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")


async def main():
    """Main function to execute the automation."""
    if not validate_environment():
        logger.error("Environment validation failed")
        return

    chrome_path = os.environ['CHROME_PATH']
    combined_cert_path = os.environ['CERT_PATH']

    # Verify Chrome and certificate exist
    if not os.path.exists(chrome_path):
        logger.error(f"Chrome browser not found at: {chrome_path}")
        return

    if not os.path.exists(combined_cert_path):
        logger.error(f"Combined certificate not found at: {combined_cert_path}")
        return

    logger.info("Setting up environment variables")
    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path

    try:
        async with async_playwright() as p:
            logger.info("Launching browser")
            browser = await p.chromium.launch(
                executable_path=chrome_path,
                headless=False
            )

            page = await browser.new_page()
            logger.info("Browser launched successfully")

            # Set up dialog handler
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            logger.info("Dialog handler configured")

            # Navigate to the Cramer page
            logger.info("Navigating to Cramer page...")
            await page.goto("http://cramerstart.vodafone.com:8670/AmdocsOSS/Portal/index.html")
            await asyncio.sleep(3)

            # Handle login with environment variables
            await page.keyboard.type(os.environ['CRAMER_USERNAME'])
            await page.keyboard.press('Tab')
            await page.keyboard.type(os.environ['CRAMER_PASSWORD'])
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)
            await page.screenshot(path="homepage.png")
            logger.info("Took homepage screenshot")

            # Wait for and interact with the outer container
            try:
                outer_container = await page.wait_for_selector(
                    '#portal-outer-container',
                    state='visible',
                    timeout=5000
                )
                logger.info("Outer container found")
                await page.reload()
                await page.wait_for_load_state('networkidle')
                logger.info("Page loaded completely")
                await asyncio.sleep(4)

                # Debug iframe presence and loading
                logger.info("Starting iframe debugging...")

                # Get all frames and log their URLs
                frames = page.frames
                logger.info(f"Total frames found: {len(frames)}")
                for frame in frames:
                    logger.info(f"Frame URL: {frame.url}")
                    logger.info(f"Frame name: {frame.name}")

                # Wait for network to be idle
                logger.info("Waiting for network to become idle...")
                await page.wait_for_load_state('networkidle')
                logger.info("Network is idle")

                # Try different approaches to locate the iframe
                try:
                    # Using attribute selector instead of id
                    iframe = await page.wait_for_selector('iframe[id="2frame"]', state='visible', timeout=5000)
                    if iframe:
                        logger.info("Found iframe with id '2frame'")

                        # Get frame by URL pattern
                        target_frame = page.frame_locator('iframe[id="2frame"]')
                        logger.info("Successfully located frame using frame_locator")

                        # Try to evaluate if frame is accessible
                        try:
                            frame_content = await target_frame.locator('body').count()
                            logger.info(f"Frame content accessible. Found {frame_content} body elements")

                            # Try to locate and click the create-project-icon within the frame
                            try:
                                # Wait for frame content to load
                                await asyncio.sleep(2)  # Give extra time for frame content to load

                                create_project_button = target_frame.locator('.create-project-icon')
                                await create_project_button.wait_for(state='visible', timeout=10000)
                                await create_project_button.click()
                                logger.info("Clicked 'Create New Project' button successfully")
                                await asyncio.sleep(5)
                                await page.screenshot(path="new_project1.png")
                                calender_button = target_frame.locator('.subElementHolder.plannedCompletionDateField')
                                await calender_button.click()
                                logger.info("Clicked 'Calender' button successfully")
                                await page.screenshot(path="calender.png")
                                await asyncio.sleep(5)

                            except Exception as e:
                                logger.error(f"Failed to interact with create-project-icon: {str(e)}")

                                # Additional debugging information
                                logger.info("Attempting to list available elements in frame...")
                                html_content = await target_frame.locator('body').inner_html()
                                logger.info(f"Frame HTML content: {html_content[:1000]}...")  # Log first 1000 chars

                        except Exception as e:
                            logger.error(f"Cannot access frame content: {str(e)}")

                except Exception as e:
                    logger.error(f"Error while finding iframe: {str(e)}")

                    # Alternative approach using URL
                    logger.info("Attempting alternative approach using frame URL...")
                    try:
                        for frame in frames:
                            if "cramerstart.vodafone.com:8670" in frame.url:
                                logger.info(f"Found matching frame with URL: {frame.url}")
                                target_frame = page.frame_locator(f'iframe[src="{frame.url}"]')
                                logger.info("Successfully located frame using URL")
                                break
                    except Exception as e:
                        logger.error(f"Alternative approach failed: {str(e)}")

                # Take a debug screenshot
                await page.screenshot(path="new_project.png")
                logger.info("Took new_project icon screenshot")

                # After taking screenshots, run tests and send email
                logger.info("Running screenshot tests...")
                test_results = run_screenshot_tests()

                # Send email with both screenshots and test results
                await send_email_with_screenshots_and_test_results(test_results)

            except Exception as e:
                logger.error(f"Error occurred: {str(e)}", exc_info=True)
            finally:
                if 'browser' in locals():
                    logger.info("Closing browser")
                    await browser.close()
                    logger.info("Browser closed successfully")
    except Exception as e:
        logger.error(f"Outer error occurred: {str(e)}", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting automation script")
    asyncio.run(main())
    logger.info("Script execution completed")
