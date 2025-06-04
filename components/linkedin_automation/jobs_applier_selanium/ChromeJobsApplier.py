import spacy
import pandas as pd
import streamlit as st

from components.linkedin_automation.jobs_applier_selanium.helpers.DataPreprocess import data_chunking, data_cleaning
from components.linkedin_automation.jobs_applier_selanium.data.configurations import section_map_data_preprocessing
from components.linkedin_automation.jobs_applier_selanium.helpers.ApplyForJobs import start_application_process


# ---{ Start external job application by reading and cleaning data }---
def start_external_apply(import_path="D:/Course/ChatBOT/logs/jobs_applied/linkedin_jobs.xlsx", log_base="logs/job_application_logs/logs_text/", echo=False):
    
    # ---{ Read job data from Excel }---
    jobs_data = pd.read_excel(io=import_path, index_col=0)

    # ---{ Load job settings from session state }---
    job_settings = {
        key: value
        for key, value in st.session_state.get("job_settings_backup_ext", {}).items()
        if key in st.session_state.get("keys_ext", [])
    }

    # ---{ Clean job data before application }---
    jobs_data = data_cleaning(jobs_data.reset_index(), job_settings, log_base, echo)

    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")

    # ---{ Making Chunks of Data for duplicate or repeated data columns }---
    jobs_data_chunks = data_chunking(jobs_data, nlp, section_map_data_preprocessing)

    start_application_process(jobs_data_chunks, log_base, echo)

