import sqlite3
import threading
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

thread_local = threading.local()

@contextmanager
def get_db_connection():
    """Get a database connection within a context manager."""
    conn = None
    try:
        conn = sqlite3.connect('negotiations.db')
        yield conn
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database schema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create user preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en'
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                initiator_id INTEGER,
                participant_id INTEGER,
                initiator_role TEXT,
                initiator_limit INTEGER,
                participant_limit INTEGER,
                status TEXT,
                created_at DATETIME,
                expires_at DATETIME
            )
        ''')
        
        conn.commit()
        print("Database tables created successfully")

def get_db() -> sqlite3.Connection:
    """Initialize and return the database connection."""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect('negotiations.db')
        init_db()
    return thread_local.conn

def save_session(session_id: str, session, status: str = 'pending', result: str = None) -> None:
    """Save a session to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sessions
                (session_id, initiator_id, participant_id, initiator_role,
                 initiator_limit, participant_limit, status, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                session.initiator_id,
                session.invited_id,
                session.initiator_role,
                session.initiator_limit,
                session.invited_limit,
                status,
                session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                session.expires_at.strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            conn.rollback()
            raise

def get_user_language(user_id: int) -> str:
    """Retrieve the user's language preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'en'

def set_user_language(user_id: int, language: str) -> None:
    """Set the user's language preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, language)
            VALUES (?, ?)
        ''', (user_id, language))
        conn.commit()