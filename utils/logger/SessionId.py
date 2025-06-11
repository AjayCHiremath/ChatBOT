import streamlit.runtime.scriptrunner as scriptrunner
import streamlit as st

def get_session_id():
    ctx = scriptrunner.get_script_run_ctx()
    if ctx:
        if "user_name" not in st.session_state: 
            st.session_state.user_name="xyz"
            st.rerun()
        return st.session_state.user_name + "_" + ctx.session_id
    return "unknown-session"