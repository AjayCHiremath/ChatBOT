import os
import tempfile

from langchain.docstore.document import Document
from langchain_community.document_loaders import PDFPlumberLoader

from utils.logger.EventLogger import log_message

# ---{ Helper function to load documents from uploaded files }---
def load_documents(files, log_base="logs/chatbot/", echo=False):
    documents = []
    try:
        # ---{ Create a temporary directory to save uploaded files }---
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save each uploaded file to the temp directory
                saved_paths = []
                for file in files:
                    file_path = os.path.join(temp_dir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                    saved_paths.append(file_path)
                log_message("[Success] Uploaded files saved to temporary directory.", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"[Error] Saving uploaded files: {e}", log_file=log_base, echo=echo)
                raise

            try:
                # ---{ Load each PDF file using LangChain’s PDFPlumberLoader }---
                for path in saved_paths:
                    loader = PDFPlumberLoader(path)
                    doc_list = loader.load()  # This returns a list with 1 document (entire PDF)

                    for doc in doc_list:
                        pages = doc.page_content.split("\f")  # Split by form feed (page separator)
                        total_pages = len(pages)

                        for i, page_text in enumerate(pages):
                            if not page_text.strip():
                                continue  # Skip empty pages

                            # Build metadata: merge original + page info
                            metadata = {
                                **doc.metadata,
                                "source": os.path.basename(path),
                                "page": i + 1,
                                "total_pages": total_pages
                            }

                            documents.append(Document(
                                page_content=page_text,
                                metadata=metadata
                            ))

                # ---{ Logging the result }---
                if documents:
                    log_message(f"[Success] Extracted {len(documents)} pages from PDFs using LangChain.", log_file=log_base, echo=echo)
                else:
                    log_message("[Warning] No text extracted from PDFs.", log_file=log_base, echo=echo)

                return documents

            except Exception as e:
                log_message(f"[Error] Extracting content using LangChain PDFPlumberLoader: {e}", log_file=log_base, echo=echo)
                raise
            
    except Exception as e:
        log_message(f"[Error] load_documents: {e}", log_file=log_base, echo=echo)
        raise