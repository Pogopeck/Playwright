import os
import asyncio
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()
sname = os.getenv("IT_NAME")
spass = os.getenv("PRD_PASS")
dsfurl = os.getenv("PRD_URL")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ►► HELPER: JavaScript Click Fallback for Pega ◄◄
async def js_click(locator, description="element"):
    """Fallback JavaScript click for stubborn Pega elements"""
    try:
        await locator.evaluate("element => element.click()")
        logging.info(f"✅ JS Click succeeded on {description}")
        return True
    except Exception as e:
        logging.warning(f"⚠️ JS Click failed on {description}: {e}")
        return False


async def main():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=edge_path,
            headless=False,  # Set to True for scheduled runs
        )
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        try:
            # ► STEP 1: Login ◄
            logging.info("🌐 Navigating to DSF URL...")
            await page.goto(dsfurl)

            logging.info("🔐 Starting login process...")
            await page.get_by_role("link", name="Login with SSO").click()
            await page.get_by_role("textbox", name="Enter your email, phone, or").fill(sname)
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("textbox", name="Enter the password for").fill(spass)
            await page.get_by_role("button", name="Sign in").click()
            await page.get_by_role("button", name="No").click()

            logging.info("✅ IT Admin - URL accessibility is working")

            # ► STEP 2: Handle Global Search Popup ◄
            async with page.expect_popup() as page1_info:
                await page.get_by_role("button", name="Click to trigger the search").click()
            page1 = await page1_info.value

            # Interact with popup page
            locator = page1.locator('[data-test-id="202006091432210525478"] [data-test-id="2016122110475608391271"]')
            await locator.click()
            await locator.fill("dsf-*")
            await locator.press("Enter")

            # Validate Global Search Result
            result_count_locator = page1.locator("text=500 results")
            try:
                await result_count_locator.wait_for(state="visible", timeout=10000)
                result_text = await result_count_locator.text_content()
                assert result_text.strip() == "500 results", f"Expected '500 results', but got '{result_text}'"
                logging.info("✅ Global Search is working")
            except Exception as e:
                logging.error(f"❌ Global Search assertion failed: {e}")
                raise

            # ► STEP 3: Navigate to DSF Workbasket & Validate IT Operations WB ◄
            logging.info("📂 Navigating to DSF Workbasket...")
            await page1.get_by_role("link", name="DSF Workbasket").click()
            await page1.wait_for_load_state("domcontentloaded")

            # Wait for UI mask to disappear
            try:
                mask = page1.locator("#pega_ui_mask")
                await mask.wait_for(state="hidden", timeout=15000)
                logging.info("✅ UI mask disappeared")
            except Exception as e:
                logging.warning(f"⚠️ UI mask didn't disappear, proceeding anyway: {e}")

            # Attempt to collapse sidebar (optional)
            logging.info("↔️ Attempting to collapse sidebar (if expanded)...")
            try:
                collapse_btn = page1.locator('button[aria-label="Collapse Panel"], [title="Collapse"], #sidebar-toggle, button[data-test-id*="collapse"]')
                await collapse_btn.wait_for(state="visible", timeout=3000)
                await collapse_btn.click()
                logging.info("✅ Sidebar collapsed")
                await page1.wait_for_timeout(1000)
            except Exception as e:
                logging.info("ℹ️ Sidebar collapse not needed or button not found")

            # Click IT Operations WB
            logging.info("🖱️ Clicking 'IT Operations WB'...")
            it_wb_locator = page1.locator("#ITOperationsWB")
            await it_wb_locator.wait_for(state="visible", timeout=10000)

            clicked = False
            for attempt in range(3):
                try:
                    await it_wb_locator.click(timeout=5000)
                    clicked = True
                    break
                except Exception as e:
                    logging.warning(f"⚠️ Normal click attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        await page1.wait_for_timeout(2000)

            if not clicked:
                logging.info("🔄 Falling back to JavaScript click on 'IT Operations WB'")
                await js_click(it_wb_locator, "IT Operations WB")

            logging.info("✅ Clicked 'IT Operations WB'")

            # Validate count on main page
            logging.info("⏳ Waiting for IT Operations WB element on main page...")
            await page.wait_for_selector("#ITOperationsWB", timeout=10000)
            logging.info("✅ Found IT Operations WB element on main page")

            count_locator = page.locator("tr:has(#ITOperationsWB) > td:nth-child(2)")
            await count_locator.wait_for(timeout=10000)
            count_text = await count_locator.inner_text()
            count = int(count_text.strip()) if count_text.strip().isdigit() else 0
            logging.info(f"🔢 IT Operations WB Count: {count}")

            assert count == 0, f"❌ IT Operations WB count is {count}, expected 0"
            logging.info("✅ IT Operations WB count is zero - Validation passed")

            # ► STEP 4: Navigate to Failed Processing Report ◄
            logging.info("📂 Navigating to 'Failed Processing of Imported File' report...")

            # Click "Old Administration"
            await page1.get_by_role("link", name="Old Administration").click()
            await page1.wait_for_load_state("domcontentloaded")

            # Wait for UI mask
            try:
                mask = page1.locator("#pega_ui_mask")
                await mask.wait_for(state="hidden", timeout=15000)
            except:
                pass

            # Locate and expand "Export and Import of..."
            export_section_title = page1.get_by_title("Export and Import of")
            expand_icon = export_section_title.locator("i.icon-openclose")

            logging.info("🔍 Locating 'Export and Import of...' expand icon...")
            await expand_icon.wait_for(state="visible", timeout=10000)
            await expand_icon.scroll_into_view_if_needed()

            # Try normal click
            clicked = False
            for attempt in range(3):
                try:
                    logging.info(f"▶️ Attempt {attempt + 1}: Clicking expand icon...")
                    await expand_icon.click(timeout=5000)
                    clicked = True
                    break
                except Exception as e:
                    logging.warning(f"⚠️ Click attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        await page1.wait_for_timeout(2000)

            # Fallback to JS click
            if not clicked:
                logging.info("🔄 Falling back to JavaScript click on expand icon...")
                await js_click(expand_icon, "Export and Import expand icon")

            logging.info("✅ Expand icon clicked — waiting for menu to open...")

            # Wait for target report link to appear
            report_locator = page1.locator("[data-test-id=\"202103040611470626102\"]")
            try:
                await report_locator.wait_for(state="visible", timeout=15000)
                logging.info("✅ 'Failed processing of imported file report' link is now visible")
            except Exception as e:
                logging.warning("⚠️ Report link not visible — forcing expand again...")
                try:
                    await expand_icon.click(force=True)
                    await report_locator.wait_for(state="visible", timeout=10000)
                except:
                    raise Exception("❌ Menu did not expand — report link remains hidden after all attempts")

            # Click the report
            await report_locator.click()
            await page1.wait_for_load_state("domcontentloaded")

            # Wait for UI mask again
            try:
                mask = page1.locator("#pega_ui_mask")
                await mask.wait_for(state="hidden", timeout=15000)
            except:
                pass

            # ► STEP 5: Validate Failed Processing Report ◄
            logging.info("🔍 Validating Failed Processing of Imported File report...")

            # Find the table
            table = page1.locator("table[data-test-id]")
            await table.wait_for(state="visible", timeout=10000)

            # Get text content of first cell — even if "hidden"
            first_cell = table.locator("tbody tr td").first
            text_content = await first_cell.text_content()

            if text_content and text_content.strip() == "No items":
                logging.info("✅ 'No items' found in Failed Processing report - Validation passed")
            else:
                # Check for actual data rows — exclude the "No items" row
                no_items_row = table.locator("tbody tr").filter(has_text="No items")
                no_items_count = await no_items_row.count()

                if no_items_count > 0:
                    logging.info("✅ 'No items' found in Failed Processing report - Validation passed")
                else:
                    # Count rows that do NOT contain "No items"
                    real_data_rows = table.locator("tbody tr").filter(has_not_text="No items")
                    row_count = await real_data_rows.count()
                    if row_count > 0:
                        logging.error(f"❌ Found {row_count} failed items in report. Expected 0.")

                        # Log sample failed items
                        failed_files = []
                        for i in range(min(row_count, 5)):
                            try:
                                first_cell_in_row = real_data_rows.nth(i).locator("td").first
                                file_name = await first_cell_in_row.text_content()
                                failed_files.append(file_name.strip())
                            except Exception as e:
                                failed_files.append(f"<error reading row {i}: {e}>")
                        logging.info(f"📄 Sample failed items: {failed_files}")

                        raise AssertionError(f"Failed Processing report contains {row_count} items. Expected 0.")
                    else:
                        logging.warning("⚠️ Report state unclear — neither empty nor data detected.")
                        body_text = await page1.text_content("body")
                        logging.debug(f"📄 Page text preview: {body_text[:300]}...")
                        raise AssertionError("Failed Processing report UI state is ambiguous.")
            await page1.close()

            # ► STEP 6: Switch Apps & Close ◄
            logging.info("🔄 Switching apps and closing browser...")
            await page.locator("[data-test-id=\"px-opr-image-ctrl\"]").click()
            await page.get_by_role("menuitem", name="Switch Apps").hover()
            await page.get_by_role("menuitem", name="Digital Service Fulfillment (IT Administrator)").click()
            await page.locator("[data-test-id=\"switch-wks\"]").click()
            await page.get_by_role("menuitem", name="Admin Studio").click()
            await page.pause()

        except Exception as e:
            logging.error(f"🚨 An error occurred during execution: {e}")
            raise
        finally:
            await browser.close()
            logging.info("🏁 Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
