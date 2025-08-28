import os
import asyncio
import requests
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from plyer import notification
import schedule
import time

# ===========================
# 📦 Load Environment & Config
# ===========================
load_dotenv()

sname = os.getenv("IT_NAME")
spass = os.getenv("PRD_PASS")
dsfurl = os.getenv("PRD_URL")
webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

# Proxy for corporate network
PROXY = {
    "https": "http://mmoproxy.mdv.mmo.de:8080"  # Vodafone internal proxy
}

# ===========================
# 📝 Logging Setup (UTF-8 Safe)
# ===========================

# Ensure stdout uses UTF-8 to reduce emoji issues (optional, safe to keep)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dsf_monitor.log", encoding='utf-8'),  # Log file supports emojis
        logging.StreamHandler()  # Console: we'll avoid emojis here
    ]
)

# ===========================
# 🔔 Send Alert to Microsoft Teams (with emojis)
# ===========================
def send_teams_alert(count):
    if not webhook_url:
        logging.warning("TEAMS_WEBHOOK_URL not set. Skipping Teams alert.")
        return

    message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "FF0000" if count > 0 else "00FF00",
        "summary": "DSF Alert",
        "sections": [
            {
                "activityTitle": "🚨 DSF IT Operations Workbasket Alert",
                "activitySubtitle": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "facts": [
                    {"name": "Current Count", "value": str(count)},
                    {"name": "Status", "value": "⚠️ Action Required" if count > 0 else "✅ All Clear"}
                ],
                "text": "**High-priority items detected!**" if count > 0 else "No pending items found."
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "👉 Open DSF",
                "targets": [
                    {"os": "default", "uri": dsfurl}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            webhook_url,
            json=message,
            proxies=PROXY,
            timeout=30
        )
        if response.status_code == 200:
            logging.info("Teams notification sent to Microsoft Teams.")
        else:
            logging.error(f"Teams webhook failed: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error sending to Teams: {e}")


# ===========================
# 💻 Send Desktop Notification (with emojis)
# ===========================
def send_desktop_alert(count):
    try:
        notification.notify(
            title="🚨 DSF Alert: Items Detected",
            message=f"Found {count} item(s) in IT Operations WB!\nCheck DSF for details.",
            app_name="DSF Monitor",
            timeout=15
        )
        logging.info("Desktop notification displayed.")
    except Exception as e:
        logging.warning(f"Failed to show desktop notification: {e}")


# ===========================
# 🏁 Main Browser Automation
# ===========================
async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                executable_path=edge_path,
                headless=False
            )
            context = await browser.new_context(locale='en-US')
            page = await context.new_page()

            logging.info(f"Navigating to DSF: {dsfurl}")
            await page.goto(dsfurl, wait_until="networkidle")

            # Login flow
            logging.info("Logging in via SSO...")
            await page.get_by_role("link", name="Login with SSO").click()
            await page.get_by_role("textbox", name="Enter your email, phone, or").fill(sname)
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("textbox", name="Enter the password for").fill(spass)
            await page.get_by_role("button", name="Sign in").click()
            await page.get_by_role("button", name="No").click()

            # Wait for workbasket element
            logging.info("Waiting for IT Operations WB element...")
            await page.wait_for_selector("#ITOperationsWB", timeout=20000)
            logging.info("Found IT Operations WB element")

            # Get count from second <td> in the same row
            count_locator = page.locator("tr:has(#ITOperationsWB) > td:nth-child(2)")
            await count_locator.first.wait_for(timeout=10000)
            count_text = await count_locator.first.inner_text()
            count = int(count_text.strip()) if count_text.strip().isdigit() else 0

            logging.info(f"IT Operations WB Count: {count}")

            # Send alerts if items found
            if count > 0:
                send_desktop_alert(count)
                send_teams_alert(count)
            else:
                logging.info("No items found in workbasket. No alert sent.")

            await browser.close()

        except Exception as e:
            logging.error(f"Automation failed: {e}")
            try:
                await browser.close()
            except:
                pass


# ===========================
# 🔁 Run Monitor (Scheduled)
# ===========================
def run_monitor():
    logging.info("Starting DSF monitoring cycle...")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Failed to start monitoring cycle: {e}")


# ===========================
# ✅ Entry Point: Schedule & Run
# ===========================
if __name__ == "__main__":
    logging.info("DSF Monitor started.")
    logging.info("First run begins immediately...")

    # Run now first
    run_monitor()

    # Schedule every 15 minutes
    schedule.every(15).minutes.do(run_monitor)

    logging.info("Scheduled to run every 15 minutes. Monitoring continues...")

    # Keep script alive
    while True:
        schedule.run_pending()
        time.sleep(10)
