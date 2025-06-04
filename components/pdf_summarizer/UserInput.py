import streamlit as st

# ---------------------{ File Upload Handler }---------------------
def get_file():
    # ---------------------{ PDF Upload Configuration }---------------------
    max_files = 3
    disabled = len(st.session_state.uploaded_pdfs) >= max_files

    # Disable input during response generation
    if st.session_state.generating_response:
        disabled = st.session_state.generating_response

    # ---------------------{ PDF Upload UI Layout }---------------------
    cols = st.columns([0.5, 9])
    cols[0].markdown("**📎 Attach PDF**")

    # ---------------------{ Upload Limit Status }---------------------
    if len(st.session_state.uploaded_pdfs) >= max_files:
        st.info("✅ Maximum of 3 PDF files uploaded.")

    # ---------------------{ File Uploader Widget }---------------------
    cols[1].file_uploader(
        label="Attach PDF",
        type=["pdf"],
        label_visibility="collapsed",
        accept_multiple_files=True,
        disabled=disabled,
        key=f"uploaded"
    )
    if st.session_state.get("uploaded", []):
        st.session_state.uploaded_pdfs=st.session_state.get("uploaded", [])

# ---------------------{ Chat Input Form Builder }---------------------
def create_input_form(cols):
    # ---------------------{ User Message Input }---------------------
    cols[0].text_input(
        label="Message",
        label_visibility="collapsed",
        placeholder="Type your message here...",
        disabled=st.session_state.generating_response,
        key="user_input"
    )

    # ---------------------{ Submit Button (➤) }---------------------
    cols[1].button(
        label="➤", disabled=st.session_state.generating_response, use_container_width=True, key="submitted"
    )

    # ---------------------{ Clear Button (🗑️) }---------------------
    cols[2].button(
        label="🗑️", disabled=st.session_state.generating_response, use_container_width=True, key="cleared"
    )

# ---------------------{ Main Input Logic Handler }---------------------
def get_user_input():
    # ---------------------{ Layout Columns }---------------------
    cols = st.columns([8, 1, 1])
    create_input_form(cols=cols)

    # ---------------------{ Reset App State on Clear }---------------------
    if st.session_state.cleared:
        st.session_state.chat_history = []
        st.session_state.generating_response = False
        st.session_state.run_chain = False
        st.session_state.current_input = ""
        st.session_state.uploaded_pdfs = []
        st.session_state.file_upload_key += 1
        st.rerun()