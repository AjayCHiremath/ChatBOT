from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.global_variables import DOCUMENTS_CHUNK_OVERLAP, DOCUMENTS_CHUNK_SIZE
from utils.logger.EventLogger import log_message

# ---{ Helper function to split documents into chunks }---
def document_chunking(documents, log_base="logs/chatbot/", echo=False):
    try:
        # ---{Initialize the recursive character text splitter}---
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=DOCUMENTS_CHUNK_SIZE,
            chunk_overlap=DOCUMENTS_CHUNK_OVERLAP
        )
        log_message("[Success] Text splitter initialized successfully.", log_file=log_base, echo=echo)

        split_docs = []
        # ---{Iterate through each document and split it}---
        for doc in documents:
            try:
                splits = splitter.split_documents([doc])
                split_docs.extend(splits)
                log_message("[Success] Document split into chunks successfully.", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"[Error] Splitting document: {e}", log_file=log_base, echo=echo)
                raise

        # ---{Return all split documents}---
        return split_docs
    except Exception as e:
        log_message(f"[Error] document_chunking: {e}", log_file=log_base, echo=echo)
        raise