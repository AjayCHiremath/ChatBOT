import streamlit as st

def build_layout():
    st.markdown("""
        <div class="custom-container">
        """, unsafe_allow_html=True)
    response_container = st.container(border=True, height=350)
    input_container = st.container(border=False)
    return response_container, input_container