import os
import time
import pickle
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.logger.EventLogger import log_message
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped


# ------{Check if user is already logged into LinkedIn}------
def is_loggedIn(driver):
    return "linkedin.com/feed" in driver.current_url


# ------{Save cookies for future use}------
def save_cookies(driver, cookies_file, log_base, echo):
    try:
        os.makedirs(os.path.dirname(cookies_file), exist_ok=True)
        with open(cookies_file, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
        log_message(message="💾 Cookies saved for future sessions.", log_file=log_base, echo=echo)
    except Exception as e:
        log_message(message=f"⚠️ Failed to save cookies: {e}", log_file=log_base, echo=echo)


# ------{Wait for 2FA and login verification}------
def wait_for_2fa_and_save(driver, cookies_file, log_base, echo, max_wait=120):
    start_time = time.time()
    while True:
        # ------{Abort login if user stops the process}------
        exit_if_stopped(context="LOGIN PAGE", driver=driver, log_file=log_base, echo=echo)

        # ------{Check if login was successful}------
        if is_loggedIn(driver):
            log_message(message="✔️ 2FA completed. Logged in.", log_file=log_base, echo=echo)
            # ------{Save cookies for future use}------
            save_cookies(driver, cookies_file, log_base, echo)
            break

        # ------{Timeout after waiting too long for 2FA}------
        if time.time() - start_time > max_wait:
            raise TimeoutError("⏳ 2FA timeout: Login not completed.")

        time.sleep(2)


# ------{Login to LinkedIn using cookies or manual login}------
def login_to_linkedin(driver, log_base="logs/login_page_logs/", echo=True):
    # ------{Proceed only if job application mode is active}------
    if st.session_state.applying_jobs:
        cookies_file = 'logs/cookies/ajay_cookies.pkl'

        try:
            # ------{Visit LinkedIn homepage}------
            driver.get("https://www.linkedin.com/")
            time.sleep(1)

            # ------{Try loading cookies if available}------
            if os.path.exists(cookies_file):
                with open(cookies_file, 'rb') as f:
                    cookies = pickle.load(f)

                for cookie in cookies:
                    cookie.pop('sameSite', None)  # Remove attribute if present
                    driver.add_cookie(cookie)

                # ------{Refresh to apply cookies and validate login}------
                driver.refresh()
                time.sleep(2)

                if is_loggedIn(driver):
                    log_message(message="✔️ Logged in using saved cookies.", log_file=log_base, echo=echo)
                    return
                else:
                    log_message(message="⚠️ Saved cookies failed, attempting manual login.", log_file=log_base, echo=echo)

            # ------{If cookies failed or not found, perform manual login}------
            driver.get("https://www.linkedin.com/login")
            time.sleep(2)

            # ------{Enter credentials from session state}------
            email_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")

            email_input.send_keys(st.session_state.email)
            password_input.send_keys(st.session_state.password)
            password_input.send_keys(Keys.RETURN)

            log_message(message="🔐 Login submitted. Waiting for 2FA...", log_file=log_base, echo=echo)

            # ------{Wait for 2FA and login verification}------
            wait_for_2fa_and_save(driver, cookies_file, log_base, echo)

        # ------{Handle login failure due to exception}------
        except Exception as e:
            log_message(message=f"❌ Login failed: {e}", log_file=log_base, echo=echo)
            driver.quit()
            exit()

    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: Login Page", log_file=log_base, echo=echo)
        driver.quit()
        exit()