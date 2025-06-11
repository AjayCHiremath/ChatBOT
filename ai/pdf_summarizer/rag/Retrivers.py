from langchain_core.vectorstores import VectorStoreRetriever
from utils.global_variables import SEARCH_KWARGS, SEARCH_TYPE, METADATA
from utils.logger.EventLogger import log_message  

#---{Get RAG retriever from vectorstore}---
def get_rag(vectorstore, log_base="logs/chatbot/", echo=False):
    try:
        #---{Create VectorStoreRetriever instance}---
        retriever = VectorStoreRetriever(
            vectorstore=vectorstore,
            search_type=SEARCH_TYPE,
            search_kwargs=SEARCH_KWARGS,
            metadata=METADATA
        )
        log_message("[Success] RAG retriever created successfully.", log_file=log_base, echo=echo)
        return retriever
    except Exception as e:
        log_message(f"[Error] get_rag: {e}", log_file=log_base, echo=echo)
        raise