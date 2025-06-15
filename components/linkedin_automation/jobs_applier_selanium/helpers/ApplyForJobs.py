#-------------------{Importing required modules}---------------------------
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from components.linkedin_automation.jobs_applier_selanium.helpers.LoginPage import send_workday_url, is_job_page_missing, click_apply_buttons, signup_or_signin
from components.linkedin_automation.jobs_applier_selanium.data.configurations import profile, my_experience_data, my_information_data
from components.linkedin_automation.jobs_applier_selanium.helpers.myInformationPage import my_information_page
from components.linkedin_automation.jobs_applier_selanium.helpers.myExperiencePage import my_experience_form
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped
from utils.logger.EventLogger import log_message

import time
import pyautogui

#-------------------{Main application process function}---------------------------
def start_application_process(profile_data, log_base="logs/job_application_logs/logs_text/", echo=False):
    #-------------------{Initialize Selenium driver and waits}---------------------------
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 5)
    short_wait = WebDriverWait(driver, 1)

    #-------------------{Extract application URLs that contain 'myworkdayjobs.com'}---------------------------
    urls = profile_data[profile_data["Application Link"].str.contains("myworkdayjobs.com", na=False)]["Application Link"]

    #-------------------{Iterate through each application link}---------------------------
    for i, url in enumerate(urls):
        #-------------------{Exit if the process is stopped}---------------------------
        exit_if_stopped(context="linkedin_jobs_applier", driver=driver, log_file=log_base, echo=echo)
        log_message(f"🌐 Visiting {i}: {url}", log_file=log_base, echo=echo)

        #-------------------{Open Workday URL and clear session data}---------------------------
        send_workday_url(driver, url)

        #-------------------{Check if the job page is missing and skip if so}---------------------------
        if is_job_page_missing(driver, short_wait):
            continue

        #-------------------{Click 'Apply' button if available}---------------------------
        if not click_apply_buttons(driver, wait, "//a[contains(text(), 'Apply')]"):
            continue
        time.sleep(2)

        #-------------------{Click 'Apply Manually' button if available}---------------------------
        if not click_apply_buttons(driver, wait, "//a[contains(text(), 'Apply Manually')]"):
            continue
        time.sleep(2)

        #-------------------{Handle signup or signin flow}---------------------------
        if not signup_or_signin(driver, wait, profile):
            print("❌ Failed to handle authentication flow — skipping.")
            continue

        #-------------------{Fill the 'My Information' page}---------------------------
        my_information_page(driver, wait, my_information_data, log_base, echo)

        #-------------------{Click 'Save and Continue' button on My Information page}---------------------------
        if not click_apply_buttons(driver, wait, "//button[@data-automation-id='pageFooterNextButton'][contains(text(), 'Save and Continue')]"):
            continue
        
        #-------------------{Log success of form submission}---------------------------
        print("✔ Saved form 1.")

        #-------------------{Fill the 'My Experience' form}---------------------------
        my_experience_form(driver, wait, short_wait, my_experience_data, log_base, echo)


        #-------------------{Prompt user for manual verification of submission}---------------------------
        if pyautogui.confirm(text='Correct??',title='Manual Auth Required',buttons=['Yes', 'No']) == 'Yes':
            print("✔ User confirmed authentication.")

            continue