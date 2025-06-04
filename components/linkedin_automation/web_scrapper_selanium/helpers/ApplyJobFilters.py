# ---------------------{ Imports }---------------------
import streamlit as st

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger.EventLogger import log_message

# ---------------------{ Function: Apply LinkedIn Job Filters }---------------------
def apply_filters(driver, log_base="logs/login_page_logs/", echo=False):
    
    # ---------------------{ Proceed only if job application is active }---------------------
    if st.session_state.applying_jobs:
        wait = WebDriverWait(driver, 2)
        try:
            # ---------------------{ Click the "Show results" button after setting filters }---------------------
            show_results_btn: WebElement = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]')
                )
            )
            show_results_btn.click()

        except Exception as e:
            # ---------------------{ Log failure to click filter button }---------------------
            log_message(f"❌ Failed to click 'Show results': {e}", log_file=log_base, echo=echo)
    else:
        # ---------------------{ If 'applying_jobs' flag is off, terminate cleanly }---------------------
        log_message(message="🛑 Terminating Browser: Apply Filters", log_file=log_base, echo=echo)
        driver.quit()
        exit()
        
    return driver