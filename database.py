import sqlite3
from datetime import datetime
import os

def init_db():
    """Initialize the SQLite database with message tracking table"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    try:
        # First, check if the table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = c.fetchone() is not None

        if table_exists:
            # If table exists, we need to migrate the data
            # First, rename the existing table
            c.execute("ALTER TABLE users RENAME TO users_old")

            # Create new table with all required columns
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    embedding TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_id TEXT UNIQUE,
                    is_acknowledged INTEGER DEFAULT 0,
                    ack_timestamp DATETIME
                )
            ''')

        else:
            # If table doesn't exist, simply create it
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    embedding TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_id TEXT UNIQUE,
                    is_acknowledged INTEGER DEFAULT 0,
                    ack_timestamp DATETIME
                )
            ''')

        conn.commit()
        print("Database initialized successfully")

    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def store_user_interaction(phone_number, query, response, message_id, embedding=None):
    """Store a new user interaction"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO users
            (phone_number, query, response, message_id, embedding, timestamp, is_acknowledged)
            VALUES (?, ?, ?, ?, ?, DATETIME('now'), 0)
        ''', (phone_number, query, response, message_id, embedding))
        last_id = c.lastrowid
        conn.commit()
        return last_id
    except sqlite3.IntegrityError:
        print(f"Message with ID {message_id} already exists")
        return None
    finally:
        conn.close()
def update_user_interaction(phone_number, query, response, message_id, embedding=None):
    """Update an existing user interaction"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    try:
        c.execute('''
            UPDATE users
            SET query = ?,
                response = ?,
                embedding = ?,
                timestamp = DATETIME('now')
            WHERE phone_number = ? AND message_id = ?
        ''', (query, response, embedding, phone_number, message_id))
        conn.commit()
    finally:
        conn.close()

def update_acknowledgment(message_id):
    """Update message acknowledgment status"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    try:
        c.execute('''
            UPDATE users
            SET is_acknowledged = 1,
                ack_timestamp = DATETIME('now')
            WHERE message_id = ?
        ''', (message_id,))
        conn.commit()
    finally:
        conn.close()

def get_unacknowledged_messages(phone_number):
    """Get all unacknowledged messages for a user"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    try:
        c.execute('''
            SELECT id, message_id, query, response, timestamp
            FROM users
            WHERE phone_number = ? AND is_acknowledged = 0
            ORDER BY timestamp DESC
        ''', (phone_number,))
        results = c.fetchall()
        return [
            {
                'id': row[0],
                'message_id': row[1],
                'query': row[2],
                'response': row[3],
                'timestamp': row[4]
            }
            for row in results
        ]
    finally:
        conn.close()
def get_a_specific_userdata(phone_number):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id, phone_number, query, response, timestamp
            FROM users
            WHERE phone_number = ?
            ORDER BY timestamp DESC
        ''', (phone_number,))
        results = c.fetchall()
        return [
            {
                'id': row[0],
                'phone_number': row[1],
                'query': row[2],
                'response': row[3],
                'timestamp': row[4]
            }
            for row in results
        ]
    finally:
        conn.close()
if __name__ == "__main__":
    init_db()
