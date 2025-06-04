import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger.EventLogger import log_message
from components.linkedin_automation.web_scrapper_selanium.helpers.ScrapeHelpers import scrape_job_data
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped
from components.linkedin_automation.web_scrapper_selanium.helpers.PageChange import go_to_next_page
import streamlit as st

# ------------------------------{Main Scraper Function}------------------------------
def scrape_all_jobs(driver, wait, short_wait, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        results = []
        page = 1
        j = 0
        total_jobs_to_apply = st.session_state.get("job_settings_backup", {}).get("switch_number", 25)

        while True:
            exit_if_stopped("PAGE LOOP STOPPED", driver, log_base, echo)

            log_message(f"\n📄 Scraping Page {page}", log_file=log_base, echo=echo)
            time.sleep(1)

            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-occludable-job-id]')))
            log_message(f"🔍 Found {len(job_cards)} jobs on this page.", log_file=log_base, echo=echo)

            for card in job_cards:
                exit_if_stopped("JOB LOOP STOPPED", driver, log_base, echo)

                try:
                    job_id = card.get_attribute("data-occludable-job-id")

                    if total_jobs_to_apply == j:
                        return driver, results

                    # Find if JOB ALREADY APPLIED
                    try:
                        container = driver.find_element(By.CSS_SELECTOR, f'li[data-occludable-job-id="{job_id}"]')
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)

                        selector = '.job-card-container__footer-job-state'
                        applied_status = short_wait.until(
                            lambda d: container.find_element(By.CSS_SELECTOR, selector)
                        ).text.strip()

                        if "applied" in applied_status.lower():
                            log_message(f"⏭️ Skipping Job ID {job_id}: Already Applied", log_file=log_base, echo=echo)
                            continue
                    except Exception:
                        applied_status = "Not Applied"

                    # Find if EASY APPLY
                    try:
                        container = driver.find_element(By.CSS_SELECTOR, f'li[data-occludable-job-id="{job_id}"]')
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)

                        def easy_apply_marker(d):
                            icon = container.find_elements(By.CSS_SELECTOR, 'image[href*="cukxdu7s8ldmqz13xdao5xe75"]')
                            spans = container.find_elements(By.CSS_SELECTOR, 'span[dir="ltr"]')
                            return icon or any("easy apply" in span.text.strip().lower() for span in spans)

                        short_wait.until(easy_apply_marker)
                        log_message(f"⏭️ Skipping Job ID {job_id}: Easy Apply (Waited for marker)", log_file=log_base, echo=echo)
                        continue
                    except Exception:
                        pass  # No marker found; proceed

                    # Click the job card
                    try:
                        fresh_card = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[data-occludable-job-id="{job_id}"]'))
                        )
                        driver.execute_script("arguments[0].scrollIntoView(true);", fresh_card)
                        fresh_card.click()
                        time.sleep(1)
                    except Exception as e:
                        log_message(f"❌ Error clicking job ID {job_id} due to stale or missing element: {e}",
                                    log_file=log_base, echo=echo)
                        continue
                    time.sleep(1)

                    driver, wait, short_wait, job_data = scrape_job_data(driver, wait, short_wait, job_id, applied_status)

                    # If data is valid
                    if (job_data.get("Job Title") and job_data.get("Company Name") and 
                        job_data.get("Job Description") and job_data.get("Application Link")):
                        results.append(job_data)
                        log_message(f"✅ Scraped {j}/{total_jobs_to_apply}: {job_data['Job Title']} @ {job_data['Company Name']}",
                                    log_file=log_base, echo=echo)
                        j += 1
                    else:
                        log_message(f"⚠️ Incomplete data for Job ID {job_id}, skipping append.", log_file=log_base, echo=echo)

                except Exception as e:
                    log_message(f"❌ Error scraping job {j}, {e}", log_file=log_base, echo=echo)
                    continue

            if go_to_next_page(driver, page, log_base, echo):
                return driver, results
            page += 1

    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: JOB SCRAPER", log_file=log_base, echo=echo)
        driver.quit()
        exit()