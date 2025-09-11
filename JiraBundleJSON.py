import os
import asyncio
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()
jname = os.getenv("IT_NAME")
jpass = os.getenv("PRD_PASS")
jiraurl = os.getenv("JIRA_URL")

async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    #combined_cert_path = "D:\\Chandan\\combined_certificates.crt"  # Not used in this script but kept for reference

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        # Navigate to DSF URL
        await page.goto(jiraurl)
        await page.get_by_role("textbox", name="Enter your email, phone, or").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").fill(jname)
        await page.get_by_role("button", name="Next").click()
        await page.get_by_role("textbox", name="Enter the password for").click()
        await page.get_by_role("textbox", name="Enter the password for").fill(jpass)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="No").click()
        await page.pause()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())  #
