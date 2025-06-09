from streamlit_chat import message as chat_message
import random

from components.pdf_summarizer.ui.Expander import create_expander

from utils.GLOBALVARIABLES import HUMAN_ICONS, AI_ICONS

def display_chat_history(entry, idx):

    role = entry.get("role")
    think = entry.get("think")
    message_content = entry.get("message")
    
    # Add unique keys using idx or hash
    message_key = f"chat_message_{idx}_{hash(message_content)}"

    # Display the main message with unique key
    if role == "user":
        chat_message(
            message_content,
            is_user=True,
            logo=random.shuffle(HUMAN_ICONS),
            key=message_key
        )
        
    else:
        # Show chain-of-thought if available
        if think:
            create_expander(
                label="Instructions:",
                generated_text=think,
                expanded=False
            )
        chat_message(
            message_content,
            is_user=False,
            logo=random.shuffle(AI_ICONS),
            key=message_key
        )