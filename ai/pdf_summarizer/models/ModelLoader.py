from langchain_together import ChatTogether
import os

def load_llama_model(callbacks=None):
    
    return ChatTogether(
        model="meta-llama/Llama-3-8b-chat-hf",
        api_key=os.getenv("TOGETHER_API_KEY"),
        max_tokens=512,
        temperature=0.7,
        callbacks=callbacks
    )