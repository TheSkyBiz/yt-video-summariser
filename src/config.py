"""
Configuration settings for YouTube Video Summarizer
"""
import os
from pathlib import Path

# ------------------ App Settings ------------------
APP_TITLE = "🎬 YouTube Video Summarizer"
APP_LAYOUT = "wide"
VERSION = "1.0.0"

# ------------------ Database Settings ------------------
DB_NAME = "app.db"
DB_PATH = Path(__file__).parent.parent / DB_NAME

# ------------------ Chunking Settings ------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_CHUNKS = 50  # Limit for performance

# ------------------ Vector Store Settings ------------------
INDEX_DIR = "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ------------------ Gemini API Settings ------------------
GENAI_MODEL_NAME = "gemini-1.5-flash"
MAX_TOKENS = 8192
TEMPERATURE = 0.3

# ------------------ Video Processing Settings ------------------
MAX_VIDEO_DURATION = 7200  # 2 hours in seconds
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt']
DEFAULT_LANGUAGE = 'en'

# ------------------ UI Settings ------------------
SIDEBAR_WIDTH = 300
MAX_TRANSCRIPT_PREVIEW = 1500
RESULTS_PER_PAGE = 10

# ------------------ Security Settings ------------------
SESSION_TIMEOUT = 3600  # 1 hour
MIN_PASSWORD_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 5

# ------------------ Logging Settings ------------------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"