import os
import asyncio
import logging
from playwright.async_api import async_playwright

# === Configure Logging ===
logging.basicConfig(
    filename='dsf_log.txt',  # Log file name
    filemode='a',            # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO       # Log level (can be DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=edge_path, headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        logging.info("Navigating to Microsoft Apps sign-in page")
        await page.goto("https://myapps.microsoft.com/signin/78f5464b-e016-4fdb-9478-ba285b87fb8e?tenantId=68283f3b-8487-4c86-adb3-a5228f18b893")
        await page.wait_for_load_state('networkidle')

        logging.info("Entering credentials")
        await page.get_by_role("textbox", name="Geben Sie Ihre E-Mail-Adresse").fill("chandan.sahoo1@vodafone.com")
        await page.get_by_role("button", name="Weiter", exact=True).click()
        await page.get_by_role("textbox", name="Geben Sie das Kennwort für \"").fill("Python@Deco!23456")
        await page.get_by_role("button", name="Anmelden").click()

        logging.info("Handling post-login prompts")
        await page.get_by_role("button", name="Nein").click()
        await page.locator("[id=\"1\"]").get_by_role("radio", name="ReadOnly").check()
        await page.get_by_role("link", name="Melden Sie sich an").click()

        # Wait for page to finish navigation before checking for cookie button
        await page.wait_for_load_state('networkidle')

        # Handle optional cookie consent button safely
        try:
            cookie_button = page.get_by_role("button", name="Ohne Akzeptieren fortfahren")
            if await cookie_button.is_visible():
                await cookie_button.click()
                logging.info("Clicked on cookie consent button.")
            else:
                logging.info("Cookie consent button not visible.")
        except Exception as e:
            logging.warning(f"Cookie consent button not found or not clickable: {e}")

        logging.info("Navigating to EC2 dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("EC2")
        await page.get_by_test_id("services-search-result-link-ec2").click()
        await page.wait_for_url("**/ec2/home**")

        logging.info("Waiting for EC2 dashboard iframe")
        await page.locator("iframe[title='Dashboard']").wait_for(state="visible", timeout=10000)
        iframe = page.frame_locator("iframe[title='Dashboard']")
        await iframe.get_by_role("link", name="Instances (ausgeführt)").click()

        logging.info("Waiting for Instances iframe")
        await page.locator("iframe[title='Instances']").wait_for(state="visible", timeout=10000)
        frame_locator = page.frame_locator("iframe[title='Instances']")
        count_element = frame_locator.get_by_text("(5)")
        text = await count_element.text_content()

        if text and text.strip() == "(5)":
            instResult = "✅  Found exactly 5 instances."
            logging.info(instResult)
            print(instResult)
        else:
            instResult = f"❌ Expected '(5)', but found: {text}"
            logging.warning(instResult)
            print(instResult)

        # === Navigate to RDS / Aurora ===
        logging.info("Navigating to RDS dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("RDS")
        await page.get_by_test_id("services-search-result-link-rds").click()
        await page.wait_for_url("**/rds/home**")


        await page.get_by_role("link", name="Datenbanken").wait_for(timeout=10000)
        await page.get_by_role("link", name="Datenbanken").click()
        logging.info("Clicked on 'Datenbanken' link")

        # Wait for the database list to load
        await page.wait_for_timeout(5000)  # Add a short delay to ensure content is loaded

        # Try a more flexible locator
        try:
            elements = await page.locator("text=Verfügbar").all()
            visible = False
            for el in elements:
                if await el.is_visible():
                    visible = True
                    break

            if visible:
                rds_result = "✅  Database is in Available state."
            else:
                rds_result = "❌ 'Verfügbar' status not visible."
        except Exception as e:
            rds_result = f"❌ Error checking 'Verfügbar' status: {e}"

        print(rds_result)

        # === Navigate to EKS ===
        logging.info("Navigating to EKS dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("EKS")
        await page.get_by_test_id("services-search-result-link-eks").click()
        await page.wait_for_url("**/eks/home**")
        await page.wait_for_timeout(5000)
        await page.get_by_test_id("cluster-list-table").locator("text=Aktiv").is_visible()
        # Check if cluster is "Aktiv"
        try:
            elements = await page.locator("text=Aktiv").all()
            visible = False
            for el in elements:
                if await el.is_visible():
                    visible = True
                    break

            if visible:
                eks_result = "✅  Cluster is Active. Proceeding with namespace and node checks."
            else:
                eks_result = "❌ Cluster is not in 'Aktiv' (Active) state. Skipping further checks."
        except Exception as e:
            eks_result = f"❌ Error checking 'Aktiv' status: {e}"

        print(eks_result)

        await browser.close()
        logging.info("Browser closed")

if __name__ == "__main__":
    asyncio.run(main())
