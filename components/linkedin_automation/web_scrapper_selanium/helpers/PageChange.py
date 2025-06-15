import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import streamlit as st

from utils.logger.EventLogger import log_message

def go_to_next_page(driver, page, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            next_btn = driver.find_element(By.XPATH, f'//button[@aria-label="Page {page + 1}"]')
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)         
        except NoSuchElementException:
            log_message("✔️ No more pages to scrape.", log_file=log_base, echo=echo)
            return True
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: PAGE CHANGER", log_file=log_base, echo=echo)
        driver.quit()
        exit()