# ---{ Imports }---
import streamlit as st
import os
import boto3

# ---{ Streamlit Page Config }---
st.set_page_config(page_icon="🦈", layout="wide", initial_sidebar_state="auto")

# ---{ External Component Imports }---
from components.pdf_summarizer.PDFSummarizer import run_pdf_summarizer
from components.linkedin_automation.ui.LinkedInMain import run_linkedin_jobs_apply
from components.main_ui.Sidebar import select_application

from utils.env_loaders import load_environment
import components.linkedin_automation.web_scrapper_selanium.LinkedInApplier as lk
from components.linkedin_automation.jobs_applier_selanium.ChromeJobsApplier import start_external_apply
from utils.login_page.streamlit_login_auth_ui.login import login_ui

# ---{ Cached Setup Functions }---
@st.cache_resource
def load_env_variables():
    load_environment([
        'PINECONE_API_KEY', 'PINECONE_REGION', 'PINECONE_INDEX',
        'TOGETHER_API_KEY', 'TOGETHER_BASE_URL',
        'LANGCHAIN_API_KEY', 'LANGCHAIN_PROJECT',
        'LANGSMITH_TRACING', 'LANGSMITH_ENDPOINT',
        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION',
        'MY_S3_BUCKET', "COURIER_AUTH_TOKEN", "COMPANY_NAME",
        "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"
    ])

# ---{ App Class Definition }---
class ChatBotApp:
    def __init__(self):
        self.set_page_components()        
        self.init_session_state()
        self.run()

    # ---{ Initialize session state variables }---
    def init_session_state(self):
        defaults = {
            # Chat-related
            "chat_history": [],
            "generating_response": False,
            "run_chain": False,
            "current_input": "",
            "chat_history_store": {},
            "response_count": 0,
            "cooldown_until": None,
            "request_timestamps": None,
            "usage_history": None,

            # File/resume
            "file_upload_key": 0,
            "resume": [],
            "documents": None,
            "embed_docs": False,
            "embedding_complete": False,
            "embedded_and_vectorstore": None,

            # Job-related
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

            # UI-related
            "show_box2": False,

            # Auth
            "user_name": None,
            "aws_env": None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

                
    # ---{ Load CSS }---
    # ---{ Streamlit page setup }---
    @st.cache_resource
    def set_page_components(_self):
        with open(r"components/main_ui/background.css") as source_des:
            st.markdown(f'<style>{source_des.read()}</style>', unsafe_allow_html=True)

    # ---{ Application logic entry point }---
    def run(self):
        select_application(disabled=st.session_state.generating_response)
        st.title(st.session_state.app_selector)

        if st.session_state.app_selector == "PDF Summarizer":
            run_pdf_summarizer(echo=True)
        elif st.session_state.app_selector == "LinkedIn Jobs Apply":
            run_linkedin_jobs_apply()
        else:
            st.info(":construction: This application module is under construction.")

# ---{ Entry Point }---
if __name__ == "__main__":
    # Load environment variables and CSS
    load_env_variables()
    
    # Initialize AWS environment
    st.session_state.aws_env = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    
    # Initialize the login UI
    login_object = login_ui(company_name=os.getenv("COMPANY_NAME"))

    if login_object.build_login_ui():
        # Set session state variables based on login
        st.session_state.user_name = login_object.get_username()
        
        
        # Initialize the application
        ChatBotApp()

        # Check if the user is applying for LinkedIn jobs
        if st.session_state.applying_jobs:
            lk.linkedin_jobs_applier()

        if os.path.exists("logs/excel/linkedin_jobs.xlsx"):
            st.session_state.completed_scrapping = True

        if st.session_state.applying_jobs_ext:
            start_external_apply(
                import_path="logs/jobs_applied/linkedin_jobs.xlsx",
                log_base="logs/job_application_logs/logs_text/",
                echo=True)