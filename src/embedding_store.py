from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import INDEX_DIR
import os

# ------------------ Initialize Embeddings ------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# ------------------ FAISS Vector Store Functions ------------------
def build_vector_store(chunks):
    """
    Build a FAISS vector store from a list of text chunks.
    """
    db = FAISS.from_texts(chunks, embeddings)
    
    # Save index for future use
    os.makedirs(INDEX_DIR, exist_ok=True)
    db.save_local(INDEX_DIR)
    
    return db

def load_vector_store():
    """
    Load FAISS vector store from disk.
    """
    if os.path.exists(INDEX_DIR):
        db = FAISS.load_local(INDEX_DIR, embeddings)
        return db
    else:
        return None

def retrieve_similar_chunks(db, query, k=3):
    """
    Retrieve top-k similar chunks for a user query.
    """
    if db is None:
        return []
    
    results = db.similarity_search(query, k=k)
    return [res.page_content for res in results]