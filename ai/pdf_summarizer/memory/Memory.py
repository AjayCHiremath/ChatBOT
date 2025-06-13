import re
import os
import streamlit as st
from datetime import datetime, timedelta

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from utils.logger.EventLogger import log_message
from utils.aws_utils import read_auth_file_from_s3, write_auth_file_to_s3
from utils.global_variables import PERSIST_DIRECTORY, OBJECT_KEYS_CHAT_HISTORY

# ---{ Helper function to save chat history locally }---
def save_chat_history(history, log_base="logs/chatbot/", echo=False) -> BaseChatMessageHistory:
    try:
        #----{ Read auth file from S3 }------
        authorized_user_data = read_auth_file_from_s3(
            bucket_name=os.getenv("MY_S3_BUCKET"),
            object_key=(PERSIST_DIRECTORY+OBJECT_KEYS_CHAT_HISTORY),
            use_locally=False
        )

        #----{ Convert all messages to dict format using .dict() }------
        messages_dict = [msg.dict() for msg in history.messages]
        authorized_user_data.append(messages_dict)

        #----{ Write updated auth file to S3 }------
        write_auth_file_to_s3(
            authorized_user_data=authorized_user_data,
            bucket_name=os.getenv("MY_S3_BUCKET"),
            object_key=(PERSIST_DIRECTORY+OBJECT_KEYS_CHAT_HISTORY),
            use_locally=False
        )
        log_message("[Success] Saved Chat History to S3.", log_file=log_base, echo=echo)
    except Exception as e:
        log_message(f"[Error] Saving Chat History to S3 failed: {e}", log_file=log_base, echo=echo)

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
    if 'last_saved_time' not in st.session_state:
        st.session_state.last_saved_time = datetime.now()

    if datetime.now() - st.session_state.last_saved_time > timedelta(seconds=500):
        save_chat_history(history, log_base=log_base, echo=echo)
        st.session_state.last_saved_time = datetime.now()


# ---{ Directly return the chat history memory for the given session ID }---
def get_memory(session_id: str, log_base="logs/chatbot/", echo=False):
    return get_session_history(session_id=session_id, log_base=log_base, echo=echo)