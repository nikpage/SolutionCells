import sqlite3
from datetime import datetime

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect('negotiations.db')

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

def get_user_language(user_id):
    """Get user's language preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'en'

def set_user_language(user_id, language):
    """Set user's language preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, language)
            VALUES (?, ?)
        ''', (user_id, language))
        conn.commit()
