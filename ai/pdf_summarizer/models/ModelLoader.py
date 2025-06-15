from langchain_together import ChatTogether
import json
import os
import streamlit as st

from utils.logger.EventLogger import log_message
from utils.global_variables import FILE_PATH_MODEL_NAME, MODEL_MAX_TOKENS

#--------{ Load Model Names from JSON }----------
def load_models(file_path, model_work, log_base="logs/chatbot/", echo=False):
    try:
        # ---{ Open file where model names are saved }---
        with open(file=file_path) as fp:
            model_name = json.load(fp)[model_work]
            log_message(f"[Success] Model name '{model_name}' loaded successfully.", log_file=log_base, echo=echo)
            return model_name
    except Exception as e:
        log_message(f"[Error] load_models: {e}", log_file=log_base, echo=echo)
        return None

#--------{ Get Models }----------
def get_model(model_work="question_reframer", log_base="logs/chatbot/", echo=False):
    try:
        # ---{ Get model names}---
        model_name = load_models(file_path=FILE_PATH_MODEL_NAME, model_work=model_work, log_base=log_base, echo=echo)
        if model_name is None:
            raise ValueError(f"Model name not found for work: {model_work}")

        # ---{ Inference Model }---
        model = ChatTogether(
            model=model_name,
            api_key=os.getenv("TOGETHER_API_KEY") if "user_api_key" not in st.session_state else st.session_state.user_api_key,
            # max_tokens=MODEL_MAX_TOKENS,
            temperature=0.7,
            streaming=False,
            max_retries=3,
        )
        log_message(f"[Success] {model_work}: Model loaded successfully.", log_file=log_base, echo=echo)
        return model
    except Exception as e:
        log_message(f"[Error] get_model {model_work}: {e}", log_file=log_base, echo=echo)
        return None
