import streamlit as st
from functools import partial

# ---{ Create Confirm Button to Lock Current Selections }---
def create_confirm(col, disabled: bool, keys=["confirm_selections", ["job_settings_backup", "key"]]):
    col.button(
        "Confirm Selections",
        key=keys[0],
        on_click=partial(confirm_selection, False, keys[1]),
        disabled=disabled,
        use_container_width=True
    )

# ---{ Create Refix Button to Restore Previous Selections }---
def create_refix(col, disabled: bool, keys=["fix_selections", ["show_job_settings", "job_settings_backup"]]):
    col.button(
        "Refix Selections",
        key=keys[0],
        on_click=partial(refix_selection, True, keys[1]),
        disabled=disabled,
        use_container_width=True
    )

# ---{ Store Current Selections and Hide Job Settings }---
def confirm_selection(show: bool, key_=["show_job_settings", "job_settings_backup","keys"]):
    st.session_state.update({key_[0]: show})

    # ---{ Save current widget values into backup }---
    st.session_state[key_[1]] = {
        key: st.session_state.get(key) for key in st.session_state.get(key_[2])
    }


# ---{ Restore Previous Selections and Show Job Settings }---
def refix_selection(show: bool, key_=["show_job_settings", "job_settings_backup"]):
    st.session_state.update({key_[0]: show})

    # ---{ Restore widget values from backup }---
    for key, value in st.session_state.get(key_[1], {}).items():
        st.session_state[key] = value