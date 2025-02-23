import sqlite3
import json
from datetime import datetime

def init_db():
    """Initialize all database tables"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            embedding TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            status TEXT NOT NULL,
            stage TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def store_user_interaction(phone_number, query, response, embedding):
    """Store a new user interaction with embedding"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Convert embedding list to JSON string for storage
    embedding_json = json.dumps(embedding)

    c.execute('''
        INSERT INTO users (phone_number, query, response, embedding)
        VALUES (?, ?, ?, ?)
    ''', (phone_number, query, response, embedding_json))

    conn.commit()
    conn.close()

def get_user_history(phone_number, limit=5):
    """Get recent interactions for a specific user"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    c.execute('''
        SELECT query, response, embedding, timestamp
        FROM users
        WHERE phone_number = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (phone_number, limit))

    results = c.fetchall()
    conn.close()

    # Convert results to list of dictionaries
    history = []
    for row in results:
        history.append({
            'query': row[0],
            'response': row[1],
            'embedding': json.loads(row[2]) if row[2] else None,
            'timestamp': row[3]
        })

    return history

def search_similar_queries(embedding, limit=3):
    """Find similar previous queries using embedding comparison"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Get all queries with embeddings
    c.execute('SELECT query, response, embedding FROM users WHERE embedding IS NOT NULL')
    results = c.fetchall()

    # Convert embedding strings back to lists
    similar_queries = []
    for row in results:
        stored_embedding = json.loads(row[2])
        # Here you would implement similarity comparison
        # For now, we'll just return the most recent ones
        similar_queries.append({
            'query': row[0],
            'response': row[1]
        })

    conn.close()
    return similar_queries[:limit]

def create_session(phone_number):
    """Create a new chat session"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO sessions (phone_number, status, stage)
        VALUES (?, 'ACTIVE', 'INITIAL')
    ''', (phone_number,))

    conn.commit()
    conn.close()

def get_active_session(phone_number):
    """Get user's active session if exists"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    c.execute('''
        SELECT id, stage FROM sessions
        WHERE phone_number = ? AND status = 'ACTIVE'
        ORDER BY last_updated DESC LIMIT 1
    ''', (phone_number,))

    result = c.fetchone()
    conn.close()
    return result

def update_session_stage(phone_number, new_stage):
    """Update session stage"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    c.execute('''
        UPDATE sessions
        SET stage = ?, last_updated = CURRENT_TIMESTAMP
        WHERE phone_number = ? AND status = 'ACTIVE'
    ''', (new_stage, phone_number))

    conn.commit()
    conn.close()
