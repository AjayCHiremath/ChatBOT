import streamlit as st

from components.pdf_summarizer.ui.Expander import create_expander

from utils.global_variables import HUMAN_ICON, AI_ICON

def display_chat_history(entry):
    
    role = entry.get("role")
    enhanced_question = entry.get("enhanced_question")
    think = entry.get("think")
    message_content = entry.get("message")

    # Display the main message with unique key
    if role == "user":        
        with st.chat_message(role, avatar=HUMAN_ICON):
            st.markdown(message_content)

    else:
        # Show chain-of-thought if available
        if think:
            if enhanced_question:
                create_expander(
                    label="Enchanced questions:",
                    generated_text=enhanced_question,
                    expanded=False
                )
            create_expander(
                label="Instructions:",
                generated_text=think,
                expanded=False
            )

        with st.chat_message(role, avatar=AI_ICON):
            st.markdown(message_content)
