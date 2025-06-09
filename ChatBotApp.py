# ---{ Imports }---
import streamlit as st
import os

# ---{ Internal Component Imports }---
from components.pdf_summarizer.PDFSummarizer import run_pdf_summarizer
from components.linkedin_automation.ui.LinkedInMain import run_linkedin_jobs_apply
from components.main_ui.Sidebar import select_application
from utils.EnvLoaders import load_environment
import components.linkedin_automation.web_scrapper_selanium.LinkedInApplier as lk
from components.linkedin_automation.jobs_applier_selanium.ChromeJobsApplier import start_external_apply
from utils.logger.SessionStatePersistence import load_session_state, save_session_state
from utils.login_page.streamlit_login_auth_ui.login import login_ui

# ---{ App Class Definition }---
class ChatBotApp:
    def __init__(self):
        self.load_env()
        self.set_page_components()
        self.init_session_state()
        self.run()

    # ---{ Load required environment variables }---
    def load_env(self):
        load_environment([
            'PINECONE_API_KEY',
            'PINECONE_REGION',
            'PINECONE_INDEX',
            'TOGETHER_API_KEY',
            'TOGETHER_BASE_URL',
            'LANGCHAIN_API_KEY',
            'LANGCHAIN_PROJECT',
            'LANGSMITH_TRACING',
            'LANGSMITH_ENDPOINT',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_DEFAULT_REGION',
            'MY_S3_BUCKET',
            'OBJECT_KEY',
            "COURIER_AUTH_TOKEN",
            "COMPANY_NAME",
        ])

    # ---{ Streamlit page setup }---
    def set_page_components(self):
        with open(r"components\main_ui\background.css") as source_des:
            st.markdown(f'<style>{source_des.read()}</style>', unsafe_allow_html=True)
    # ---{ Initialize session state variables }---
    def init_session_state(self):
        defaults = {
            "chat_history": [],
            "generating_response": False,
            "run_chain": False,
            "current_input": "",
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
            "show_box2": False,
            "embedding_complete": False,
            "embedded_and_vectorstore": None,
            "documents": None,
            "chat_history_store": {}
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
            run_pdf_summarizer(echo=True)
        elif st.session_state.app_selector == "LinkedIn Jobs Apply":
            run_linkedin_jobs_apply()
        else:
            st.info(":construction: This application module is under construction.")

        # Save Session State Persistenly
        save_session_state()

# ---{ Entry Point }---
if __name__ == "__main__":
    LOGGED_IN = login_ui(auth_token=os.getenv("COURIER_AUTH_TOKEN"), company_name=os.getenv("COMPANY_NAME"))
    if LOGGED_IN:
        ChatBotApp()
        if st.session_state.applying_jobs:
            lk.linkedin_jobs_applier()

        if os.path.exists("logs/jobs_applied/linkedin_jobs.xlsx"):
            st.session_state.completed_scrapping = True

        if st.session_state.applying_jobs_ext:
            start_external_apply(import_path="D:/Course/ChatBOT/logs/jobs_applied/linkedin_jobs.xlsx", log_base="logs/job_application_logs/logs_text/", echo=False)
    else:
        st.info("🔒 Please logIn/create account to continue.")