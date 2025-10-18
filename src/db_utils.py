import sqlite3
import hashlib
from config import DB_NAME

# ------------------ Database Initialization ------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS videos(
            video_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS summaries(
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            summary_type TEXT NOT NULL,
            content TEXT,
            FOREIGN KEY(video_id) REFERENCES videos(video_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_history(
            qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            question TEXT,
            answer TEXT,
            FOREIGN KEY(video_id) REFERENCES videos(video_id)
        )
        """)
    print("Database initialized.")

# ------------------ User Functions ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, hash_password(password)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        user = conn.execute(
            "SELECT user_id, username FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()
        return user if user else None

# ------------------ Video / Summary / QA Functions ------------------
def save_video(user_id, url, title=None):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO videos (user_id, url, title) VALUES (?, ?, ?)",
                     (user_id, url, title))
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def save_summary(video_id, summary_type, content):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO summaries (video_id, summary_type, content) VALUES (?, ?, ?)",
                     (video_id, summary_type, content))
        conn.commit()

def save_qa(video_id, question, answer):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO qa_history (video_id, question, answer) VALUES (?, ?, ?)",
                     (video_id, question, answer))
        conn.commit()
