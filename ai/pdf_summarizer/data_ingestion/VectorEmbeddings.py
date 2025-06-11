from langchain_together import TogetherEmbeddings
import json
import os

from utils.global_variables import FILE_PATH_MODEL_NAME, CHUNK_SIZE_EMBEDDINGS

from utils.logger.EventLogger import log_message

# ---{ Helper function to embed documents }---
def get_embeddings(model_work="embeddings", log_base="logs/chatbot/", echo=False):
    # ---{ Open file where model names are saved }---
    try:
        with open(FILE_PATH_MODEL_NAME, "r") as fp:
            model_config = json.load(fp)
            log_message("[Success] Model configuration file loaded.", log_file=log_base, echo=echo)
    except Exception as e:
        log_message(f"[Error] Loading model configuration: {e}", log_file=log_base, echo=echo)
        raise

    # ---{ Get Model name for embeddings }---
    try:
        model_name = model_config[model_work]
        log_message("[Success] Model name fetched successfully.", log_file=log_base, echo=echo)
    except Exception as e:
        log_message(f"[Error] Getting model name: {e}", log_file=log_base, echo=echo)
        raise

    # ---{ Create Embeddings model using TogetherEmbeddings }---
    try:
        embedding_model = TogetherEmbeddings(
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url=os.getenv("TOGETHER_BASE_URL"),
            model=model_name,
            chunk_size=CHUNK_SIZE_EMBEDDINGS,
            show_progress_bar=True,
            skip_empty=True,
            max_retries=3,
        )
        log_message("[Success] Embedding model initialized successfully.", log_file=log_base, echo=echo)
        return embedding_model
    except Exception as e:
        log_message(f"[Error] Initializing embedding model: {e}", log_file=log_base, echo=echo)
        raise