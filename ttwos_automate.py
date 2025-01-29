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

            # Set up dialog handler
            page.on("dialog", lambda dialog: dialog.accept())

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
            page.type("#username-id", "piyush.kalbande1", delay=100)
            page.type("#pwd-id", "Kalki#1988Kalki#1988", delay=100)
            print("Credentials entered")

            # Ensure the login button is visible and clickable
            page.wait_for_selector('#login', state='visible')
            print("Login button found")

            # Click login and wait for navigation
            page.click('#login', force=True)
            print("Login button clicked")

            # Wait for a moment to ensure popup appears
            time.sleep(2)

            try:
                # Wait for and handle the popup
                print("Looking for popup...")
                # Try to find the popup iframe if it exists
                popup_frame = page.frame_locator('iframe').first
                if popup_frame:
                    print("Found popup iframe")
                    popup_frame.locator('#PopupMsgFooter > a').click(timeout=5000)
                    print("Clicked Ok button on popup")

            except Exception as popup_error:
                print(f"Popup handling error: {str(popup_error)}")
                try:
                    page.click('text=OK', timeout=5000)
                except Exception as alt_error:
                    print(f"Alternative popup handling failed: {str(alt_error)}")
            # click on inc
            page.click('#WIN_0_641000070 > div.OuterTabsDiv > div.TabsViewPort > div > dl > dd:nth-child(3) > span.Tab > a')
            page.click('#WIN_0_641000124 > div.btntextdiv > div')

            time.sleep(5)
            # Click to logout before closing browser
            page.click('#WIN_0_536870888 > div.btntextdiv > div')

            # Wait for navigation to complete
            page.wait_for_load_state('networkidle')
            print("Navigation after login completed")

            # Additional wait to ensure page is fully loaded
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
