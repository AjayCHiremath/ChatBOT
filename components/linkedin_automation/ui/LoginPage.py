import streamlit as st
import re

def login_page(disabled:bool=False, keys=["email", "password",'apply_jobs','stop_jobs']):
    # -----{Title of the login page}------
    st.title(":lock: Login to Continue")

    # -----{Email input section}------
    cols_email = st.columns([1, 1, 3, 1])
    cols_email[1].markdown("**:email: Email Address**")
    cols_email[2].text_input(
        "Email Address", 
        placeholder="you@example.com", 
        label_visibility="collapsed",
        key=keys[0]
    )

    # -----{Check if email input is present}------
    if st.session_state.get(keys[0], None):
        # -----{Validate email format using regex}------
        if re.match(r"[^@]+@[^@]+\.[^@]+", st.session_state.get(keys[0], None)):

            # -----{Password input section}------
            cols_password = st.columns([1, 1, 3, 1])
            cols_password[1].markdown("**:closed_lock_with_key: Password**")
            cols_password[2].text_input(
                "Enter Password", 
                placeholder="********", 
                type="password", 
                label_visibility="collapsed",
                key=keys[1]
            )

            # -----{Show action buttons}------
            cols_submit1, cols_submit2 = st.columns(2)

            # -----{Start applying button}------
            cols_submit1.button(":rocket: Start Applying for Jobs", key=keys[2],disabled=True or disabled, use_container_width=True)

            # -----{Stop applying button}------
            cols_submit2.button(":x: Stop Applying for Jobs", key=keys[3], disabled=True or not disabled, use_container_width=True)

        else:
            # -----{Display error if email is invalid}------
            st.error(":warning: Invalid email address")
    
    # -----{Default return if conditions not met}------
    return False, False
