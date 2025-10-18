# ------------------ Chunking Settings ------------------
CHUNK_SIZE = 1000         # number of characters per chunk
CHUNK_OVERLAP = 200       # number of overlapping characters between chunks

# ------------------ Vector Store Settings ------------------
INDEX_DIR = "faiss_index"  # folder to save/load FAISS index

# ------------------ Database Settings ------------------
DB_NAME = "youtube_summarizer.db"

# ------------------ Upload Directory ------------------
UPLOAD_DIR = "user_uploaded_files"

# ------------------ Gemini API ------------------
GENAI_MODEL_NAME = "gemini-2.0-flash"
