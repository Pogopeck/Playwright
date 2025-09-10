import os
import asyncio
import logging
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import requests

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

# File to store last seen request IDs
LAST_SEEN_FILE = "last_seen_requests.json"


def load_last_seen():
    """Load previously seen request IDs."""
    try:
        with open(LAST_SEEN_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_last_seen(request_ids):
    """Save current request IDs."""
    with open(LAST_SEEN_FILE, 'w') as f:
        json.dump(list(request_ids), f)


def send_teams_notification(title, message):
    """Send message to Microsoft Teams webhook."""
    payload = {
        "type": "MessageCard",
        "title": title,
        "text": message,
        "themeColor": "0078D4"  # Blue for info
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, proxies={"https": PROXY["server"]})
        if response.status_code != 200:
            logging.error(f"Failed to send Teams notification: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error sending Teams notification: {e}")

async def fetch_request_ids(page):
    try:
        # Wait for the table container to be visible
        await page.wait_for_selector("#WIN_2_301444200 .BaseTableInner", timeout=20000)

        # Get the entire container
        table_container = await page.query_selector("#WIN_2_301444200 .BaseTableInner")
        if not table_container:
            raise Exception("Table container not found")

        # Get all text from container
        full_text = await table_container.inner_text()
        logging.debug(f"Raw table text: {full_text[:500]}...")  # Log first 500 chars for debugging

        # Split into words/tokens and find INC/SR
        request_ids = set()
        tokens = full_text.split()

        for token in tokens:
            clean_token = token.strip().rstrip('.,;:')
            if clean_token.startswith(("INC", "SR")) and len(clean_token) > 6:  # e.g., INC00123
                request_ids.add(clean_token)

        request_ids = list(request_ids)
        logging.info(f"Found {len(request_ids)} request IDs: {request_ids}")
        return request_ids

    except Exception as e:
        logging.error(f"Error fetching request IDs: {e}")
        await page.screenshot(path="fetch_error_v2.png")
        html = await page.content()
        with open("fetch_error_v2.html", "w", encoding="utf-8") as f:
            f.write(html)
        logging.info("Debug files saved: fetch_error_v2.png, fetch_error_v2.html")
        return []

async def login_and_navigate(page):
    """Handle login and navigation to filtered view."""
    logging.info("Logging in...")

    # Fill email
    await page.get_by_role("textbox", name="Email, phone, or Skype").click()
    await page.get_by_role("textbox", name="Email, phone, or Skype").fill(itname)
    await page.get_by_role("button", name="Next").click()

    # Fill password
    await page.get_by_role("textbox", name="Enter the password for").click()
    await page.get_by_role("textbox", name="Enter the password for").fill(itpass)
    await page.get_by_role("button", name="Sign in").click()

    # Wait after login
    await page.wait_for_load_state("networkidle")

    # Handle popup: "No"
    async with page.expect_popup() as popup1_info:
        await page.get_by_role("button", name="No").click()
    page1 = await popup1_info.value
    await page1.close()

    # Click link to filter
    await page.locator("#WIN_2_303174300").get_by_role("link").click()

    # Handle second popup
    async with page.expect_popup() as popup2_info:
        await page.get_by_role("cell", name="Assigned To My Selected Groups").click()
    page2 = await popup2_info.value
    await page2.get_by_role("link", name="OK").click()

    logging.info("Navigation completed.")


async def monitor_new_requests():
    """Main function to log in and check for new requests."""
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=edge_path, headless=False)
            context = await browser.new_context(locale='en-US', proxy=PROXY)
            page = await context.new_page()

            # Go to OneITSM
            await page.goto(itsmurl, wait_until="networkidle")

            # Login and navigate
            await login_and_navigate(page)

            # Fetch current request IDs
            current_ids = await fetch_request_ids(page)

            # Load previously seen IDs
            last_seen = load_last_seen()
            new_ids = [rid for rid in current_ids if rid not in last_seen]

            if new_ids:
                logging.info(f"New requests detected: {new_ids}")
                for rid in new_ids:
                    send_teams_notification(
                        title="🚨 New Incident Detected",
                        message=f"New Request ID: `{rid}`\nCheck OneITSM dashboard."
                    )
                # Update last seen
                save_last_seen(current_ids)
            else:
                logging.info("No new requests found.")

    except Exception as e:
        logging.error(f"Error during monitoring: {e}")
    finally:
        if browser:
            await browser.close()


def run_monitoring():
    """Run monitoring periodically."""
    logging.info("Starting OneITSM Monitor...")
    while True:
        try:
            asyncio.run(monitor_new_requests())
            logging.info("Waiting for next check...")
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logging.error(f"Error in monitoring loop: {e}")
            time.sleep(60)  # Retry after 1 minute


if __name__ == "__main__":
    run_monitoring()
