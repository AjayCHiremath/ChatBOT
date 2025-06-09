import streamlit as st

from components.pdf_summarizer.ui.ContainerLayout import build_layout
from components.pdf_summarizer.ui.UserInput import get_user_input, get_file
from components.pdf_summarizer.ui.ChatHistory import display_chat_history
from ai.pdf_summarizer.tools.ModelConnections import connect_chains
from components.pdf_summarizer.ui.StatusBar import get_status_data_ingestion, get_status_embed_store
from utils.logger.EventLogger import log_message
import utils.GLOBALVARIABLES as global_variables
from utils.EnvReloader import reload_environment


# ---{ PDF Summarizer application logic }---
def run_pdf_summarizer(log_base="logs/chatbot/", echo=True):
# ---{ Reinitiate Global variables if not set }---
    variables_to_check = [value for name, value in vars(global_variables).items()
                          if name.isupper() and isinstance(value, (str, type(None)))]
    
    if any(var is None for var in variables_to_check):
        reload_environment(log_base="logs/chatbot/", echo=False)
    try:
        if 'generating_response' not in st.session_state: st.session_state.generating_response = False
        # ---{ Build layout: response and input containers }---
        try: 
            response_container, input_container = build_layout()
        except Exception as e:
            log_message(f"[Error] Building layout: {e}", log_file=log_base, echo=echo)
            return  # Stop if layout fails

        # ---{ Display chat history in response container }---
        with response_container:
            try:
                for idx, entry in enumerate(st.session_state.chat_history):
                    display_chat_history(entry=entry, idx=idx)
            except Exception as e:
                log_message(f"[Error] Displaying chat history: {e}", log_file=log_base, echo=echo)

        # ---{ Get file input and user input }---
        with input_container:
            try:
                get_file()
            except Exception as e:
                log_message(f"[Error] Getting file: {e}", log_file=log_base, echo=echo)
            try:
                get_user_input()
            except Exception as e:
                log_message(f"[Error] Getting user input: {e}", log_file=log_base, echo=echo)
            
            # ---{ Check for file uploads }---
            files = st.session_state.get(f"uploaded_pdfs_{st.session_state.file_upload_key}", [])
            previous_file_len = st.session_state.get("previous_file_len", 0)

            if len(files) != previous_file_len:
                st.session_state.embedding_complete = False  # Reset embedding state
                st.session_state.previous_file_len = len(files)  # Update the stored length

            if st.session_state.embed_docs:
                # ---{ Data Ingestion }---
                try:
                    if len(files) > 0:
                        st.session_state.generating_response = True
                        # ---{ Preprocess the uploaded files }---
                        st.session_state.documents = get_status_data_ingestion(files=files, log_base=log_base, echo=echo)
                    else:
                        st.toast("⚠️ Please Upload research documents")
                except Exception as e:
                    log_message(f"[Error] Handling Document Ingestion: {e}", log_file=log_base, echo=echo)
                finally:
                    st.session_state.generating_response = False

                # ---{ Document Embedding and Vector Store }---
                try:
                    if st.session_state.documents:
                        st.session_state.generating_response = True

                        # ---{ Preprocess stage 2 }---
                        st.session_state.embedded_and_vectorstore = get_status_embed_store(documents=st.session_state.documents, log_base=log_base, echo=echo)
                        st.session_state.embedding_complete = True
                        st.rerun()
                    else:
                        st.toast("⚠️ Please click on analyse data.")
                except Exception as e:
                    log_message(f"[Error] Handling Embeddings: {e}", log_file=log_base, echo=echo)
                finally:
                    st.session_state.generating_response = False

        # ---{ Handle user message submission }---
        try:
            
            if st.session_state.submitted and st.session_state.user_input and st.session_state.documents and st.session_state.embedded_and_vectorstore:
                st.session_state.generating_response = True
                st.session_state.run_chain = True
                st.session_state.current_input = st.session_state.user_input
                st.rerun()
                log_message("[Success] User submission handled successfully.", log_file=log_base, echo=echo)
        except Exception as e:
            log_message(f"[Error] Handling user submission: {e}", log_file=log_base, echo=echo)

        # ---{ Run the chat chain and stream the assistant response }---
        if st.session_state.run_chain:
            # ---{ Main Process }---
            with response_container:
                try:
                    message = {
                        "role": "user",
                        "think": None,
                        "message": st.session_state.user_input,
                        "enhanced_question": None
                    }
                    st.session_state.chat_history.append(message)
                    display_chat_history(entry=message, idx=len(st.session_state.get("chat_history", 1)) - 1)
                    (reframed_question_response, chain_of_thought, 
                        summary_response) = connect_chains(vectorstore=st.session_state.embedded_and_vectorstore, log_base=log_base, echo=echo)
                    log_message("[Success] Chat chain executed successfully.", log_file=log_base, echo=echo)
                    message = {
                        "role": "assistant",
                        "think": chain_of_thought,
                        "message": summary_response,
                        "enhanced_question": reframed_question_response
                    }
                    st.session_state.chat_history.append(message)
                    display_chat_history(entry=message, idx=len(st.session_state.get("chat_history", 1)) - 1)

                except Exception as e:
                    log_message(f"[Error] Running the chat chain: {e}", log_file=log_base, echo=echo)

                finally:
                    try:
                        st.session_state.generating_response = False
                        st.session_state.run_chain = False
                        st.session_state.current_input = ""
                        st.rerun()
                        log_message("[Success] Application state cleaned up successfully.", log_file=log_base, echo=echo)
                    except Exception as e:
                        log_message(f"[Error] Cleaning up app state: {e}", log_file=log_base, echo=echo)

    except Exception as e:
        log_message(f"[Error] run_pdf_summarizer: {e}", log_file=log_base, echo=echo)