from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import streamlit as st

class StreamToStreamlit(StreamingStdOutCallbackHandler):
    def __init__(self, placeholder):
        self.text = ""
        self.placeholder = placeholder

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.placeholder.markdown(f"**Assistant:** {self.text}▌")