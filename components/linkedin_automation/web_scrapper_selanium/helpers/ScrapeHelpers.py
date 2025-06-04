from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped
from utils.logger.EventLogger import log_message

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import streamlit as st


# ------------------------------{Helper: Safe Text Extraction}------------------------------
def safe_get_text(driver, short_wait, by, selector, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)
    try:
        element = short_wait.until(EC.presence_of_element_located((by, selector)))
        text = element.text.strip()
        return driver, short_wait, text if text else None
    except (TimeoutException, NoSuchElementException) as e:
        log_message(f"⚠️ safe_get_text failed for {selector}: {e}", log_file=log_base, echo=echo)
        return driver, short_wait, None


# ------------------------------{Extract Company Name with Fallbacks}------------------------------
def extract_company_name(driver, short_wait, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)

    company = None

    selectors = [
        'div.job-details-jobs-unified-top-card__company-name a',  # Modern LinkedIn layout
        'div.artdeco-entity-lockup__subtitle span',               # Common subtitle
        'div.artdeco-entity-lockup__title a',                     # Older layout
    ]

    for selector in selectors:
        try:
            el = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            company = el.text.strip()
            if company:
                return driver, short_wait, company
        except (TimeoutException, NoSuchElementException):
            continue

    log_message("⚠️ Company name not found using known selectors", log_base, echo)
    return driver, short_wait, None


# ------------------------------{Extract About Company Section with Fallbacks}------------------------------
def extract_about_company(driver, wait, short_wait, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)

    # Primary selector - used in latest UI
    try:
        about_section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p.jobs-company__company-description')))
        div_inside = WebDriverWait(about_section, 2).until(
            lambda el: el.find_element(By.CSS_SELECTOR, 'div')
        )
        return driver, wait, short_wait, div_inside.text.strip()
    except Exception as e:
        log_message(f"⚠️ Primary About selector failed: {e}", log_base, echo)

    # Fallback 1 - from older or alternate layout
    try:
        about_section_fallback = short_wait.until(
            EC.presence_of_element_located((By.XPATH, '//section[contains(@class, "about-the-company")]'))
        )
        return driver, wait, short_wait, about_section_fallback.text.strip()
    except TimeoutException:
        pass
    except Exception as e:
        log_message(f"⚠️ Fallback 1 failed: {e}", log_file=log_base, echo=echo)

    # Fallback 2 - very old layout (show-more-less-html__markup)
    try:
        about_legacy = short_wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.show-more-less-html__markup'))
        )
        return driver, wait, short_wait, about_legacy.text.strip()
    except TimeoutException:
        pass
    except Exception as e:
        log_message(f"⚠️ Fallback 2 failed: {e}", log_file=log_base, echo=echo)

    return driver, wait, short_wait, None


# ------------------------------{Extract Application Info: Type, Label, Link}------------------------------
def extract_application_info(driver, wait, short_wait, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)

    try:
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.jobs-apply-button--top-card button')))
        aria_label = button.get_attribute('aria-label') or ""

        # External application (opens new tab)
        if 'company website' in aria_label.lower():
            original_window = driver.current_window_handle
            log_message("🌐 Opening external application link...", log_base, echo)

            try:
                button.click()
                time.sleep(0.5)
                windows = driver.window_handles

                if len(windows) > 1:
                    for win in windows:
                        exit_if_stopped("SCRAPPER", driver, log_base, echo)

                        if win != original_window:
                            driver.switch_to.window(win)
                            time.sleep(3)
                            try:
                                short_wait.until(lambda d: d.current_url.startswith("http"))
                            except TimeoutException:
                                log_message("⚠️ New tab URL did not load in time.", log_base, echo)
                            external_link = driver.current_url
                            driver.close()
                            driver.switch_to.window(original_window)
                            return driver, wait, short_wait, {
                                "Application Type": "External",
                                "Application Label": aria_label.strip(),
                                "Application Link": external_link
                            }
            except Exception as e:
                log_message(f"⚠️ Failed to open external application link: {e}", log_base, echo)
                return driver, wait, short_wait, {
                    "Application Type": "External",
                    "Application Label": aria_label.strip(),
                    "Application Link": None
                }

        # Easy Apply (stays on LinkedIn)
        elif 'easy apply' in aria_label.lower():
            return driver, wait, short_wait, {
                "Application Type": "Easy Apply",
                "Application Label": aria_label.strip(),
                "Application Link": driver.current_url
            }

        # Default fallback
        return driver, wait, short_wait, {
            "Application Type": "Unknown",
            "Application Label": aria_label.strip(),
            "Application Link": driver.current_url
        }

    except Exception as e:
        log_message(f"⚠️ Failed to extract application info: {e}", log_base, echo)
        return driver, wait, short_wait, {
            "Application Type": "Not Found",
            "Application Label": None,
            "Application Link": None
        }


