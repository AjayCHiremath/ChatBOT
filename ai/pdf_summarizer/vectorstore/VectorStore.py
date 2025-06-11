import pinecone
from pinecone import ServerlessSpec
import os

from langchain_pinecone.vectorstores import PineconeVectorStore

from utils.logger.EventLogger import log_message
from utils.logger.SessionId import get_session_id
from utils.global_variables import METADATA

# ---{ Helper function to Create or Get Vector Database (Pinecone) }---
def create_vectorstore(embeddings, documents=None, log_base="logs/chatbot/", echo=False):
    try:
        # ---{Initialize Pinecone client}---
        try:
            pc = pinecone.Pinecone(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_REGION")
            )            
            log_message("[Success] Pinecone client initialized successfully.", log_file=log_base, echo=echo)
        except Exception as e:
            log_message(f"[Error] Initializing Pinecone client: {e}", log_file=log_base, echo=echo)
            raise

        # ---{Connect to Pinecone index}---
        try:
            #---{Delete existing index}---
            index_name = os.getenv("PINECONE_INDEX")
            
            if index_name not in pc.list_indexes().names():
                log_message(f"[Info] Pinecone index '{index_name}' does not exist. Creating a new index.", log_file=log_base, echo=echo)
                #---{Get Dimensions}---
                embed_dim = (len(embeddings.embed_query("test")))
                #---{Create new index with correct dimension}---
                pc.create_index(
                    name=index_name,
                    dimension=embed_dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ),
                    deletion_protection="disabled"
                )
                log_message(f"[Success] Pinecone index '{index_name}' created successfully.", log_file=log_base, echo=echo)
            else:
                log_message(f"[Info] Pinecone index '{index_name}' already exists. Connecting to it.", log_file=log_base, echo=echo)
            
            index = pc.Index(name=index_name)
            log_message("[Success] Connected to Pinecone index successfully.", log_file=log_base, echo=echo)
        except Exception as e:
            log_message(f"[Error] Connecting to Pinecone index: {e}", log_file=log_base, echo=echo)
            raise

        # ---{Create Pinecone VectorStore}---
        try:
            vectorstore = PineconeVectorStore(index=index, 
                                              embedding=embeddings,
                                              namespace=f"{get_session_id()}",
                                              distance_strategy="cosine")
            log_message("[Success] Pinecone VectorStore created successfully.", log_file=log_base, echo=echo)

            # ---{Push documents if provided}---
            if documents:
                texts = [doc.page_content for doc in documents]
                vectorstore.add_texts(texts, metadatas=[METADATA])
                log_message("[Success] Documents pushed to Pinecone.", log_file=log_base, echo=echo)

            return vectorstore
        except Exception as e:
            log_message(f"[Error] Creating Pinecone VectorStore or pushing data: {e}", log_file=log_base, echo=echo)
            raise

    except Exception as e:
        log_message(f"[Error] create_vectorstore: {e}", log_file=log_base, echo=echo)
        raise