import streamlit as st

# ---{ Application Selector }---
def select_application(disabled=False):
    app_descriptions = {
        "PDF Summarizer": "Summarize legal or research-oriented PDF documents.",
        "LinkedIn Jobs Apply": "Automatically apply to LinkedIn job postings (non-Easy Apply only).",
        "Data Analyst": "Analyze and clean data from uploaded CSV or Excel files."
    }

    with st.sidebar:
        st.subheader(body="Select an Application:", divider=True)
        st.selectbox(
            label="Select an Application:",
            options=list(app_descriptions.keys()),
            key="app_selector",
            disabled=disabled,
            label_visibility="collapsed"
        )
        st.caption(app_descriptions[st.session_state.app_selector])


# ---{ GROQ API Key Entry }---
def get_groq(api_key: str, usage_history: int):
    if usage_history > 5:
        return st.sidebar.text_area(label=":key: Enter your GROQ API key", key="groq_api_key")