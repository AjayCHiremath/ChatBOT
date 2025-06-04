# File: ChatBot.py

# ---{ Imports }---
import streamlit as st
import os

# ---{ Internal Component Imports }---
from components.pdf_summarizer.PDFSummarizer import run_pdf_summarizer
from components.linkedin_automation.ui.LinkedInMain import run_linkedin_jobs_apply
from components.ui.Sidebar import select_application
from utils.EnvironmentLoaders import load_environment
import components.linkedin_automation.web_scrapper_selanium.LinkedInApplier as lk
from components.linkedin_automation.jobs_applier_selanium.ChromeJobsApplier import start_external_apply

# ---{ App Class Definition }---
class ChatBotApp:
    def __init__(self):
        self.load_env()
        self.set_page_config()
        self.init_session_state()
        self.run()

    # ---{ Load required environment variables }---
    def load_env(self):
        load_environment([
            'LANGCHAIN_API_KEY',
            'LANGCHAIN_TRACING_V2',
            'LANGSMITH_ENDPOINT',
            'LANGCHAIN_PROJECT',
            'TOGETHER_API_KEY'
        ])

    # ---{ Streamlit page setup }---
    def set_page_config(self):
        st.set_page_config(layout="wide", page_icon=":shark:")

    # ---{ Initialize session state variables }---
    def init_session_state(self):
        defaults = {
            "chat_history": [],
            "generating_response": False,
            "run_chain": False,
            "current_input": "",
            "uploaded_pdfs": [],
            "file_upload_key": 0,
            "resume": [],
            "show_job_settings": True,
            "show_job_settings_ext": True,
            "job_settings_backup": {},
            "job_settings_backup_ext": {},
            "keys": {},
            "keys_ext": {},
            "applying_jobs": False,
            "stopped_jobs": False,
            "applying_jobs_ext": False,
            "stopped_jobs_ext": False,
            "completed_scrapping": False,
            "show_box2": False
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # ---{ Application logic entry point }---
    def run(self):
        # ---{ Sidebar: application selector }---
        select_application(disabled=st.session_state.generating_response)

        # ---{ Main title: display selected application name }---
        st.title(st.session_state.app_selector)

        # ---{ Route logic to selected application }---
        if st.session_state.app_selector == "PDF Summarizer":
            run_pdf_summarizer()
        elif st.session_state.app_selector == "LinkedIn Jobs Apply":
            run_linkedin_jobs_apply()
        else:
            st.info(":construction: This application module is under construction.")

# ---{ Entry Point }---
if __name__ == "__main__":
    ChatBotApp()
    if st.session_state.applying_jobs:
        lk.linkedin_jobs_applier()

    if os.path.exists("logs/jobs_applied/linkedin_jobs.xlsx"):
        st.session_state.completed_scrapping = True

    if st.session_state.applying_jobs_ext:
        start_external_apply(import_path="D:/Course/ChatBOT/logs/jobs_applied/linkedin_jobs.xlsx", log_base="logs/job_application_logs/logs_text/", echo=False)