import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from plyer import notification  # ✅ Added import

# Load environment variables from .env file
load_dotenv()
sname = os.getenv("IT_NAME")
spass = os.getenv("PRD_PASS")
dsfurl = os.getenv("PRD_URL")

async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        # Navigate to DSF URL
        await page.goto(dsfurl)

        # Login flow
        await page.get_by_role("link", name="Login with SSO").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").fill(sname)
        await page.get_by_role("button", name="Next").click()
        await page.get_by_role("textbox", name="Enter the password for").fill(spass)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="No").click()

        # Wait for the workbasket element to appear
        await page.wait_for_selector("#ITOperationsWB", timeout=20000)
        print("✅  Found IT Operations WB element")

        # Locate the count (second <td> in the same row)
        count_locator = page.locator("tr:has(#ITOperationsWB) > td:nth-child(2)")

        # Wait for the element to be visible
        await count_locator.first.wait_for(timeout=10000)

        # Get the text
        count_text = await count_locator.first.inner_text()
        count = int(count_text.strip()) if count_text.strip().isdigit() else 0

        print(f"📊 IT Operations WB Count: {count}")

        # 🧪 TEMPORARY: Force alert to test desktop notification
        if count > 0 or True:  # 🔥 Remove 'or True' after testing
            notification.notify(
                title="🚨 TEST: DSF Monitor Active",
                message=f"Test alert! Current count: {count}\nDesktop notifications are working.",
                app_name="DSF Monitor",
                timeout=10
            )

        await page.pause()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
