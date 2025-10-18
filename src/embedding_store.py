"""
FAISS vector store operations for semantic search
"""
import os
import logging
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import INDEX_DIR, EMBEDDING_MODEL, RAG_CHUNK_RETRIEVAL, RAG_MAX_CONTEXT_LENGTH, RAG_MIN_SIMILARITY

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
        try:
            if not chunks:
                raise ValueError("No chunks provided for vector store creation")
            db = FAISS.from_texts(chunks, self.embeddings)
            index_dir = f"{self.index_path}_{video_id}" if video_id else self.index_path
            os.makedirs(index_dir, exist_ok=True)
            db.save_local(index_dir)
            logger.info(f"Vector store created and saved to {index_dir}")
            return db
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            raise
    
    def load_vector_store(self, video_id: Optional[str] = None) -> Optional[FAISS]:
        try:
            index_dir = f"{self.index_path}_{video_id}" if video_id else self.index_path
            if not os.path.exists(index_dir):
                logger.warning(f"Vector store not found at {index_dir}")
                return None
            db = FAISS.load_local(index_dir, self.embeddings, allow_dangerous_deserialization=True)
            logger.info(f"Vector store loaded from {index_dir}")
            return db
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return None
    
    def retrieve_similar_chunks(self, db: FAISS, query: str, k: int = 3) -> List[str]:
        try:
            if db is None:
                return []
            results = db.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"Error retrieving similar chunks: {e}")
            return []

    # ---------------- Enhanced Retrieval -----------------
    def retrieve_enhanced_chunks(self, db: FAISS, query: str, k: int = None) -> List[str]:
        """Enhanced retrieval with similarity filtering and larger k"""
        try:
            if db is None:
                return []
            if k is None:
                k = RAG_CHUNK_RETRIEVAL
            results_with_scores = db.similarity_search_with_score(query, k=k*2)
            filtered = [(doc, score) for doc, score in results_with_scores if score >= RAG_MIN_SIMILARITY]
            top = [doc.page_content for doc, score in filtered[:k]]
            return top
        except Exception as e:
            logger.error(f"Error in enhanced retrieval: {e}")
            return []

    def get_comprehensive_context(self, db: FAISS, query: str) -> str:
        """Build a comprehensive context by combining results from query variants"""
        query_variations = [
            query,
            f"What is mentioned about {query}?",
            f"Details about {query}",
            f"Information regarding {query}"
        ]
        seen = set()
        chunks: List[str] = []
        for q in query_variations:
            part = self.retrieve_enhanced_chunks(db, q)
            for p in part:
                key = hash(p[:120])
                if key not in seen:
                    seen.add(key)
                    chunks.append(p)
        context = ""
        for c in chunks:
            if len(context) + len(c) < RAG_MAX_CONTEXT_LENGTH:
                context += c + "\n\n"
            else:
                break
        return context.strip()

    def get_store_statistics(self, db: FAISS) -> dict:
        try:
            if db is None:
                return {}
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
