"""
FAISS vector store operations for semantic search
"""
import os
import logging
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import INDEX_DIR, EMBEDDING_MODEL
from typing import List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.index_path = os.path.join(os.path.dirname(__file__), '..', INDEX_DIR)
    
    def build_vector_store(self, chunks: List[str], video_id: Optional[str] = None) -> FAISS:
        """
        Build FAISS vector store from text chunks
        """
        try:
            if not chunks:
                raise ValueError("No chunks provided for vector store creation")
            
            # Create FAISS index
            db = FAISS.from_texts(chunks, self.embeddings)
            
            # Save index with video-specific naming if provided
            index_dir = f"{self.index_path}_{video_id}" if video_id else self.index_path
            os.makedirs(index_dir, exist_ok=True)
            
            db.save_local(index_dir)
            logger.info(f"Vector store created and saved to {index_dir}")
            
            return db
            
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            raise
    
    def load_vector_store(self, video_id: Optional[str] = None) -> Optional[FAISS]:
        """
        Load existing FAISS vector store
        """
        try:
            index_dir = f"{self.index_path}_{video_id}" if video_id else self.index_path
            
            if not os.path.exists(index_dir):
                logger.warning(f"Vector store not found at {index_dir}")
                return None
            
            db = FAISS.load_local(
                index_dir, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            
            logger.info(f"Vector store loaded from {index_dir}")
            return db
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return None
    
    def retrieve_similar_chunks(self, db: FAISS, query: str, k: int = 3) -> List[str]:
        """
        Retrieve top-k similar chunks for a query
        """
        try:
            if db is None:
                return []
            
            # Perform similarity search
            results = db.similarity_search(query, k=k)
            
            # Extract text content
            chunks = [doc.page_content for doc in results]
            
            logger.info(f"Retrieved {len(chunks)} similar chunks for query: {query[:50]}...")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving similar chunks: {e}")
            return []
    
    def retrieve_with_scores(self, db: FAISS, query: str, k: int = 3) -> List[tuple]:
        """
        Retrieve similar chunks with similarity scores
        """
        try:
            if db is None:
                return []
            
            # Perform similarity search with scores
            results = db.similarity_search_with_score(query, k=k)
            
            # Format results
            scored_chunks = [(doc.page_content, score) for doc, score in results]
            
            return scored_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks with scores: {e}")
            return []
    
    def add_chunks_to_store(self, db: FAISS, new_chunks: List[str]) -> FAISS:
        """
        Add new chunks to existing vector store
        """
        try:
            # Create embeddings for new chunks
            new_db = FAISS.from_texts(new_chunks, self.embeddings)
            
            # Merge with existing store
            db.merge_from(new_db)
            
            logger.info(f"Added {len(new_chunks)} new chunks to vector store")
            return db
            
        except Exception as e:
            logger.error(f"Error adding chunks to store: {e}")
            return db
    
    def get_store_statistics(self, db: FAISS) -> dict:
        """
        Get statistics about the vector store
        """
        try:
            if db is None:
                return {}
            
            # Get index information
            index = db.index
            
            return {
                'total_vectors': index.ntotal,
                'vector_dimension': index.d,
                'index_type': type(index).__name__
            }
            
        except Exception as e:
            logger.error(f"Error getting store statistics: {e}")
            return {}

# Global embedding store instance
embedding_store = EmbeddingStore()
