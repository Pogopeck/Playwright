from playwright.sync_api import sync_playwright
import os
import time

def main():
    chrome_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\chrome-win\\chrome.exe"
    combined_cert_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\combined_certificates.crt"

    if not os.path.exists(chrome_path):
        print(f"Chrome not found at: {chrome_path}")
        return

    if not os.path.exists(combined_cert_path):
        print(f"Combined certificate not found at: {combined_cert_path}")
        return

    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path


    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=False
            )
            context = browser.new_context(
                viewport={"width": 1800, "height": 1000}
            )
            page = context.new_page()

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


            # Scrape the data using JavaScript
            data = page.evaluate('''() => {
                return document.body.innerText;
            }''')

            # Extract and list only the INCs
            inc_lines = [line for line in data.split('\n') if line.startswith('Z_INC', 'Z_SRT')]
            for inc in inc_lines:
                print(inc)

            # Process each INC
            for selected_inc in inc_lines:
                print(f"Selected INC: {selected_inc}")

                # Paste the INC value in the selector
                page.fill('#arid_WIN_0_536870961', selected_inc)
                page.click('#WIN_0_536870891 > div.btntextdiv > div')

                # Wait for the page to load the INC details
                page.wait_for_load_state('networkidle')

                value = page.evaluate('''() => {
                    const element = document.querySelector('#arid_WIN_0_810000112');
                    return element ? element.textContent : 'Element not found';
                }''')
                print(value)

                time.sleep(5)

                # Close the tab
                page.close()

            time.sleep(50)
            # Click to logout before closing browser
            page.click('#WIN_0_536870888 > div.btntextdiv > div')

            # Wait for navigation to complete
            page.wait_for_load_state('networkidle')
            print("Navigation after login completed")

            # Additional wait to ensure page is fully loaded
            time.sleep(5)

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == "__main__":
    main()


## "#WIN_0_rc2id7 -- selector of Taken" 
## "#WIN_0_rc3id7 -- selecror of In-progress"
## "#arid_WIN_0_610000000 -- Selector of short desc"

def main():
    # Define applications and team members
    application_teams = {
        
        "ATOLL": ApplicationTeam("ATOLL", ["Mayuri Chavan", "Aritra Banerjee"]),
        "Network Mobile": ApplicationTeam("Network Mobile", ["Mayuri Chavan", "Pallavi Amolik"]),
        "ActixOne": ApplicationTeam("ActixOne", ["Aritra Banerjee", "Ajay Jadhav"]),
        "STOV": ApplicationTeam("STOV", ["Mayuri Chavan", "Aritra Banerjee"]),
        "IQLink": ApplicationTeam("IQLink", ["Aritra Banerjee", "Pallavi Amolik"]),
        "GKTool": ApplicationTeam("GKTool", ["Pallavi Amolik"]),
        "Pre-HCM Suite": ApplicationTeam("Pre-HCM Suite", ["Pallavi Amolik", "Ajay Jadhav"]),
        "AND": ApplicationTeam("AND", ["Anant Kulkarni"]),
        "Ibwave": ApplicationTeam("Ibwave", ["Ajay Jadhav", "Aritra Banerjee"]),
        "Ibwave Unity": ApplicationTeam("Ibwave Unity", ["Ajay Jadhav", "Aritra Banerjee"]),
        "IRP": ApplicationTeam("IRP", ["Jyotirmaya Dange"]),
        "Saperion": ApplicationTeam("Saperion", ["Pritam Jaiswar", "Aritra Banerjee", "Ajay Jadhav"]),
        "FME": ApplicationTeam("FME", ["Anant Kulkarni", "Mayuri Chavan"]),
        "CRAMER MOBILE": ApplicationTeam("App2", ["chandan.sahoo1", "surbahi.mohite", "rohit.ashtikar1", "piyush.kalbande1", "abdul.hakeem", "kajal.patil"]),
        "CRAMER MOBILE/Cramer Fixed": ApplicationTeam("App2", ["chandan.sahoo1", "surbahi.mohite", "rohit.ashtikar1", "piyush.kalbande1", "abdul.hakeem", "kajal.patil"]),
        "PPLUS": ApplicationTeam("PPLUS", ["rucha.bhujbal1", "Aritra Banerjee"]),
    }
