import json
import os
import sqlite3

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "user_count.db")

def _get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_FILE)

def _init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_counts (
        chat_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        count INTEGER NOT NULL,
        PRIMARY KEY (chat_id, user_id)
        )    
        """
    )
    conn.commit()

def get_count(chat_id: str, user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id,),
        ).fetchone()
        return row[0] if row else 0
    
def increment_count(chat_id: str, user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO user_counts (chat_id, user_id, count)
            VALUES(?, ?, 1)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1        
            """,
            (chat_id, user_id,),
        )
        conn.commit()
        return conn.execute(
            "SELECT count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id,),
        ).fetchone()[0]
    
def get_group_total(chat_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(count), 0) FROM user_counts WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
        return row[0] if row else 0