# ------------------------------{Extract Recruiters from Hiring Team Section}------------------------------
def extract_people_and_recruiters(driver, wait, short_wait, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)

    recruiters = []

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.job-details-module div.artdeco-card')))
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.job-details-module div.artdeco-card')
        
        for card in cards:
            exit_if_stopped("SCRAPPER", driver, log_base, echo)

            try:
                header_el = short_wait.until(lambda d: card.find_element(By.TAG_NAME, 'h2'))
                header_text = header_el.text.lower()
            except:
                continue

            if "meet the hiring team" in header_text:
                people = card.find_elements(By.CSS_SELECTOR, 'a[href*="linkedin.com/in/"]')
                for person in people:
                    exit_if_stopped("SCRAPPER", driver, log_base, echo)
                    try:
                        name_el = short_wait.until(lambda d: person.find_element(By.TAG_NAME, 'strong'))
                        name = name_el.text.strip()
                        profile = person.get_attribute('href')
                        title_el = short_wait.until(lambda d: person.find_element(By.XPATH, './/following-sibling::div'))
                        title = title_el.text.strip()

                        recruiters.append({
                            "name": name,
                            "title": title,
                            "profile_url": profile
                        })
                    except:
                        continue
    except Exception as e:
        log_message(f"⚠️ Failed to parse people/recruiters: {e}", log_base, echo)

    return driver, wait, short_wait, recruiters


# ------------------------------{Extract Preferences & Skills from Modal}------------------------------
def parse_job_preferences_and_skills(driver, short_wait, log_base="logs/login_page_logs/", echo=False):
    exit_if_stopped("SCRAPPER", driver, log_base, echo)

    try:
        button = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.job-details-preferences-and-skills')))
        driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
    except Exception as e:
        log_message(f"⚠️ Could not open preferences/skills modal: {e}", log_base, echo)

    salary = workplace_type = job_type = None
    skills = []

    modal_sections = driver.find_elements(By.CSS_SELECTOR, '.job-details-preferences-and-skills__modal-section')
    for section in modal_sections:
        exit_if_stopped("SCRAPPER", driver, log_base, echo)
        try:
            header = section.find_element(By.TAG_NAME, 'h3').text.strip().lower()
            items = section.find_elements(By.CSS_SELECTOR, 'ul li')
            for item in items:
                exit_if_stopped("SCRAPPER", driver, log_base, echo)
                text_el = item.find_element(By.CSS_SELECTOR, 'span.text-body-small')
                text = text_el.text.strip()
                if 'preference' in header:
                    if '£' in text or '$' in text or '₹' in text:
                        salary = text
                    elif 'time' in text.lower():
                        job_type = text
                    elif any(w in text for w in ['Hybrid', 'Remote', 'On-site']):
                        workplace_type = text
                elif 'skill' in header:
                    skills.append(text)
        except Exception as e:
            log_message(f"⚠️ Error parsing modal section: {e}", log_base, echo)
            continue

    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
        log_message("✅ Closed preferences & skills modal.", log_base, echo)
    except Exception as e:
        log_message(f"⚠️ Failed to close modal with ESC: {e}", log_base, echo)

    return driver, salary, workplace_type, job_type, skills


# ------------------------------{Main: Scrape Full Job Data per Card}------------------------------
def scrape_job_data(driver, wait, short_wait, job_id, applied_status, log_base="logs/login_page_logs/", echo=False):
    if st.session_state.applying_jobs:

        job_data = {'Job ID': job_id, 'Applied': applied_status}
        driver, short_wait, job_data['Job Title'] = safe_get_text(driver, short_wait, By.CSS_SELECTOR, 'h1', log_base, echo)
        driver, short_wait, job_data['Company Name'] = extract_company_name(driver, short_wait, log_base, echo)
        driver, short_wait, job_data['Location'] = safe_get_text(driver, short_wait, By.XPATH, '//span[contains(@class, "tvm__text--low-emphasis") and contains(text(), ",")]', log_base, echo)
        driver, short_wait, job_data['Date Posted'] = safe_get_text(driver, short_wait, By.XPATH, '//span[contains(@class, "tvm__text--positive")]//span', log_base, echo)
        driver, short_wait, job_data['Applicants'] = safe_get_text(driver, short_wait, By.XPATH, '//span[contains(text(), "applicant")]', log_base, echo)

        driver, salary, workplace_type, job_type, skills = parse_job_preferences_and_skills(driver, short_wait, log_base, echo)
        job_data['Salary'] = salary
        job_data['Workplace Type'] = workplace_type
        job_data['Job Type'] = job_type
        job_data['Skills'] = skills

        driver, short_wait, job_data['Job Description'] = safe_get_text(driver, short_wait, By.ID, 'job-details', log_base, echo)
        driver, wait, short_wait, job_data['Recruiters'] = extract_people_and_recruiters(driver, wait, short_wait, log_base, echo)
        driver, wait, short_wait, job_data['About Company'] = extract_about_company(driver, wait, short_wait, log_base, echo)

        driver, wait, short_wait, application_info = extract_application_info(driver, wait, short_wait, log_base, echo)
        job_data.update(application_info)

        return driver, wait, short_wait, job_data
    
    else:
        # ------{If applying_jobs flag is off, exit cleanly}------
        log_message(message="🛑 Terminating Browser: JOB SCRAPER", log_file=log_base, echo=echo)
        driver.quit()
        exit()