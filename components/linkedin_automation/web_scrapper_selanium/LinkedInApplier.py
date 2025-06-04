#-----------------------{ Imports }--------------------------
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from components.linkedin_automation.web_scrapper_selanium.helpers.AppLogin import login_to_linkedin
from components.linkedin_automation.web_scrapper_selanium.helpers.JobSearch import go_to_job_search
from components.linkedin_automation.web_scrapper_selanium.helpers.FillJobFilters import click_all_filters_button, apply_all_filters
from components.linkedin_automation.web_scrapper_selanium.helpers.ApplyJobFilters import apply_filters
from components.linkedin_automation.web_scrapper_selanium.helpers.ScrapeData import scrape_all_jobs
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped
from utils.logger.EventLogger import log_message

import pyautogui
import pandas as pd
import streamlit as st
import os
import random

#-----------------------{ Apply filter }--------------------------
def applied_filters(driver, export_path, log_base="logs/login_page_logs/", echo=False):
    wait, short_wait = WebDriverWait(driver, 1), WebDriverWait(driver, 0.5)

    driver = apply_filters(driver, log_base, echo)
    driver, df = scrape_all_jobs(driver, wait, short_wait, log_base, echo)

    update_or_append_excel(df, export_path)
    log_message(f"📦 Exported data to: {export_path}", log_file=log_base, echo=echo)
    return driver

#-----------------------{ Add Scrapped jobs in excel }--------------------------
def update_or_append_excel(df_new, export_path):
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    df_new = pd.DataFrame(df_new)
    df_new.set_index("Job ID", inplace=True)

    # If file exists, load and update
    if os.path.exists(export_path):
        df_existing = pd.read_excel(export_path)
        df_existing.set_index("Job ID", inplace=True)

        # Update or append
        df_updated = df_existing.combine_first(df_new)
        df_updated.update(df_new)
    else:
        df_updated = df_new

    # Save back to file
    df_updated.reset_index().to_excel(export_path, index=False)


#-----------------------{ Job Application Logic }--------------------------
def linkedin_jobs_applier():
    log_base = "logs/login_page_logs/"
    export_path = "logs/jobs_applied/linkedin_jobs.xlsx"
    echo = True

    #-----------------------{ Initialize Chrome WebDriver }--------------------------
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 5)

    #-----------------------{ Log into LinkedIn }--------------------------
    login_to_linkedin(driver, log_base, echo)
    
    search_terms_string = st.session_state.get("job_settings_backup", {}).get("search_terms", "")
    job_details = [term.strip() for term in search_terms_string.split(",") if term.strip()]

    randomize = st.session_state.get("job_settings_backup", {}).get("randomize", False)
    if randomize:
        random.shuffle(job_details)

    for job_name in job_details:
        exit_if_stopped(context="🛑 Terminating Browser: ALL FILTERS BTN CLICK", driver=driver, log_file=log_base, echo=echo)

        #-----------------------{ Open LinkedIn Jobs Page and Search }--------------------------
        driver.get("https://www.linkedin.com/jobs/")
        
        driver = go_to_job_search(driver=driver, job_keyword=job_name,
                                        log_base=log_base, echo=echo)

        #-----------------------{ Click "All filters" }--------------------------
        driver = click_all_filters_button(driver, log_base, echo)

        #-----------------------{ Select all filters from session }--------------------------
        short_wait = WebDriverWait(driver, 0.5)
        driver = apply_all_filters(driver, wait, short_wait, st.session_state.get("job_settings_backup", {}), log_base, echo)

        #-----------------------{ Show confirmation dialog with applied filters }--------------------------
        all_applied = pyautogui.confirm(
                text="Did all the filters you wanted were applied?\n",
                title="✅ Filters Applied",
                buttons=["Yes","No"]
            )
        
        if all_applied=="Yes":
            driver = applied_filters(driver, export_path, log_base, echo)
        else:
            corrected = pyautogui.confirm(
                text="Correct the filters manually and click Okay. (Only when done)\n Don't click on 'Show Results'",
                title="✅ Corrected Filters",
                buttons=["Okay"]
            )
            if corrected == "Okay":
                driver = applied_filters(driver, export_path, log_base, echo)