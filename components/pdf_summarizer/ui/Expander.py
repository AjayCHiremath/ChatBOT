import streamlit as st

def create_expander(label, generated_text, expanded=False):
    if st.session_state.get("generating_response", False):
        expanded=True

    with st.expander(label=label, expanded=expanded):
        with st.spinner("Generating text..."):
            st.write(generated_text)