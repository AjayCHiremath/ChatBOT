# -----{ Required Imports }------
import os
import time
import streamlit as st

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from utils.logger.EventLogger import log_message


# -----{ Input job title into LinkedIn search bar }------
def input_job_title(driver, wait, job_keyword, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            log_message(f"⌨️ Typing job title: {job_keyword}", log_file=log_base, echo=echo)

            job_input_xpath = "//input[@aria-label='Search by title, skill, or company' and not(@disabled)]"
            job_input = wait.until(EC.element_to_be_clickable((By.XPATH, job_input_xpath)))

            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].focus();", job_input)
            time.sleep(1)
            job_input.clear()
            job_input.send_keys(job_keyword)

            log_message(f"✔️ Entered job title: {job_keyword}", log_file=log_base, echo=echo)
            return driver
        except Exception as e:
            log_message(f"❌ Failed to enter job title: {e}", log_file=log_base, echo=echo)
            driver.quit()
            exit()
    else:
        log_message("🛑 Terminating Browser: JOB Title", log_file=log_base, echo=echo)
        driver.quit()
        exit()


# -----{ Input job location into LinkedIn search bar }------
def input_location(driver, wait, location_keyword, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            log_message(f"⌨️ Typing job location: {location_keyword}", log_file=log_base, echo=echo)

            #-----------------------{ Locate location input }--------------------------
            location_input_xpath = "//input[@aria-label='City, state, or zip code' and not(@disabled)]"
            location_input = wait.until(EC.element_to_be_clickable((By.XPATH, location_input_xpath)))

            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].focus();", location_input)
            time.sleep(1)
            location_input.clear()
            location_input.send_keys(location_keyword)

            #-----------------------{ Wait and select autosuggestion }--------------------------
            time.sleep(2)  # Allow dropdown to appear
            location_input.send_keys(Keys.DOWN)  # Highlight first suggestion
            time.sleep(0.5)
            location_input.send_keys(Keys.ENTER)  # Confirm selection

            log_message(f"✔️ Entered job location: {location_keyword}", log_file=log_base, echo=echo)
            return driver
        except Exception as e:
            log_message(f"❌ Failed to enter job location: {e}", log_file=log_base, echo=echo)
            driver.quit()
            exit()
    else:
        log_message("🛑 Terminating Browser: LOCATION", log_file=log_base, echo=echo)
        driver.quit()
        exit()


# -----{ Complete flow to open job search and apply filters }------
def go_to_job_search(driver, wait, job_keyword="", log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            #-----------------------{ Extract search location safely }--------------------------
            job_settings = st.session_state.get("job_settings_backup", {})
            location_keyword = ""

            if isinstance(job_settings, dict):
                search_loc = job_settings.get("search_location", "")
                if isinstance(search_loc, str) and search_loc:
                    location_keyword = search_loc.split(',')[0].strip()
            
            # -----{ Fill job title and location fields }------
            driver = input_job_title(driver, wait, job_keyword, log_base, echo)
            driver = input_location(driver, wait, location_keyword, log_base, echo)
            
            # -----{ Log search activity }------
            log_message(f"🔍 Searched for: {job_keyword} in {location_keyword}",
                        log_file=os.path.join(log_base), echo=echo)

            time.sleep(3)  # Allow page to load after location input

        except Exception as e:
            # -----{ Log and exit if job search fails }------
            log_message(f"❌ Job search failed: {e}",
                        log_file=os.path.join(log_base), echo=echo)
            driver.quit()
            exit()
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: MAIN JOB SEARCH TERMINATED", log_file=log_base, echo=echo)
        driver.quit()
        exit()

    return driver