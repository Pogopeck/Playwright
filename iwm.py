import logging
import os
import asyncio
from playwright.async_api import async_playwright

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


async def main():
    chrome_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\chrome-win\\chrome.exe"
    combined_cert_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\cramer_combine.crt"

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

            # Handle login
            await page.keyboard.type('hp_som_int_iwm')
            await page.keyboard.press('Tab')
            await page.keyboard.type('Welcome1')
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

            except Exception as e:
                logger.error(f"Error while interacting with outer container: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)

    finally:
        if 'browser' in locals():
            logger.info("Closing browser")
            await browser.close()
            logger.info("Browser closed successfully")


if __name__ == "__main__":
    logger.info("Starting automation script")
    asyncio.run(main())
    logger.info("Script execution completed")
