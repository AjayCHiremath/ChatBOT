import os
import tempfile

from langchain_community.document_loaders.generic import GenericLoader, FileSystemBlobLoader
from langchain_community.document_loaders.parsers import PyMuPDFParser

from utils.logger.EventLogger import log_message

# ---{ Helper function to load documents from uploaded files }---
def load_documents(files, log_base="logs/chatbot/", echo=False):
    try:
        # ---{Create temporary directory to store uploaded files}---
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                for file in files:
                    file_path = os.path.join(temp_dir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                log_message("[Success] Uploaded files saved to temporary directory.", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"[Error] Saving uploaded files: {e}", log_file=log_base, echo=echo)
                raise

            try:
                # ---{Use GenericLoader and PyMuPDFParser to load documents}---
                loader = GenericLoader(
                    blob_loader=FileSystemBlobLoader(
                        path=temp_dir,
                        glob="*.pdf",
                    ),
                    blob_parser=PyMuPDFParser(),
                )
                documents = loader.load()
                log_message("[Success] Documents loaded successfully.", log_file=log_base, echo=echo)
                return documents
            except Exception as e:
                log_message(f"[Error] Loading documents with loader: {e}", log_file=log_base, echo=echo)
                raise
    except Exception as e:
        log_message(f"[Error] load_documents: {e}", log_file=log_base, echo=echo)
        raise