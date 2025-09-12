import os
import asyncio
import re
import json
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables (credentials only)
load_dotenv()
jname = os.getenv("IT_NAME")
jpass = os.getenv("PRD_PASS")
JIRA_BASE_URL = "https://de.jira.agile.vodafone.com/browse/"  # Base URL without ticket

# Extract JIRA ID from CLI argument
def get_jira_id_from_args():
    if len(sys.argv) < 2:
        print("❌ Usage: python script.py <JIRA_ID> (e.g., DSF-12906)")
        sys.exit(1)
    return sys.argv[1].strip().upper()  # Normalize input

async def extract_package_details_from_description(page):
    """
    Extracts package details from JIRA description text.
    Returns dict: { "CN_000900": { "PackageName": "DSF_..." } }
    """
    selectors = [
        '#description-val',
        '[data-field-id="description"]',
        'div#descriptionmodule .user-content',
    ]

    description_text = ""
    for selector in selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            element = await page.query_selector(selector)
            if element:
                description_text = await element.inner_text()
                if description_text.strip():
                    print(f"✅ Description found using selector: {selector}")
                    break
        except Exception as e:
            print(f"Selector {selector} failed: {e}")
            continue

    if not description_text:
        print("❌ Could not extract description. Check selectors or page structure.")
        return {}

    # Regex to extract: DSF_..._CN_XXXXXX.zip
    pattern = r'(DSF_[^_]+_[^_]+_(CN_\d+)\.zip)'
    matches = re.findall(pattern, description_text)

    cn_migration_matrix = {}
    for full_name, cn_id in matches:
        cn_migration_matrix[cn_id] = {
            "PackageName": full_name
        }

    print(f"📦 Found {len(cn_migration_matrix)} packages.")
    return cn_migration_matrix

async def main():
    jira_id = get_jira_id_from_args()
    full_jira_url = JIRA_BASE_URL + jira_id

    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=True
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        # Navigate and login
        await page.goto(full_jira_url)
        await page.get_by_role("textbox", name="Enter your email, phone, or").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").fill(jname)
        await page.get_by_role("button", name="Next").click()
        await page.get_by_role("textbox", name="Enter the password for").click()
        await page.get_by_role("textbox", name="Enter the password for").fill(jpass)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="No").click()

        # Wait for issue page to load
        await page.wait_for_load_state("networkidle")

        # Output filename
        output_filename = f"{jira_id}_bundle.json"

        # Extract package details
        cn_migration_matrix = await extract_package_details_from_description(page)

        if not cn_migration_matrix:
            print("⚠️  No packages found. Check description content or regex pattern.")
        else:
            # Build final JSON structure
            output_json = {
                "cn_migration_matrix": cn_migration_matrix
            }

            # Save to file
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(output_json, f, indent=2)

            print(f"✅ JSON saved to: {output_filename}")
            print(json.dumps(output_json, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
