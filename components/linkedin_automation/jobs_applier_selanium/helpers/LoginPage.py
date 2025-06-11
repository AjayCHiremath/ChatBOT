from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
# import pyautogui
import pygame

# -------------------{Function to open URL in Workday and clear local/session storage}---------------------------
def send_workday_url(driver, url, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        driver.get(url)
        time.sleep(2)
        print("🌐 Navigated to Workday URL.")
        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            driver.refresh()
            time.sleep(1)
            print("✔ Cleared cookies and local/session storage.")
        except Exception:
            print("⚠️ Failed to clear local/session storage.")
    except Exception:
        print("⚠️ Failed in send_workday_url. Skipping to next.")

# -------------------{Function to detect missing job page error}---------------------------
def is_job_page_missing(driver, short_wait, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        short_wait.until(lambda d: d.find_elements(By.XPATH, "//span[@data-automation-id='errorMessage']"))
        try:
            elements = driver.find_elements(By.XPATH, "//span[@data-automation-id='errorMessage']")
            for el in elements:
                if "doesn't exist" in el.text or "not available" in el.text.lower():
                    print(f"❌ Job error found: {el.text.strip()} — skipping.")
                    return True
        except Exception:
            print("⚠️ Failed while checking error message elements.")
    except TimeoutException:
        print("ℹ️ No missing job error detected.")
    except Exception:
        print("⚠️ Error during is_job_page_missing check.")
    return False

# -------------------{Function to click apply button}---------------------------
def click_apply_buttons(driver, wait, xpath, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        print(f"➡️ Trying to click: {xpath}")
        try:
            button = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", button)
                print("✔ Click successful.")
                return True
            except Exception:
                print("⚠️ Failed to scroll or click the button.")
        except (TimeoutException, NoSuchElementException):
            print(f"⚠️ Timeout or NoSuchElementException: Button not found for xpath: {xpath}")
    except Exception:
        print(f"⚠️ Unexpected error clicking button for xpath: {xpath}")
    return False

# -------------------{Function to tick consent checkbox if present}---------------------------
def tick_checkbox_if_present(driver, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='createAccountCheckbox']")
        if not checkbox.is_selected():
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", checkbox)
                print("✔ Ticked consent checkbox.")
                return True
            except Exception:
                print("⚠️ Failed to scroll or click checkbox.")
    except NoSuchElementException:
        print("ℹ️ Consent checkbox not found — skipping.")
    except Exception:
        print("⚠️ Unexpected error ticking consent checkbox.")
    return False

# -------------------{Function to check if page is Sign-In}---------------------------
def is_signin_page(driver):
    try:
        return bool(driver.find_elements(By.XPATH, "//h2[contains(text(), 'Sign In')]"))
    except Exception:
        print("⚠️ Failed checking for Sign-In page.")
        return False

# -------------------{Function to check if page is Create Account}---------------------------
def is_create_account_page(driver):
    try:
        return bool(driver.find_elements(By.XPATH, "//h2[contains(text(), 'Create Account')]"))
    except Exception:
        print("⚠️ Failed checking for Create Account page.")
        return False

# -------------------{Function to click Sign-In switch button}---------------------------
def try_click_signin_switch(driver, wait, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        switch_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='signInLink']")))
        driver.execute_script("arguments[0].click();", switch_button)
        print("🔁 Switched to Sign-In form.")
        time.sleep(2)
    except TimeoutException:
        print("⚠️ Switch to Sign-In button not found.")
    except Exception:
        print("⚠️ Unexpected error trying to switch to Sign-In.")

# -------------------{Function to click Create Account switch button}---------------------------
def try_click_create_account_switch(driver, wait, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        switch_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='createAccountLink']")))
        driver.execute_script("arguments[0].click();", switch_button)
        print("🔁 Switched to Create Account form.")
        time.sleep(2)
    except TimeoutException:
        print("⚠️ Switch to Create Account button not found.")
    except Exception:
        print("⚠️ Unexpected error trying to switch to Create Account.")

# -------------------{Function to fill email and password fields}---------------------------
def send_email_password(driver, wait, profile, verify_password=False, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[data-automation-id='email']")))
        email_input.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        email_input.send_keys(profile['email'])
        print("📧 Filled email.")
    except TimeoutException:
        print("⚠️ Timeout filling email field.")
    except Exception:
        print("⚠️ Unexpected error filling email field.")

    try:
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][data-automation-id='password'], input[type='password'][name='password']")
        password_input.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        password_input.send_keys(profile['password'])
        print("🔒 Filled password.")
    except NoSuchElementException:
        print("⚠️ Password field not found.")
    except Exception:
        print("⚠️ Unexpected error filling password field.")

    if verify_password:
        try:
            confirm_password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][data-automation-id='verifyPassword'], input[type='password'][name='verifyPassword']")
            confirm_password_input.send_keys(Keys.CONTROL + "a", Keys.DELETE)
            confirm_password_input.send_keys(profile['password'])
            print("🔒 Confirmed password.")
        except NoSuchElementException:
            print("⚠️ Confirm password field not found.")
        except Exception:
            print("⚠️ Unexpected error filling confirm password field.")

    try:
        tick_checkbox_if_present(driver)
    except Exception:
        print("⚠️ Error trying to tick consent checkbox.")

# -------------------{Function to play beep sound as an alert}---------------------------
def alert_user_beep(sound_file='D:/Course/ChatBOT/components/linkedin_automation/jobs_applier_selanium/notification/alert.mp3', repeat=3, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        pygame.mixer.init()
        print("⚠️ Alerting user that it requires manual authentication")
        for _ in range(repeat):
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    except Exception:
        print("⚠️ Failed to play alert sound.")

# -------------------{Function to handle manual authentication flow}---------------------------
def handle_manual_authentication(log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        alert_user_beep()
        print("⌛ Waiting for user manual authentication confirmation...")
        start_time = time.time()
        while time.time() - start_time < 300:
            try:
                print("5 minutes left for manual authentication confirmation...")
                # response = pyautogui.confirm(
                #     text='Have you completed manual authentication?',
                #     title='Manual Auth Required',
                #     buttons=['Yes', 'No']
                # )
                # if response == 'Yes':
                #     print("✔ User confirmed authentication.")
                #     return True
                # elif response == 'No':
                #     print("⏭️ User declined. Skipping job.")
                #     return False
                # else:
                #     time.sleep(5)
            except Exception:
                print("⚠️ Error during manual authentication prompt.")
        print("⏳ Timeout: No manual authentication confirmed.")
    except Exception:
        print("⚠️ Error during manual authentication flow.")
    return False

# -------------------{Function to handle sign-up or sign-in flow}---------------------------
def signup_or_signin(driver, wait, profile, timeout_seconds=60, log_base="logs/job_application_logs/logs_text/", echo=False):
    print("🚀 Attempting to sign up or sign in...")
    start_time = time.time()
    try:
        while time.time() - start_time < timeout_seconds:
            try:
                driver.switch_to.default_content()
            except Exception:
                print("⚠️ Failed to switch to default content.")

            try:
                if is_create_account_page(driver):
                    send_email_password(driver, wait, profile, verify_password=True)
                    try:
                        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Create Account']")))
                        driver.execute_script("arguments[0].click();", create_btn)
                        print("📝 Attempted account creation.")
                    except TimeoutException:
                        print("⚠️ Could not click 'Create Account' button.")
                    except Exception:
                        print("⚠️ Unexpected error clicking 'Create Account' button.")
                    time.sleep(2)

                    if is_signin_page(driver):
                        if handle_manual_authentication():
                            send_email_password(driver, wait, profile, verify_password=False)
                            try:
                                signin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Sign In']")))
                                driver.execute_script("arguments[0].click();", signin_btn)
                                print("🔐 Attempted sign in.")
                            except TimeoutException:
                                print("⚠️ Could not click 'Sign In' button.")
                            except Exception:
                                print("⚠️ Unexpected error clicking 'Sign In' button.")
                            time.sleep(2)
                        else:
                            break

                elif is_signin_page(driver):
                    send_email_password(driver, wait, profile, verify_password=False)
                    try:
                        signin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Sign In']")))
                        driver.execute_script("arguments[0].click();", signin_btn)
                        print("🔐 Attempted sign in.")
                    except TimeoutException:
                        print("⚠️ Could not click 'Sign In' button.")
                    except Exception:
                        print("⚠️ Unexpected error clicking 'Sign In' button.")
                    time.sleep(2)

                try:
                    if (
                        driver.find_elements(By.XPATH, "//h1[contains(text(), 'Something went wrong')]") or
                        driver.find_elements(By.XPATH, "//h2[contains(text(), 'My Information')]") or
                        driver.find_elements(By.CSS_SELECTOR, "button[data-automation-id='pageFooterNextButton']")
                    ):
                        print("✔ Success: Detected entry into application flow or profile page.")
                        return True
                except Exception:
                    print("⚠️ Error checking page state for success.")

                try:
                    if is_create_account_page(driver):
                        try_click_signin_switch(driver, wait)
                    elif is_signin_page(driver):
                        try_click_create_account_switch(driver, wait)
                except Exception:
                    print("⚠️ Error switching between Create Account and Sign In forms.")

                time.sleep(1)
            except Exception:
                print("⚠️ Unexpected error during signup/signin loop.")

        print("⏳ Timeout: did not reach 'My Information' page.")
    except Exception:
        print("❌ Error during signup/signin process.")
    return False