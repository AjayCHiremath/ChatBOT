import streamlit as st

def display_chat_history():
    for role, message in st.session_state.chat_history:
        st.markdown(f"**{role.capitalize()}:** {message}")