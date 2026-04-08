import os
import sqlite3
from datetime import datetime

DATA_DIR = os.getenv("DATA_DIR", "data")
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS monthly_counts (
        chat_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        year_month TEXT NOT NULL,
        count INTEGER NOT NULL,
        PRIMARY KEY (chat_id, user_id, year_month)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS monthly_reports (
        chat_id TEXT NOT NULL,
        year_month TEXT NOT NULL,
        sent_at TEXT NOT NULL,
        PRIMARY KEY (chat_id, year_month)
        )
        """
    )
    conn.commit()


def _current_year_month() -> str:
    return datetime.now().strftime("%Y-%m")


def get_count(chat_id: str, user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row[0] if row else 0


def increment_count(chat_id: str, user_id: str, year_month: str | None = None) -> int:
    month_key = year_month or _current_year_month()

    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO user_counts (chat_id, user_id, count)
            VALUES (?, ?, 1)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1
            """,
            (chat_id, user_id),
        )
        conn.execute(
            """
            INSERT INTO monthly_counts (chat_id, user_id, year_month, count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(chat_id, user_id, year_month) DO UPDATE SET count = count + 1
            """,
            (chat_id, user_id, month_key),
        )
        conn.commit()
        return conn.execute(
            "SELECT count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()[0]


def get_group_total(chat_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(count), 0) FROM user_counts WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
        return row[0] if row else 0


def get_scoreboard(chat_id: str, limit: int = 10) -> list[tuple[str, int]]:
    with _get_connection() as conn:
        _init_db(conn)
        return conn.execute(
            """
            SELECT user_id, count
            FROM user_counts
            WHERE chat_id = ?
            ORDER BY count DESC, user_id ASC
            LIMIT ?
            """,
            (chat_id, limit),
        ).fetchall()


def get_monthly_scoreboard(chat_id: str, year_month: str, limit: int = 10) -> list[tuple[str, int]]:
    with _get_connection() as conn:
        _init_db(conn)
        return conn.execute(
            """
            SELECT user_id, count
            FROM monthly_counts
            WHERE chat_id = ? AND year_month = ?
            ORDER BY count DESC, user_id ASC
            LIMIT ?
            """,
            (chat_id, year_month, limit),
        ).fetchall()


def get_monthly_group_total(chat_id: str, year_month: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(count), 0) FROM monthly_counts WHERE chat_id = ? AND year_month = ?",
            (chat_id, year_month),
        ).fetchone()
        return row[0] if row else 0


def get_all_chat_ids() -> list[str]:
    with _get_connection() as conn:
        _init_db(conn)
        rows = conn.execute(
            """
            SELECT DISTINCT chat_id FROM user_counts
            UNION
            SELECT DISTINCT chat_id FROM monthly_counts
            ORDER BY chat_id
            """
        ).fetchall()
        return [row[0] for row in rows]


def has_monthly_report_been_sent(chat_id: str, year_month: str) -> bool:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT 1 FROM monthly_reports WHERE chat_id = ? AND year_month = ?",
            (chat_id, year_month),
        ).fetchone()
        return row is not None


def mark_monthly_report_sent(chat_id: str, year_month: str):
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT OR REPLACE INTO monthly_reports (chat_id, year_month, sent_at)
            VALUES (?, ?, ?)
            """,
            (chat_id, year_month, datetime.utcnow().isoformat()),
        )
        conn.commit()