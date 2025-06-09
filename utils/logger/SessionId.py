import streamlit.runtime.scriptrunner as scriptrunner

def get_email_id():
    return "ajaychiremathgreprep"

def get_session_id():
    ctx = scriptrunner.get_script_run_ctx()
    if ctx:
        return ctx.session_id
    return "unknown-session"