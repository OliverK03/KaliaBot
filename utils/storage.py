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
        user_id TEXT PRIMARY KEY,
        count INTEGER NOT NULL
        )    
        """
    )
    conn.commit()

def get_count(user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT count FROM user_counts WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return row[0] if row else 0
    
def increment_count(user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO user_counts (user_id, count)
            VALUES(?, 1)
            ON CONFLICT(user_id) DO UPDATE SET count = count + 1        
            """,
            (user_id,),
        )
        conn.commit()
        return conn.execute(
            "SELECT count FROM user_counts WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]