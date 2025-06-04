import streamlit as st

def build_layout():
    response_container = st.container(border=True, height=350)
    input_container = st.container(border=False)
    return response_container, input_container