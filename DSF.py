import os
import asyncio
import re
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()
sname = os.getenv("IT_NAME")
spass = os.getenv("PRD_PASS")
dsfurl = os.getenv("PRD_URL")

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    combined_cert_path = "D:\\Chandan\\combined_certificates.crt"  # Not used but kept for reference

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False,
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        # Navigate to DSF URL
        await page.goto(dsfurl)

        # Login flow
        await page.get_by_role("link", name="Login with SSO").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").fill(sname)
        await page.get_by_role("button", name="Next").click()
        await page.get_by_role("textbox", name="Enter the password for").click()
        await page.get_by_role("textbox", name="Enter the password for").fill(spass)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="No").click()

        print("✅  IT Admin - URL accessibility is working")

        # Handle popup window
        async with page.expect_popup() as page1_info:
            await page.get_by_role("button", name="Click to trigger the search").click()
        page1 = await page1_info.value

        # Interact with popup page
        locator = page1.locator('[data-test-id="202006091432210525478"] [data-test-id="2016122110475608391271"]')
        await locator.click()
        await locator.fill("dsf-*")
        await locator.press("Enter")

        result_count_locator = page1.locator("text=500 results")

        # Wait until it's visible (with timeout)
        try:
            await result_count_locator.wait_for(state="visible", timeout=10000)
            result_text = await result_count_locator.text_content()
            assert result_text == "500 results", f"Expected '500 results', but got '{result_text}'"
            print("✅  Global Search is working")
        except Exception as e:
            print(f"❌ Global Search assertion failed: {e}")
            raise
        await page1.get_by_role("link", name="DSF Workbasket").click()
        await page1.get_by_text("IT Operations WB").click()
        logging.info("Waiting for IT Operations WB element...")
        await page.wait_for_selector("#ITOperationsWB", timeout=20000)
        logging.info("Found IT Operations WB element")

        # Get count from second <td> in the same row
        count_locator = page.locator("tr:has(#ITOperationsWB) > td:nth-child(2)")
        await count_locator.wait_for(timeout=10000)
        count_text = await count_locator.inner_text()
        count = int(count_text.strip()) if count_text.strip().isdigit() else 0
        logging.info(f"IT Operations WB Count: {count}")

        # Navigate in popup
        await page1.get_by_role("link", name="Old Administration").click()
        await page1.locator("#EXPAND-PLUSMINUS > #RULE_KEY").first.click()
        await page1.locator("[data-test-id=\"202103040611470626102\"]").click()
        await page1.get_by_role("cell", name="No items").locator("div").nth(3).click()

        # Pause for manual inspection (REMOVE IN PRODUCTION)
        await page.pause()

        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
