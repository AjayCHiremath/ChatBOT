import re
import json
import os
import streamlit as st

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from utils.GLOBALVARIABLES import PERSIST_DIRECTORY
from utils.logger.EventLogger import log_message

# ---{ Helper function to save chat history locally }---
def save_chat_history_locally(session_id: str, history, log_base="logs/chatbot/", echo=False) -> BaseChatMessageHistory:
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
    # ---{ Save to local file in JSON format }---
    file_path = os.path.join(PERSIST_DIRECTORY, f"{session_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        # ---{ Convert all messages to dict format using .dict() }---
        messages_dict = [msg.dict() for msg in history.messages]
        json.dump(messages_dict, f, ensure_ascii=False, indent=2)
    log_message("[Success] Saved Chat History locally.", log_file=log_base, echo=echo)


# ---{ Retrieve or initialize in-memory chat history for a given session ID }---
def get_session_history(session_id: str, log_base="logs/chatbot/", echo=False) -> BaseChatMessageHistory:
    if session_id not in st.session_state.chat_history_store:
        # ---{ Create new chat history }---
        st.session_state.chat_history_store[session_id] = ChatMessageHistory()
        log_message("[Success] Chat History not found initiating new chat history.", log_file=log_base, echo=echo)
    else:
        log_message("[Success] Chat History found.", log_file=log_base, echo=echo)
    return st.session_state.chat_history_store[session_id]

# ---{ Add messages directly to the in-memory chat history }---
def add_message_to_history(session_id: str, message: str, is_user=True, log_base="logs/chatbot/", echo=False):
    history = get_session_history(session_id=session_id, log_base=log_base, echo=echo)

    # ---{ Clean AI message to remove <think> blocks }---    
    if not is_user:
        message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL | re.IGNORECASE).strip()

    if is_user:
        history.add_user_message(message)
    else:
        history.add_ai_message(message)
    log_message("[Success] Created chat histroy sucessfully.", log_file=log_base, echo=echo)

    # ---{ Save history locally }---    
    save_chat_history_locally(session_id=session_id, history=history, log_base=log_base, echo=echo)


# ---{ Directly return the chat history memory for the given session ID }---
def get_memory(session_id: str, log_base="logs/chatbot/", echo=False):
    return get_session_history(session_id=session_id, log_base=log_base, echo=echo)