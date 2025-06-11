import pandas as pd
import streamlit as st

from components.linkedin_automation.ui.LoginPage import login_page
from components.linkedin_automation.ui.ConfirmRefixValues import create_confirm, create_refix
from components.linkedin_automation.ui.ResumeUploader import get_resume
from components.linkedin_automation.ui.LinkedInJobDetails import get_job_settings
from components.linkedin_automation.ui.ExternalJobDetails import get_ext_job_settings

def confirm_refix_buttons(sjs="show_job_settings",cc_keys=["confirm_selections", ["show_job_settings", "job_settings_backup", "keys"]], 
                          cr_keys=["fix_selections", ["show_job_settings", "job_settings_backup"]],
                          lp_keys=["email", "password",'apply_jobs','stop_jobs'],
                          apj_keys="apply_jobs", stj_keys="stop_jobs",
                          asj_keys=["applying_jobs", "stopped_jobs"]):

    # ---{ Confirm and Refix buttons }---
    with st.container(border=True):
        col1, col2 = st.columns(2)

        create_confirm(col1, disabled=not st.session_state[sjs], keys=cc_keys)
        create_refix(col2, disabled=st.session_state.generating_response, keys=cr_keys)

    # ---{ If settings confirmed, show login screen }---
    if not st.session_state[sjs]:
        # --- Render login form with buttons ---
        login_page(disabled=st.session_state.generating_response, keys=lp_keys)

        # --- Ensure both keys exist to avoid KeyError ---
        if apj_keys in st.session_state:
            if st.session_state[apj_keys]:
                # --- User clicked "Start Applying" ---
                st.session_state.generating_response = True
                st.session_state[asj_keys[0]] = True
                st.session_state[asj_keys[1]] = False
                st.write(":white_check_mark: Job application Started")

                st.rerun()
        
        # --- If user also clicked "Stop", cancel application ---
        if stj_keys in st.session_state:
            if st.session_state[stj_keys]:
                st.session_state.generating_response = False
                st.session_state[asj_keys[0]] = False
                st.session_state[asj_keys[1]] = True
                st.write(":x: Not Started")
                st.rerun()


# ---{ LinkedIn Jobs Apply application logic }---
def run_linkedin_jobs_apply(sjs=['show_job_settings','show_job_settings_ext']):
    # ---{ Resume upload section }---
    st.subheader(body="Upload your Resume File (PDF/Docx)", divider=True)
    st.info("Currently, the application is disabled. As we are testing the application will eb enabled soon.")
    get_resume(disabled=st.session_state.generating_response)

    # Simulated "sliding" content
    if not st.session_state.show_box2:
        # ---{ If resume uploaded, show job settings form }---
        if st.session_state.get("resume_file"):
            st.subheader(body="Fill the Job Settings", divider=True)

            # ---{ Job settings input or summary display }---
            with st.container(border=True, height=400):
                if st.session_state[sjs[0]]:
                    st.session_state.keys = get_job_settings()
                else:
                    settings_df = pd.DataFrame(
                        [(key, str(value)) for key, value in st.session_state["job_settings_backup"].items()],
                        columns=["Setting", "Value"]
                    )
                    st.subheader("Saved Job Settings", divider=True)
                    st.table(settings_df)

            confirm_refix_buttons(sjs=sjs[0], cc_keys=["confirm_selections", ["show_job_settings", "job_settings_backup", "keys"]], 
                          cr_keys=["fix_selections", ["show_job_settings", "job_settings_backup"]],
                          lp_keys=["email", "password",'apply_jobs','stop_jobs'],
                          apj_keys="apply_jobs", stj_keys="stop_jobs",
                          asj_keys=["applying_jobs", "stopped_jobs"])
    else:
        with st.container(border=True, height=400):
            if st.session_state[sjs[1]]:
                st.session_state.keys_ext = get_ext_job_settings()
            else:
                settings_df = pd.DataFrame(
                    [(key, str(value)) for key, value in st.session_state["job_settings_backup_ext"].items()],
                    columns=["Setting", "Value"]
                )
                st.subheader("Saved Job Settings", divider=True)
                st.table(settings_df)

        confirm_refix_buttons(sjs=sjs[1], cc_keys=["confirm_selections_ext", ["show_job_settings_ext", "job_settings_backup_ext", "keys_ext"]], 
                          cr_keys=["fix_selections_ext", ["show_job_settings_ext", "job_settings_backup_ext"]],
                          lp_keys=["email_ext", "password_ext",'apply_jobs_ext','stop_jobs_ext'],
                          apj_keys="apply_jobs_ext", stj_keys="stop_jobs_ext",
                          asj_keys=["applying_jobs_ext", "stopped_jobs_ext"])

    # Button to toggle
    if st.session_state.get("completed_scrapping", False) and st.session_state.get("resume_file"):
        if st.button("Apply External JOBS?", icon="🚨", key="toggle_form", use_container_width=True, disabled=True or st.session_state.generating_response):
            st.session_state.show_box2 = not st.session_state.show_box2
            st.rerun()

    # ---{ Placeholder note for unfinished logic }---
    st.info(":construction: LinkedIn Jobs Apply logic not implemented yet.")