"""
Database utilities for user management and data persistence
"""
import sqlite3
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict
import logging
from .config import DB_PATH, SESSION_TIMEOUT, MAX_LOGIN_ATTEMPTS
from typing import Optional, List, Tuple, Dict 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection with foreign key support"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table with enhanced security
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Videos table with metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    youtube_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    duration INTEGER,
                    language TEXT DEFAULT 'en',
                    transcript_length INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    summary_type TEXT NOT NULL CHECK(summary_type IN ('short', 'detailed')),
                    content TEXT NOT NULL,
                    word_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(video_id) REFERENCES videos(video_id) ON DELETE CASCADE
                )
            """)
            
            # Q&A History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qa_history (
                    qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    similarity_score REAL,
                    response_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(video_id) REFERENCES videos(video_id) ON DELETE CASCADE
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password with salt using bcrypt"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8'), salt.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> bool:
        """Create new user account"""
        try:
            password_hash, salt = self.hash_password(password)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                    (username, email, password_hash, salt)
                )
                conn.commit()
                logger.info(f"User created successfully: {username}")
                return True
                
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if account is locked
            cursor.execute(
                "SELECT user_id, password_hash, login_attempts, locked_until FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                return None
            
            user_id, password_hash, login_attempts, locked_until = user
            
            # Check if account is locked
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                logger.warning(f"Account locked for user: {username}")
                return None
            
            # Verify password
            if self.verify_password(password, password_hash):
                # Reset login attempts and update last login
                cursor.execute(
                    "UPDATE users SET login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                
                return {
                    'user_id': user_id,
                    'username': username
                }
            else:
                # Increment login attempts
                new_attempts = login_attempts + 1
                locked_until = None
                
                if new_attempts >= MAX_LOGIN_ATTEMPTS:
                    locked_until = (datetime.now() + timedelta(minutes=30)).isoformat()
                
                cursor.execute(
                    "UPDATE users SET login_attempts = ?, locked_until = ? WHERE user_id = ?",
                    (new_attempts, locked_until, user_id)
                )
                conn.commit()
                
                logger.warning(f"Failed login attempt for user: {username}")
                return None
    
    def save_video(self, user_id: int, youtube_id: str, url: str, title: str, duration: Optional[int] = None, language: str = 'en') -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
            "INSERT INTO videos (user_id, youtube_id, url, title, duration, language, processed_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, youtube_id, url, title, duration, language)
            )
            conn.commit()
            last_id = cursor.lastrowid
            return int(last_id) if last_id is not None else 0
    
    def save_summary(self, video_id: int, summary_type: str, content: str):
        """Save video summary"""
        word_count = len(content.split())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO summaries (video_id, summary_type, content, word_count) VALUES (?, ?, ?, ?)",
                (video_id, summary_type, content, word_count)
            )
            conn.commit()
    
    def save_qa(self, video_id: int, question: str, answer: str, similarity_score: Optional[float] = None, response_time: Optional[float] = None):
        """Save Q&A interaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO qa_history (video_id, question, answer, similarity_score, response_time) VALUES (?, ?, ?, ?, ?)",
                (video_id, question, answer, similarity_score, response_time)
            )
            conn.commit()
    
    def get_user_videos(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get user's processed videos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT video_id, youtube_id, url, title, duration, language, created_at, processed_at
                FROM videos 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            videos = []
            for row in cursor.fetchall():
                videos.append({
                    'video_id': row[0],
                    'youtube_id': row[1],
                    'url': row[2],
                    'title': row[3],
                    'duration': row[4],
                    'language': row[5],
                    'created_at': row[6],
                    'processed_at': row[7]
                })
            
            return videos
    
    def get_video_summaries(self, video_id: int) -> Dict:
        """Get summaries for a video"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT summary_type, content, word_count, created_at FROM summaries WHERE video_id = ?",
                (video_id,)
            )
            
            summaries = {}
            for row in cursor.fetchall():
                summaries[row[0]] = {
                    'content': row[1],
                    'word_count': row[2],
                    'created_at': row[3]
                }
            
            return summaries
    
    def get_video_qa_history(self, video_id: int) -> List[Dict]:
        """Get Q&A history for a video"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT question, answer, similarity_score, response_time, created_at FROM qa_history WHERE video_id = ? ORDER BY created_at DESC",
                (video_id,)
            )
            
            qa_history = []
            for row in cursor.fetchall():
                qa_history.append({
                    'question': row[0],
                    'answer': row[1],
                    'similarity_score': row[2],
                    'response_time': row[3],
                    'created_at': row[4]
                })
            
            return qa_history

# Global database instance
db_manager = DatabaseManager()