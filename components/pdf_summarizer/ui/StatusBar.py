import streamlit as st
import time

from ai.pdf_summarizer.data_ingestion.DataLoaders import load_documents
from ai.pdf_summarizer.data_ingestion.DocumentSplitters import document_chunking
from ai.pdf_summarizer.vectorstore.VectorStore import create_vectorstore
from ai.pdf_summarizer.data_ingestion.VectorEmbeddings import get_embeddings
from utils.logger.EventLogger import log_message

#---{Function to get status and split documents}---
def get_status_embed_store(documents, log_base="logs/chatbot/", echo=False):
    try:
        #---{Display status to user}---
        placeholder = st.empty()
        with placeholder.status("🔍 Analyzing Data...", expanded=True):
            try:
                #---{Get OpenAI embeddings}---
                st.write("💡 Preparing data for future storage...")
                time.sleep(0.5)
                embeddings = get_embeddings(model_work="embeddings", log_base=log_base, echo=echo)
                log_message("[Success] Embeddings loaded successfully.", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"[Error] Embedding the data: {e}", log_file=log_base, echo=echo)
                raise  #---{Raise error to halt execution if embeddings fail}---

            try:
                st.write("🗂️ Storing the data securely...")
                time.sleep(0.5)
                #---{Create Pinecone VectorStore}---
                vectorstore = create_vectorstore(embeddings=embeddings, documents=documents, log_base=log_base, echo=echo)
                log_message("[Success] Vectorstore created successfully.", log_file=log_base, echo=echo)
                st.write("✔️ Data analysis completed!")
                time.sleep(0.5)
                st.empty()
                return vectorstore
            except Exception as e:
                log_message(f"[Error] Storing the document into Pinecone: {e}", log_file=log_base, echo=echo)
                raise
    except Exception as e:
        log_message(f"[Error] get_status_embed_store: {e}", log_file=log_base, echo=echo)
        raise

#---{Function to get status and split documents}---
def get_status_data_ingestion(files, log_base="logs/chatbot/", echo=False):
    try:
        #---{Display status to user}---
        placeholder = st.empty()
        with placeholder.status("📥 Uploading data...", expanded=True):
            try:
                documents = load_documents(files=files, log_base=log_base, echo=echo)
                log_message("[Success] Documents loaded successfully.", log_file=log_base, echo=echo)
            except Exception as e:
                log_message(f"[Error] Loading documents: {e}", log_file=log_base, echo=echo)
                raise  #---{Raise error to halt execution if documents can't be loaded}---

            try:
                st.write("🔎 Searching through the documents...")
                time.sleep(0.5)
                split_document = document_chunking(documents=documents, log_base=log_base, echo=echo)
                st.write("✂️ Splitting documents into chunks...")
                time.sleep(0.5)
                log_message("[Success] Documents chunked successfully.", log_file=log_base, echo=echo)
                st.empty()
                return split_document
            except Exception as e:
                log_message(f"[Error] Chunking document: {e}", log_file=log_base, echo=echo)
                raise
    except Exception as e:
        log_message(f"[Error] get_status_data_ingestion: {e}", log_file=log_base, echo=echo)
        raise