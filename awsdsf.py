import os
import asyncio
import logging
from playwright.async_api import async_playwright
import win32com.client as win32

# === Configure Logging ===
logging.basicConfig(
    filename='dsf_log.txt',  # Log file name
    filemode='a',            # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO       # Log level (can be DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        #os.environ["DEBUG"] = "pw:api"
        browser = await p.chromium.launch(executable_path=edge_path, headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        logging.info("Navigating to Microsoft Apps sign-in page")
        await page.goto("https://myapps.microsoft.com/signin/78f5464b-e016-4fdb-9478-ba285b87fb8e?tenantId=68283f3b-8487-4c86-adb3-a5228f18b893")
        await page.wait_for_load_state('networkidle')

        logging.info("Entering credentials")
        await page.get_by_role("textbox", name="Geben Sie Ihre E-Mail-Adresse").fill("chandan.sahoo1@vodafone.com")
        await page.get_by_role("button", name="Weiter", exact=True).click()
        await page.get_by_role("textbox", name="Geben Sie das Kennwort für \"").fill("Python@Deco!23456")
        await page.get_by_role("button", name="Anmelden").click()

        logging.info("Handling post-login prompts")
        await page.get_by_role("button", name="Nein").click()
        await page.locator("[id=\"1\"]").get_by_role("radio", name="ReadOnly").check()
        await page.get_by_role("link", name="Melden Sie sich an").click()

        # Wait for page to finish navigation before checking for cookie button
        await page.wait_for_load_state('networkidle')

        # Handle optional cookie consent button safely
        try:
            cookie_button = page.get_by_role("button", name="Ohne Akzeptieren fortfahren")
            if await cookie_button.is_visible():
                await cookie_button.click()
                logging.info("Clicked on cookie consent button.")
            else:
                logging.info("Cookie consent button not visible.")
        except Exception as e:
            logging.warning(f"Cookie consent button not found or not clickable: {e}")

        logging.info("Navigating to EC2 dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("EC2")
        await page.get_by_test_id("services-search-result-link-ec2").click()
        await page.wait_for_url("**/ec2/home**")

        logging.info("Waiting for EC2 dashboard iframe")
        await page.locator("iframe[title='Dashboard']").wait_for(state="visible", timeout=10000)
        iframe = page.frame_locator("iframe[title='Dashboard']")
        await iframe.get_by_role("link", name="Instances (ausgeführt)").click()

        logging.info("Waiting for Instances iframe")
        await page.locator("iframe[title='Instances']").wait_for(state="visible", timeout=10000)
        frame_locator = page.frame_locator("iframe[title='Instances']")
        count_element = frame_locator.get_by_text("(5)")
        text = await count_element.text_content()

        if text and text.strip() == "(5)":
            instResult = "✅  Found exactly 5 instances."
            logging.info(instResult)
            print(instResult)
        else:
            instResult = f"❌ Expected '(5)', but found: {text}"
            logging.warning(instResult)
            print(instResult)
        await page.wait_for_timeout(5000)
        # === Navigate to RDS / Aurora ===
        logging.info("Navigating to RDS dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("RDS")
        await page.get_by_test_id("services-search-result-link-rds").click()
        await page.wait_for_url("**/rds/home**")
        await page.wait_for_timeout(5000)
        await page.get_by_role("link", name="Datenbanken").wait_for(timeout=10000)
        await page.get_by_role("link", name="Datenbanken").click()
        logging.info("Clicked on 'Datenbanken' link")

        # Wait for the database list to load
        await page.wait_for_timeout(5000)  # Add a short delay to ensure content is loaded

        # Try a more flexible locator
        try:
            elements = await page.locator("text=Verfügbar").all()
            visible = False
            for el in elements:
                if await el.is_visible():
                    visible = True
                    break

            if visible:
                rds_result = "✅  Database is in Available state."
            else:
                rds_result = "❌ 'Verfügbar' status not visible."
        except Exception as e:
            rds_result = f"❌ Error checking 'Verfügbar' status: {e}"

        print(rds_result)

        # === Navigate to EKS ===
        logging.info("Navigating to EKS dashboard")
        await page.get_by_test_id("awsc-concierge-input").fill("EKS")
        await page.wait_for_timeout(5000)
        await page.get_by_test_id("services-search-result-link-eks").click()
        await page.wait_for_url("**/eks/home**")
        await page.wait_for_timeout(5000)
        await page.get_by_test_id("cluster-list-table").locator("text=Aktiv").is_visible()
        # Check if cluster is "Aktiv"
        try:
            elements = await page.locator("text=Aktiv").all()
            visible = False
            for el in elements:
                if await el.is_visible():
                    visible = True
                    break

            if visible:
                eks_result = "✅  Cluster is Active. Proceeding with namespace and node checks."
            else:
                eks_result = "❌ Cluster is not in 'Aktiv' (Active) state. Skipping further checks."
        except Exception as e:
            eks_result = f"❌ Error checking 'Aktiv' status: {e}"

        print(eks_result)
        await page.get_by_role("link", name="Link zu vfde-prod-dsf-").click()
        await page.get_by_test_id("cluster-resources-tab").click()
        await page.get_by_role("button", name="Namespace auswählen All").click()
        await page.get_by_text("pega").first.click()

        # === Validate the pod count ===
        logging.info("Validating pod count")
        try:
            # Wait for the Workloads section to appear (adjust selector as needed)
            await page.wait_for_timeout(5000)  # Allow time for data to load

            # Use a flexible locator to find any "Pods (X)" text
            pod_text_locator = page.locator("text=Pods (").first

            # Wait explicitly for the element to be available and visible
            await pod_text_locator.wait_for(state="visible", timeout=30000)
            full_text = await pod_text_locator.text_content()
            logging.info(f"Found pod count text: {full_text}")

            # Extract the number using regex
            import re
            match = re.search(r"Pods\s*\((\d+)\)", full_text)
            if not match:
                pod_count_result = "❌ Could not parse pod count from text."
                logging.warning(pod_count_result)
                print(pod_count_result)
            else:
                pod_count = int(match.group(1))
                if pod_count == 4:
                    pod_count_result = "✅  Pod count is correct: 4"
                    logging.info(pod_count_result)
                    print(pod_count_result)
                else:
                    pod_count_result = f"❌ Expected 4 pods, but found: {pod_count}"
                    logging.warning(pod_count_result)
                    print(pod_count_result)

        except Exception as e:
            pod_count_result = f"❌ Error validating pod count: {type(e).__name__}: {e}"
            logging.error(pod_count_result)
            print(pod_count_result)

        await page.wait_for_timeout(5000)
        # === Navigate to S3 ===
        await page.get_by_test_id("awsc-concierge-input").click()
        await page.get_by_test_id("awsc-concierge-input").fill("S3")
        await page.get_by_test_id("services-search-result-link-s3").click()
        await page.get_by_role("link", name="-file-transfer").click()
        await page.get_by_role("link", name="fif_transfer/").click()
        #await page.pause()
        # === Check for .xml files in fif_transfer/ folder ===
        logging.info("Checking for .xml files in fif_transfer/ folder")

        try:
            await page.wait_for_timeout(5000)
            file_elements = await page.locator("a[href*='fif_transfer/']").all_text_contents()
            xml_files = [file for file in file_elements if file.endswith(".xml")]

            if xml_files:
                s3_result = ", ".join(xml_files)
            else:
                s3_result = "OK"

            print(f"S3 Result: {s3_result}")
            logging.info(f"S3 Result: {s3_result}")

        except Exception as e:
            s3_result = f"Error checking S3 folder contents: {e}"
            print(s3_result)
            logging.error(s3_result)

            #logging.info(s3_result)

        except Exception as e:
            s3_result = f"❌ Error checking S3 folder contents: {e}"
            print(s3_result)
            logging.error(s3_result)
        import win32com.client as win32

        # Replace these with your actual results
        ec2_status = "5 INSTANCES"
        ec2_result = "OK"

        rds_status = "DEPDSF"
        rds_result = "OK"

        eks_status = "ACTIVE"
        eks_result = "OK"

        pods_status = "4"
        pods_result = "OK"

        s3_status = "FIF files"
        s3_result = ", ".join(xml_files) if xml_files else "OK"

        # Construct the HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 60%;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h2>AWS Validation Report</h2>
            <table>
                <tr>
                    <th>AWS</th>
                    <th>Service</th>
                    <th>Status</th>
                    <th>Result</th>
                </tr>
                <tr>
                    <td rowspan="5">AWS</td>
                    <td>EC2</td>
                    <td>{ec2_status}</td>
                    <td>{ec2_result}</td>
                </tr>
                <tr>
                    <td>RDS</td>
                    <td>{rds_status}</td>
                    <td>{rds_result}</td>
                </tr>
                <tr>
                    <td>CLUSTER</td>
                    <td>{eks_status}</td>
                    <td>{eks_result}</td>
                </tr>
                <tr>
                    <td>PODS</td>
                    <td>{pods_status}</td>
                    <td>{pods_result}</td>
                </tr>
                <tr>
                    <td>S3</td>
                    <td>{s3_status}</td>
                    <td>{s3_result}</td>
                </tr>
            </table>
        </body>
        </html>
        """

        # Send the email
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = "chandan.sahoo1@vodafone.com"  # Replace with actual recipient
        mail.Subject = "AWS Sanity Report"
        mail.HTMLBody = html_body
        mail.Send()

        print("✅  Email sent successfully.")

        #await page.pause()
        await browser.close()
        logging.info("Browser closed")

if __name__ == "__main__":
    asyncio.run(main())
