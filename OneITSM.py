import os
import asyncio
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

itname = os.getenv("IT_NAME")
itpass = os.getenv("PRD_PASS")
itsmurl = os.getenv("ONE_ITSM")
webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

# Proxy for corporate network
PROXY = {
    "server": "http://mmoproxy.mdv.mmo.de:8080",
    "bypass": "localhost,127.0.0.1"
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("OneITSM_monitor.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = None
        try:
            # Launch Microsoft Edge
            browser = await p.chromium.launch(
                executable_path=edge_path,
                headless=False
            )
            logging.info("Browser launched.")

            # Create a new browser context with proxy and locale
            context = await browser.new_context(
                locale='en-US',
                proxy=PROXY
            )
            page = await context.new_page()

            logging.info(f"Navigating to OneITSM: {itsmurl}")
            await page.goto(itsmurl, wait_until="networkidle")

            # Fill in email
            await page.get_by_role("textbox", name="Email, phone, or Skype").click()
            await page.get_by_role("textbox", name="Email, phone, or Skype").fill(itname)
            await page.get_by_role("button", name="Next").click()

            # Fill in password
            await page.get_by_role("textbox", name="Enter the password for").click()
            await page.get_by_role("textbox", name="Enter the password for").fill(itpass)
            await page.get_by_role("button", name="Sign in").click()

            # Wait for navigation after login
            await page.wait_for_load_state("networkidle")

            # Handle first popup: "No" button
            async with page.expect_popup() as popup1_info:
                await page.get_by_role("button", name="No").click()
            page1 = await popup1_info.value
            await page1.close()

            # Click main link by ID
            await page.locator("#WIN_2_303174300").get_by_role("link").click()

            # Handle second popup: "Assigned To My Selected Groups"
            async with page.expect_popup() as popup2_info:
                await page.get_by_role("cell", name="Assigned To My Selected Groups").click()
            page2 = await popup2_info.value

            # Click "OK" link in the new popup
            await page2.get_by_role("link", name="OK").click()
            await page.pause()

            logging.info("Automation completed successfully.")

        except Exception as e:
            logging.error(f"Error during interaction: {e}")
            await page.pause()  # Pause on error for debugging
        finally:
            if browser:
                await browser.close()


if __name__ == "__main__":
    asyncio.run(main())  # ✅ Correct syntax
