import streamlit as st

# ---{ Resume File Upload Component }---
def get_resume(disabled:bool=False):
    # ---{ Upload a single resume file in PDF or DOCX format }---
    st.file_uploader(
        label="Upload your Resume File (PDF/Docx)",
        accept_multiple_files=False,
        key="resume_file",
        label_visibility="collapsed",
        disabled=disabled
    )

    # ---{ Return uploaded resume file from session state }---
    return st.session_state.get("resume_file")