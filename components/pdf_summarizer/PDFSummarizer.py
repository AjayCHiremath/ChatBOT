import streamlit as st

from ai.pdf_summarizer.chains.SimpleLLMChain import get_chat_chain
from components.pdf_summarizer.ContainerLayout import build_layout
from components.pdf_summarizer.UserInput import get_user_input, get_file
from components.pdf_summarizer.ChatHistory import display_chat_history
from ai.pdf_summarizer.models.ModelLoader import load_llama_model
from ai.pdf_summarizer.models.OutputParsers import get_output_parser
from ai.pdf_summarizer.prompts.PromptEngineering import get_prompt_template
from utils.StreamingCallbacks import StreamToStreamlit


# ---{ PDF Summarizer application logic }---
def run_pdf_summarizer():
    # ---{ Build layout: response and input containers }---
    response_container, input_container = build_layout()

    # ---{ Display chat history in response container }---
    with response_container:
        display_chat_history()

    # ---{ Get file input and user input }---
    with input_container:
        get_file()
        get_user_input()

    # ---{ Handle user message submission }---
    if st.session_state.submitted and st.session_state.user_input:
        st.session_state.chat_history.append(("user", st.session_state.user_input))
        st.session_state.generating_response = True
        st.session_state.run_chain = True
        st.session_state.current_input = st.session_state.user_input
        st.rerun()

    # ---{ Run the chat chain and stream the assistant response }---
    if st.session_state.run_chain:
        with response_container:
            placeholder = st.empty()
            try:
                callback = [StreamToStreamlit(placeholder)]
                prompt = get_prompt_template()
                llm = load_llama_model(callbacks=callback)
                parser = get_output_parser()
                chain = get_chat_chain(prompt=prompt, llm=llm, parser=parser)

                answer = chain.invoke({"question": st.session_state.current_input})
                st.session_state.chat_history.append(("assistant", answer))

            except Exception as e:
                st.error(f"Error: {e}")

            finally:
                st.session_state.generating_response = False
                st.session_state.run_chain = False
                st.session_state.current_input = ""
                st.rerun()
