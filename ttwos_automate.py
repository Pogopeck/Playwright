import logging
from playwright.sync_api import sync_playwright
import os
import time
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ApplicationTeam:
    name: str
    members: List[str]


def setup_logging():
    logger = logging.getLogger('playwright_automation')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('automation.log')

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_next_team_member(team_members: List[str], current_index: int = 0) -> str:
    """Implement round-robin selection of team members"""
    return team_members[current_index % len(team_members)]


def find_matching_application(application_name: str, application_teams: Dict[str, ApplicationTeam]) -> ApplicationTeam:
    """Find matching application using fuzzy matching"""
    for app_name, app_team in application_teams.items():
        if (application_name.upper().strip() in app_name.upper() or
                app_name.upper() in application_name.upper().strip()):
            return app_team
    return None


def main():
    logger = setup_logging()

    # Define applications and team members
    application_teams = {
        "ATOLL": ApplicationTeam("ATOLL", ["Mayuri.chavan2", "Aritra.banerjee2"]),
        "Network Mobile": ApplicationTeam("Network Mobile", ["Mayuri.chavan2", "Pallvi.amolik"]),
        "ActixOne": ApplicationTeam("ActixOne", ["Aritra.banerjee2", "Ajay Jadhav"]),
        "STOV": ApplicationTeam("STOV", ["Mayuri Chavan", "Aritra.banerjee2"]),
        "IQLink": ApplicationTeam("IQLink", ["Aritra.banerjee2", "Pallvi.amolik"]),
        "GKTool": ApplicationTeam("GKTool", ["Pallvi.amolik"]),
        "Pre-HCM Suite": ApplicationTeam("Pre-HCM Suite", ["Pallvi.amolik", "Ajay Jadhav"]),
        "AND": ApplicationTeam("AND", ["Anant Kulkarni"]),
        "Ibwave": ApplicationTeam("Ibwave", ["Ajay Jadhav", "Aritra.banerjee2"]),
        "Ibwave Unity": ApplicationTeam("Ibwave Unity", ["Ajay Jadhav", "Aritra.banerjee2"]),
        "IRP": ApplicationTeam("IRP", ["Jyotirmaya Dange"]),
        "Saperion": ApplicationTeam("Saperion", ["Pritam Jaiswar", "Aritra.banerjee2", "Ajay Jadhav"]),
        "FME": ApplicationTeam("FME", ["Anant Kulkarni", "Mayuri Chavan"]),
        "CRAMER MOBILE": ApplicationTeam("CRAMER MOBILE",["chandan.sahoo1", "surbahi.mohite", "rohit.ashtikar1", "piyush.kalbande1","abdul.hakeem", "kajal.patil"]),
        "CRAMER MOBILE/Cramer Fixed": ApplicationTeam("CRAMER MOBILE/Cramer Fixed",["chandan.sahoo1", "surbahi.mohite", "rohit.ashtikar1","piyush.kalbande1", "abdul.hakeem", "kajal.patil"]),
        "PPLUS": ApplicationTeam("PPLUS", ["rucha.bhujbal1", "Aritra Banerjee"]),
    }

    # Initialize assignment counters for round-robin
    assignment_counters = {app_name: 0 for app_name in application_teams.keys()}

    # Log application teams configuration
    logger.info("Application Teams Configuration:")
    for app_name, app_team in application_teams.items():
        logger.info(f"Application: {app_name}")
        logger.info(f"Team Members: {', '.join(app_team.members)}")
        logger.info("-" * 50)

    chrome_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\chrome-win\\chrome.exe"
    combined_cert_path = "C:\\Users\\C.sahooA\\PycharmProjects\\Playwrightdemo\\combined_certificates.crt"

    if not os.path.exists(chrome_path):
        logger.error(f"Chrome not found at: {chrome_path}")
        return

    if not os.path.exists(combined_cert_path):
        logger.error(f"Combined certificate not found at: {combined_cert_path}")
        return

    logger.info("Setting up environment variables")
    os.environ['NODE_EXTRA_CA_CERTS'] = combined_cert_path

    with sync_playwright() as p:
        try:
            logger.info("Launching browser")
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=False
            )
            context = browser.new_context(
                viewport={"width": 1800, "height": 1000}
            )
            page = context.new_page()
            logger.debug("Browser context and page created successfully")

            # Set up dialog handler
            page.on("dialog", lambda dialog: dialog.accept())
            logger.info("Dialog handler set up")

            # Navigate to login page
            logger.info("Navigating to login page")
            page.goto("https://myttwos.vf-de.corp.vodafone.com/arsys/shared/login.jsp")

            # Handle login
            logger.info("Handling login process")
            page.wait_for_selector('#username-id', state='visible', timeout=30000)

            # Clear and fill credentials
            page.evaluate('document.querySelector("#username-id").value = ""')
            page.evaluate('document.querySelector("#pwd-id").value = ""')

            # Note: Replace with actual username
            #username = os.getenv('USERNAME')  # Get username from environment variable
            page.type("#username-id", "piyush.kalbande1", delay=100)
            page.type("#pwd-id", "Kalki#1988Kalki#1988", delay=100)  # Get password from environment variable

            page.wait_for_selector('#login', state='visible')
            page.click('#login', force=True)

            time.sleep(2)

            # Scrape INC data
            logger.info("Scraping INC data")
            data = page.evaluate('() => { return document.body.innerText; }')
            inc_lines = [line for line in data.split('\n') if line.startswith(('Z_INC', 'Z_SRT'))]
            logger.info(f"Found {len(inc_lines)} INC entries")

            # Process each INC
            for selected_inc in inc_lines:
                logger.info(f"Processing INC: {selected_inc}")
                try:
                    # Search for the INC
                    page.fill('#arid_WIN_0_536870961', selected_inc)
                    page.click('#WIN_0_536870891 > div.btntextdiv > div')
                    page.wait_for_load_state('networkidle')

                    # Extract application name
                    application_name = page.evaluate('document.querySelector("#arid_WIN_0_610000000").value')
                    logger.info(f"Found application name: {application_name}")

                    # Find matching application team
                    assigned_team = find_matching_application(application_name, application_teams)

                    if assigned_team:
                        # Get next team member using round-robin
                        current_index = assignment_counters[assigned_team.name]
                        team_member = get_next_team_member(assigned_team.members, current_index)
                        assignment_counters[assigned_team.name] = current_index + 1

                        logger.info(f"Assigning {selected_inc} to {team_member} for application {application_name}")

                        # Update assignment
                        page.type("#arid_WIN_0_4", team_member, delay=100)

                        # Update status
                        page.click('#WIN_0_rc2id7')  # Taken
                        page.click('#WIN_0_rc3id7')  # In-progress
                        page.click('#TBsearchsavechanges')  # Save

                        logger.info(f"Successfully assigned {selected_inc} to {team_member}")
                    else:
                        logger.warning(f"No matching team found for application {application_name}")

                except Exception as e:
                    logger.error(f"Error processing INC {selected_inc}: {str(e)}")
                    continue

                time.sleep(5)

            # Logout process
            logger.info("Logging out")
            page.click('#WIN_0_536870888 > div.btntextdiv > div')
            page.wait_for_load_state('networkidle')

            time.sleep(5)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}", exc_info=True)

        finally:
            if 'browser' in locals():
                logger.info("Closing browser")
                browser.close()


if __name__ == "__main__":
    main()
