import os
import asyncio
from playwright.async_api import async_playwright

async def main():  # Added async here
    os.environ["DEBUG"] = "pw:api"
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    combined_cert_path = "D:\\Chandan\\combined_certificates.crt"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False
        )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://myttwos.vf-de.corp.vodafone.com/arsys/shared/login.jsp")
        await page.pause()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async function
