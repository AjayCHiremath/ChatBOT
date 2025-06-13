import streamlit as st

# ---------------------{ File Upload Handler }---------------------
def get_file():
    # ---------------------{ PDF Upload Configuration }---------------------
    max_files = 3
    disabled = len(st.session_state.get(f"uploaded_pdfs_{st.session_state.file_upload_key}", [0])) >= max_files

    # Disable input during response generation
    if st.session_state.generating_response:
        disabled = st.session_state.generating_response

    # ---------------------{ Upload Limit Status }---------------------
    if len(st.session_state.get(f"uploaded_pdfs_{st.session_state.file_upload_key}", [0])) > max_files:
        st.info("✔️ Maximum of 3 PDF files uploaded.")

    # ---------------------{ File Uploader Widget }---------------------
    st.file_uploader(
        label="📎 Attach PDF",
        type=["pdf"],
        label_visibility="visible",
        accept_multiple_files=True,
        disabled=disabled,
        key=f"uploaded_pdfs_{st.session_state.file_upload_key}",
    )
    
# ---------------------{ Chat Input Form Builder }---------------------
def create_input_form():
    # ---------------------{ User Message Input Form }---------------------
    with st.form(key="user_input_form", clear_on_submit=False):
        cols = st.columns([7, 1, 1, 1])

        with cols[0]:
            st.text_input(
                label="Message",
                label_visibility="collapsed",
                placeholder="Type your message here...",
                disabled=st.session_state.generating_response,
                key="user_input",
            )

        # ---------------------{ Submit Button (➤) }---------------------
        with cols[1]:
            st.session_state.submitted = st.form_submit_button(
                label="➤", 
                disabled=st.session_state.generating_response, 
                use_container_width=True
            )

        # ---------------------{ Embeding and Vector Store Button (📨) }---------------------
        with cols[2]:
            embed_docs_clicked = st.form_submit_button(
                label="🧩",
                disabled=(st.session_state.generating_response or
                          st.session_state.embedding_complete or
                          not st.session_state.get(f"uploaded_pdfs_{st.session_state.file_upload_key}", False)),
                use_container_width=True
            )

            if embed_docs_clicked:
                st.session_state.embed_docs = True
                st.session_state.generating_response = True
                embed_docs_clicked=False
                st.rerun()

        # ---------------------{ Clear Button (🗑️) }---------------------
        with cols[3]:
            st.session_state.cleared = st.form_submit_button(
                label="🗑️", 
                disabled=st.session_state.generating_response, 
                use_container_width=True
            )

# ---------------------{ Main Input Logic Handler }---------------------
def get_user_input():
    # ---------------------{ Layout Columns }---------------------
    create_input_form()

    # ---------------------{ Reset App State on Clear }---------------------
    if st.session_state.cleared:
        st.session_state.chat_history = []
        st.session_state.generating_response = False
        st.session_state.run_chain = False
        st.session_state.current_input = ""
        for i in range(st.session_state.file_upload_key + 1):
            key = f"uploaded_pdfs_{i}"
            if key in st.session_state and i != st.session_state.file_upload_key: del st.session_state[key]
        st.session_state.file_upload_key += 1 
        st.session_state.embedding_complete = False
        if st.session_state.get("chat_history_store", None): st.session_state.chat_history_store = []
        st.rerun()