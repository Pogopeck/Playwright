import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
# Access them using os.getenv
gname = os.getenv("GNAME")
gpass = os.getenv("GPASS")
ghurl = os.getenv("GH_URL")

from playwright.async_api import async_playwright

async def main():  # Added async here
    #os.environ["DEBUG"] = "pw:api"
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    ##chrome_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    combined_cert_path = "D:\\Chandan\\combined_certificates.crt"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()
        await page.goto(ghurl)
        await page.get_by_role("textbox", name="Enter your email, phone, or").click()
        await page.get_by_role("textbox", name="Enter your email, phone, or").fill(gname)
        await page.get_by_role("button", name="Next").click()
        await page.get_by_role("textbox", name="Enter the password for").click()
        await page.get_by_role("textbox", name="Enter the password for").fill(gpass)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="No").click()
        await page.get_by_role("button", name="Add file").click()
        await page.get_by_role("menuitem", name="Create new file").click()

        await page.pause()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async function
