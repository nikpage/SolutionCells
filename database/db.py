import sqlite3
import threading
from datetime import datetime

thread_local = threading.local()

def get_db():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect('negotiations.db')
        cursor = thread_local.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                initiator_id INTEGER,
                invited_id INTEGER,
                initiator_role TEXT,
                initiator_limit INTEGER,
                invited_limit INTEGER,
                status TEXT,
                created_at DATETIME,
                expires_at DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en'
            )
        ''')
        thread_local.conn.commit()
    return thread_local.conn

def save_session(session_id, sessions, status='pending', result=None):
    conn = get_db()
    cursor = conn.cursor()
    session = sessions[session_id]
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO sessions
            (session_id, initiator_id, invited_id, initiator_role,
             initiator_limit, invited_limit, status, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session['initiator_id'],
            session.get('invited_id'),
            session['initiator_role'],
            session.get('initiator_limit'),
            session.get('invited_limit'),
            status,
            session.get('created_at'),
            session.get('expires_at')
        ))
        conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"DB Error: {e}")

def get_user_language(user_id: int) -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM user_preferences WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 'en'

def set_user_language(user_id: int, language: str) -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_preferences (user_id, language)
        VALUES (?, ?)
    ''', (user_id, language))
    conn.commit()
