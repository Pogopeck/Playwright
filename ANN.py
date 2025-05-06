import logging
import pyautogui
from playwright.async_api import async_playwright
import os
import asyncio

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
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    combined_cert_path = "D:\\Chandan\\combined_certificates.crt"  # Fixed path with double backslashes

    # Verify Edge and combined certificate exist
    if not os.path.exists(edge_path):
        logger.error(f"Edge browser not found at: {edge_path}")
        return

    if not os.path.exists(combined_cert_path):
        logger.error(f"Combined certificate not found at: {combined_cert_path}")
        return

    logger.info("Setting up environment variables")
    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path

    async with async_playwright() as p:
        try:
            logger.info("Launching browser")
            browser = await p.chromium.launch(
                executable_path=edge_path,
                headless=False
            )
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1800, "height": 730})
            logger.info("Browser launched successfully")

            # Set up dialog handler
            page.on("dialog", lambda dialog: dialog.accept())
            logger.info("Dialog handler configured")

            # Navigate to the Cramer
            logger.info("Navigating to Cramer page...")
            await page.goto("https://cramer.vodafone.com:8811/")
            await asyncio.sleep(2)

            logger.info("Clicking navigation elements")
            await page.click("#headline-start > h1:nth-child(3) > a")
            await asyncio.sleep(2)
            await page.click("#headline-start > a:nth-child(3)")

            logger.info("Waiting for login form")
            await asyncio.sleep(2)

            logger.info("Entering login credentials")
            # Note: pyautogui doesn't have async support, but we'll keep it for now
            pyautogui.typewrite('chandan.sahoo1@vodafone.com', interval=0.1)
            pyautogui.press('tab')
            pyautogui.typewrite('Cursor@SQL!23456', interval=0.1)
            pyautogui.press("enter")

            logger.info("Login submitted, waiting for page load")
            await asyncio.sleep(5)

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
                    iframe = await page.wait_for_selector('iframe[id="7frame"]', state='visible', timeout=5000)
                    if iframe:
                        logger.info("Found iframe with id '7frame'")

                        # Get frame by URL pattern
                        target_frame = page.frame_locator('iframe[id="7frame"]')
                        logger.info("Successfully located frame using frame_locator")

                        # Try to evaluate if frame is accessible
                        try:
                            frame_content = await target_frame.locator('body').count()
                            logger.info(f"Frame content accessible. Found {frame_content} body elements")

                            # Try to locate and click the Device within the frame
                            try:
                                # Wait for frame content to load
                                await asyncio.sleep(2)  # Give extra time for frame content to load

                                device_button = target_frame.get_by_role("button", name="Device")
                                await device_button.click()
                                logger.info("Clicked 'Device' button successfully")
                                await asyncio.sleep(5)
                                search_input = target_frame.locator('#ann-search-criteria-input-name')
                                await search_input.wait_for(state='visible', timeout=5000)
                                await search_input.fill('B001')
                                await search_input.press('Enter')
                                logger.info("Successfully entered 'B001' in search field and pressed Enter")
                                await page.get_by_text("empty frame").content_frame.locator(
                                    ".jqx-grid-cell-all-amdocs-search-not-selected").first.click()
                                await page.get_by_text("empty frame").content_frame.locator(
                                    "[id=\"\\39 51\"]").get_by_role("img").click()
                                await page.get_by_text("empty frame").content_frame.get_by_role("menuitem",
                                                                                                name="Logical Device Reporter").click()
                                await asyncio.sleep(5)
                                await page.screenshot(path="LDR.png")
                                await page.get_by_text("empty frame").content_frame.locator(
                                    "#wizard-title-icons div").nth(2).click()
                                await page.get_by_text("empty frame").content_frame.locator(
                                    "#wizard-title-icons div").nth(3).click()
                                await page.get_by_text("empty frame").content_frame.get_by_role("button",
                                                                                                name="Location").click()
                                await asyncio.sleep(2)
                                await page.get_by_text("Logout").click()
                                await asyncio.sleep(2)
                            except Exception as e:
                                logger.error(f"Failed to interact with ann-search-16x16-icon-black: {str(e)}")

                                # Additional debugging information
                                logger.info("Attempting to list available elements in frame...")
                                html_content = await target_frame.locator('body').inner_html()
                                logger.info(f"Frame HTML content: {html_content[:1000]}...")  # Log first 1000 chars

                        except Exception as e:
                            logger.error(f"Cannot access frame content: {str(e)}")

                except Exception as e:
                    logger.error(f"Error while finding iframe: {str(e)}")

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
