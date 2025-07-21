import os
import asyncio
from playwright.async_api import async_playwright

async def main():
    #os.environ["DEBUG"] = "pw:api"
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False
        )

        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to Microsoft Apps sign-in page
        await page.goto("https://myapps.microsoft.com/signin/78f5464b-e016-4fdb-9478-ba285b87fb8e?tenantId=68283f3b-8487-4c86-adb3-a5228f18b893")
        await page.wait_for_load_state('networkidle')

        # Enter email
        await page.get_by_role("textbox", name="Geben Sie Ihre E-Mail-Adresse").click()
        await page.get_by_role("textbox", name="Geben Sie Ihre E-Mail-Adresse").fill("chandan.sahoo1@vodafone.com")
        await page.get_by_role("button", name="Weiter", exact=True).click()

        # Enter password
        await page.get_by_role("textbox", name="Geben Sie das Kennwort für \"").click()
        await page.get_by_role("textbox", name="Geben Sie das Kennwort für \"").fill("HEllo")
        await page.get_by_role("button", name="Anmelden").click()

        # Handle additional prompts
        await page.get_by_role("button", name="Nein").click()
        await page.locator("[id=\"1\"]").get_by_role("radio", name="ReadOnly").check()
        await page.get_by_role("link", name="Melden Sie sich an").click()
        await page.get_by_role("button", name="Alle Cookies akzeptieren").click()

        # === SANITY CHECK: Validate 5 Running EC2 Instances ===

        # Use Concierge search to go to EC2
        await page.get_by_test_id("awsc-concierge-input").fill("EC2")
        await page.get_by_test_id("services-search-result-link-ec2").click()

        # Wait for navigation to EC2 dashboard
        await page.wait_for_url("**/ec2/home**")

        # Wait for the iframe to be visible
        await page.locator("iframe[title='Dashboard']").wait_for(state="visible", timeout=10000)

        # Now target the iframe that contains the EC2 dashboard
        iframe = page.frame_locator("iframe[title='Dashboard']")

        # Click on "Instances (running)" link inside the iframe
        await iframe.get_by_role("link", name="Instances (ausgeführt)").click()
        #await page.pause()
        # Wait for instance table to load
        #page.locator("iframe[title=\"Instances\"]").content_frame.get_by_text("(5)").click()

        # Wait for the iframe to be visible
        await page.locator("iframe[title='Instances']").wait_for(state="visible", timeout=10000)

        # Access the iframe
        frame_locator = page.frame_locator("iframe[title='Instances']")

        # Locate the element with text "(5)"
        count_element = frame_locator.get_by_text("(5)")

        # Get the text content
        text = await count_element.text_content()

        # Check if it matches "(5)"
        if text and text.strip() == "(5)":
            print("✅ Found exactly 5 instances.")
        else:
            print(f"❌ Expected '(5)', but found: {text}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
