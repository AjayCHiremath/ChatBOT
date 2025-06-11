from utils.env_loaders import load_environment
from utils.logger.EventLogger import log_message

def reload_environment(log_base="logs/chatbot/", echo=False):
    keys_to_load = ['PINECONE_API_KEY', 'PINECONE_REGION', 'PINECONE_INDEX', 
                    'TOGETHER_API_KEY', 'TOGETHER_BASE_URL', 'LANGCHAIN_API_KEY', 
                    'LANGCHAIN_PROJECT', 'LANGSMITH_TRACING', 'LANGSMITH_ENDPOINT']
    
    load_environment(keys_to_load)
    for keys in keys_to_load:
        log_message(f"[Success] Reloading Environment variables:{keys}", log_file=log_base, echo=echo)