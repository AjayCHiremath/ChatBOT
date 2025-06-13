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

        # ---{Split documents}---
        split_docs = splitter.split_documents(documents)
        log_message(f"[Success] {len(split_docs)} chunks created.", log_base, echo)

        # ---{Return all split documents}---
        return split_docs
    except Exception as e:
        log_message(f"[Error] document_chunking: {e}", log_file=log_base, echo=echo)
        raise