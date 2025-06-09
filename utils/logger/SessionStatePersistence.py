import os
import json
import streamlit as st
from utils.logger.SessionId import get_session_id

def save_session_state():
    session_id = "Ajay"
    state_data = {}
    for key, value in st.session_state.items():
        try:
            json.dumps(value)  # test if it's serializable
            state_data[key] = value
        except (TypeError, OverflowError):
            # Skip unserializable items
            pass
    os.makedirs("logs/session_states", exist_ok=True)
    with open(f"logs/session_states/{session_id}.json", "w") as f:
        json.dump(state_data, f)

def load_session_state():
    # session_id = get_session_id()
    session_id = get_session_id()

    filename = f"logs/session_states/{session_id}.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                state_data = json.load(f)
            for key, value in state_data.items():
                st.session_state[key] = value
        except json.JSONDecodeError:
            # Handle corrupted file: delete or skip
            os.remove(filename)
            print(f"[Warning] Corrupted session file {filename} deleted.")
