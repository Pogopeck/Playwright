from playwright.sync_api import sync_playwright
import os
import time

def main():
    chrome_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\chrome-win\\chrome.exe"
    combined_cert_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\combined_certificates.crt"

    # Verify Chrome and combined certificate exist
    if not os.path.exists(chrome_path):
        print(f"Chrome not found at: {chrome_path}")
        return

    if not os.path.exists(combined_cert_path):
        print(f"Combined certificate not found at: {combined_cert_path}")
        return

    # Set the NODE_EXTRA_CA_CERTS environment variable
    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=False
            )
            page = browser.new_page()

            # Navigate to the login page
            print("Navigating to login page...")
            page.goto("https://myttwos.vf-de.corp.vodafone.com/arsys/shared/login.jsp")

            # Wait for the login form to be visible
            page.wait_for_selector('#username-id', state='visible', timeout=30000)
            print("Login form found")

            # Clear the fields first
            page.evaluate('document.querySelector("#username-id").value = ""')
            page.evaluate('document.querySelector("#pwd-id").value = ""')

            # Type the credentials slowly
            page.type("#username-id", "chandan.sahoo1", delay=100)
            page.type("#pwd-id", "Laxmipe!234", delay=100)
            print("Credentials entered")

            # Ensure the login button is visible and clickable
            page.wait_for_selector('#login', state='visible')
            print("Login button found")

            # Click login and wait for navigation
            page.click('#login', force=True)
            print("Login button clicked")
            time.sleep(5)
            page.wait_for_selector('//*[@id="PopupMsgFooter"]/a', state='visible')
            page.locator('//*[@id="PopupMsgFooter"]/a').click()
            # Wait for navigation to complete
            page.wait_for_load_state('networkidle')
            print("Navigation after login completed")
            time.sleep(5)
            # Check for error messages
            if page.query_selector('.error-message'):
                error_message = page.query_selector('.error-message').inner_text()
                print(f"Login failed: {error_message}")
            else:
                # Take screenshot after login
                page.screenshot(path="after_login.png", full_page=True)
                print("Screenshot captured successfully")

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == "__main__":
    main()
