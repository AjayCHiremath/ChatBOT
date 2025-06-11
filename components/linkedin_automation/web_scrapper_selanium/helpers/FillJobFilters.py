# -----{ Required Imports }------
import time
import copy
import streamlit as st

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from utils.logger.EventLogger import log_message
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped

# -----{ Click the "All filters" button and wait for the panel to load }------
def click_all_filters_button(driver, wait, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            filters_btn_xpath = "//button[normalize-space()='All filters']"
            wait.until(EC.element_to_be_clickable((By.XPATH, filters_btn_xpath))).click()
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.XPATH,
                "//div[contains(@class, 'search-reusables__secondary-filters')]"
            )))
        except Exception as e:
            log_message(f"❌ Failed to open All Filters panel: {e}",
                        log_file=log_base , echo=echo)
            raise
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: ALL FILTERS BTN CLICK", log_file=log_base, echo=echo)
        driver.quit()
        exit()
    return driver


#-----------------------{ Toggle switch-based filters }--------------------------
def switch_based_filter(driver, wait, filter_group, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            
            log_message(f"🔎 Looking for toggle switch: {filter_group}", log_file=log_base, echo=echo)

            fieldset_xpath = f'.//h3[normalize-space()="{filter_group}"]/ancestor::fieldset'
            fieldset = wait.until(EC.presence_of_element_located((By.XPATH, fieldset_xpath)))
            
            toggle_btn = WebDriverWait(fieldset, 5).until(lambda el: el.find_element(By.XPATH, './/input[@role="switch"]'))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", toggle_btn)
            driver.execute_script("arguments[0].click();", toggle_btn)

            msg = f"✅ Toggled: {filter_group}"
        except Exception as e:
            msg = f"⚠️ Toggle fallback failed: {filter_group} → {e}"

        log_message(msg, log_file=log_base, echo=echo)
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: ALL FILTERS BTN CLICK", log_file=log_base, echo=echo)
        driver.quit()
        exit()
    return driver

#-----------------------{ Select radio-based filter options }--------------------------
def radio_based_filter(driver, wait, val, filter_label, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        try:
            log_message(f"🔎 Applying radio filter: {filter_label} → {val}", log_file=log_base, echo=echo)

            label_xpath = (
                f"//li[contains(@class, 'search-reusables__filter-value-item')]"
                f"[.//span[contains(normalize-space(), '{val}')]]//label"
            )

            label_elem = wait.until(EC.element_to_be_clickable((By.XPATH, label_xpath)))
            log_message("✅ Found label element. Scrolling and clicking...", log_file=log_base, echo=echo)

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label_elem)
            driver.execute_script("arguments[0].click();", label_elem)

            msg = f"✅ Applied: {filter_label} → {val}"
        except Exception as e:
            msg = f"⚠️ {filter_label} filter failed: {e}"

        log_message(msg, log_file=log_base, echo=echo)
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: ALL FILTERS BTN CLICK", log_file=log_base, echo=echo)
        driver.quit()
        exit()
    return driver

#-----------------------{ Addable Input Filter Function }--------------------------
def handle_addable_input_filter(driver, short_wait, label, value, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        label = label.lower()
        pre_label = "Add an" if label == "industry" else "Add a"
        placeholder = f"{pre_label} {label}"

        input_xpath = f'(.//input[@placeholder="{placeholder}"])[1]'
        btn_xpath = f'//span[normalize-space()="{placeholder}"]'

        log_message(f"🔎 Trying to add: {value} to {label}", log_file=log_base, echo=echo)

        try:
            try:
                # Try the full button first
                add_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
                add_btn.click()
                time.sleep(0.3)
            except Exception as e_btn:
                log_message(f"⚠️ Primary button click failed:", log_file=log_base, echo=echo)

            # Locate and interact with input
            search_input = short_wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.DELETE)
            search_input.send_keys(value)
            time.sleep(1)

            search_input.send_keys(Keys.DOWN)
            time.sleep(0.5)
            search_input.send_keys(Keys.ENTER)
            time.sleep(0.2)

            # Post-clear (depends on UI behavior)
            try:
                search_input = short_wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
                search_input.send_keys(Keys.CONTROL + "a")
                search_input.send_keys(Keys.DELETE)
            except:
                log_message("⚠️ Input disappeared after selection (normal)", log_file=log_base, echo=echo)

            log_message(f"✅ Added '{value}' to {label} filter", log_file=log_base, echo=echo)

        except Exception as final_error:
            log_message(f"⚠️ Failed to add '{value}' to {label}: {final_error}", log_file=log_base, echo=echo)
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: ALL FILTERS BTN CLICK", log_file=log_base, echo=echo)
        driver.quit()
        exit()
    return driver


#-----------------------{ Handle multi-select filter selections }--------------------------
def multiselect_based_filter(driver, wait, short_wait, values, filter_group, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        addedable_btns = {"preferred_companies": "Company", "industry": "Industry", "job_function": "Job function"}
        
        if isinstance(values, list):
            values = values
        elif isinstance(values, str) and (filter_group.strip() not in addedable_btns.values()):
            values = [v.strip() for v in values.split(",")]
        elif isinstance(values, str) and (filter_group.strip() in addedable_btns.values()):
            values = [v.strip() for v in values.split("|")]

        for val in values:
            exit_if_stopped(context="🛑 Terminating Browser: ALL FILTERS BTN CLICK", driver=driver, log_file=log_base, echo=echo)

            label_text = f"{filter_group} → {val}"
            success = False

            try:
                log_message(f"🔎 Looking for filter group: {filter_group}", log_file=log_base, echo=echo)
                fieldset_xpath = f'//h3[normalize-space()="{filter_group}"]/ancestor::fieldset'
                fieldset = wait.until(EC.presence_of_element_located((By.XPATH, fieldset_xpath)))

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fieldset)
                log_message(f"✅ Found fieldset for: {filter_group}", log_file=log_base, echo=echo)

                if filter_group.strip() in addedable_btns.values():
                    driver = handle_addable_input_filter(driver, short_wait, filter_group, val, log_base, echo)
                    continue

                # Now search labels inside the fieldset
                label_elements = wait.until(lambda d: fieldset.find_elements(By.XPATH, './/label'))
                log_message(f"🔍 Searching for value: {val} in {len(label_elements)} label(s)", log_file=log_base, echo=echo)

                for label in label_elements:
                    exit_if_stopped("🛑 Terminating Browser: ALL FILTERS BTN CLICK", driver, log_base)

                    try:
                        # Wait for the span to be attached and accessible
                        span = label.find_element(By.XPATH, './/span[@aria-hidden="true"]')
                        label_text_value = span.text.strip().lower()
                        val_lower = val.strip().lower()

                        log_message(f"   ⏵ Comparing with: {label_text_value}", log_file=log_base, echo=echo)

                        if val_lower in label_text_value:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                            short_wait.until(lambda d: label.is_displayed() and label.is_enabled())
                            driver.execute_script("arguments[0].click();", label)
                            success = True
                            log_message(f"✅ Applied: {label_text}", log_file=log_base, echo=echo)
                            break

                    except Exception as e:
                        log_message(f"⚠️ Span or click failed for label '{val}': {e}", log_file=log_base, echo=echo)
                        continue

                if not success:
                    log_message(f"❌ Could not apply: {label_text}", log_file=log_base, echo=echo)

            except TimeoutException as e:
                log_message(f"⏰ Timeout waiting for filter group or label: {label_text} → {e}", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"⚠️ Unexpected error during filter selection: {label_text} → {e}", log_file=log_base, echo=echo)

    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: ALL FILTERS BTN CLICK", log_file=log_base, echo=echo)
        driver.quit()
        exit()

    return driver 


# ---{ Formatting Salary value }---
def map_salary_to_linkedin_format(salary, country_raw):
    country = country_raw.split(",")[0].strip().lower()

    # Country-specific minimum salary thresholds
    thresholds = {
        "united kingdom": 20000,
        "uk": 20000,
        "england": 20000,
        "united states": 40000,
        "usa": 40000,
        "us": 40000,
        "canada": 30000,
        "india": 300000,
        "germany": 30000,
        "australia": 40000,
        "france": 30000,
        "japan": 3000000
    }

    # Currency formatting per country
    currency_formats = {
        "united kingdom": lambda s: f"£{s:,}+",
        "uk": lambda s: f"£{s:,}+",
        "england": lambda s: f"£{s:,}+",
        "united states": lambda s: f"${s:,}+",
        "usa": lambda s: f"${s:,}+",
        "us": lambda s: f"${s:,}+",
        "canada": lambda s: f"${s:,} CAD+",
        "india": lambda s: f"₹{s:,}+",
        "germany": lambda s: f"€{s:,}+",
        "australia": lambda s: f"${s:,} AUD+",
        "france": lambda s: f"{s:,} €+",
        "japan": lambda s: f"¥{s:,}+"
    }

    min_salary = thresholds.get(country)
    formatter = currency_formats.get(country)

    if min_salary is None or formatter is None:
        return f"{salary:,}+"

    return formatter(salary) if salary >= min_salary else ""


# -----{ Apply filters using session state values and log them }------
def apply_all_filters(driver, wait, short_wait, session_data, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:
        session_data_ = copy.deepcopy(session_data)
        log_message("📦 Applying filters with session data:", log_file=log_base, echo=echo)

        for key, val in session_data_.items():
            exit_if_stopped(context="🛑 Terminating Browser: ALL FILTERS BTN CLICK", driver=driver, log_file=log_base)

            log_message(f"  {key}: {val}", log_file=log_base, echo=echo)
            if key == "salary":
                session_data_[key] = map_salary_to_linkedin_format(session_data_[key], session_data_["search_location"])

        filter_mapping = {
            "preferred_companies": "Company",
            "experience_level": "Experience level",
            "job_type": "Job type",
            "workplace_type": "Remote",
            "industry": "Industry",
            "location": "Location",
            "job_function": "Job function",
            "job_titles": "Title",
            "benefits": "Benefits",
            "commitments": "Commitments",
            "under_10": "Under 10 applicants",
            "in_network": "In your network",
            "fair_chance": "Fair Chance Employer",
            "sort_by": "Sort by",
            "salary": "Salary",
            "date_posted": "Date Posted" 
        }
        
        switch_based_filters = {"under_10","in_network","fair_chance"}
        multiselect_filters = {"preferred_companies", "experience_level","job_type","workplace_type",
                               "industry","location","job_function","job_titles","benefits","commitments"}
        radio_filters = {"sort_by","salary","date_posted"}

        for key, values in session_data_.items():
            exit_if_stopped(context="🛑 Terminating Browser: ALL FILTERS BTN CLICK", driver=driver, log_file=log_base)

            if key not in filter_mapping or not values:
                continue
            
            filter_group = filter_mapping[key]
            if key in multiselect_filters:
                driver = multiselect_based_filter(driver, wait, short_wait, values, filter_group, log_base, echo)
            elif key in radio_filters:
                driver = radio_based_filter(driver, wait, values, filter_group, log_base, echo)
            elif key in switch_based_filters:
                driver = switch_based_filter(driver, wait, filter_group, log_base, echo)
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: MAIN JOB SEARCH TERMINATED", log_file=log_base, echo=echo)
        driver.quit()
        exit()

    return driver