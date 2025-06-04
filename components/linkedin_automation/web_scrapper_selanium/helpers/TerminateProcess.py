import streamlit as st
from utils.logger.EventLogger import log_message

# ------------------------------{Helper: Exit if user stops}------------------------------
def exit_if_stopped(context: str, driver, log_file="logs/login_page_logs/", echo=False):
    if st.session_state.stopped_jobs:
        log_message(f"🛑 Terminating Browser: {context}", log_file=log_file, echo=echo)
        driver.quit()
        exit()