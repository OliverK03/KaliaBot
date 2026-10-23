import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator
from uuid import uuid4

import psycopg


class _PostgresConnection:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def execute(self, statement: str, params: tuple = ()):
        return self._connection.execute(statement.replace("?", "%s"), params)

    def executemany(self, statement: str, params):
        with self._connection.cursor() as cursor:
            return cursor.executemany(statement.replace("?", "%s"), params)

    def commit(self) -> None:
        self._connection.commit()


@contextmanager
def _get_connection(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL must be set to connect to PostgreSQL.")

    raw_connection = psycopg.connect(url)
    connection = _PostgresConnection(raw_connection)
    try:
        yield connection
        raw_connection.commit()
    except Exception:
        raw_connection.rollback()
        raise
    finally:
        raw_connection.close()


@contextmanager
def get_database_connection(
    database_url: str | None = None,
) -> Generator[object, None, None]:
    with _get_connection(database_url) as conn:
        _init_db(conn)
        yield conn


def _init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_counts (
        chat_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        count INTEGER NOT NULL,
        pyha_count INTEGER NOT NULL DEFAULT 0,
        holiton_count INTEGER NOT NULL DEFAULT 0,
        username TEXT,
        full_name TEXT,
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
        pyha_count INTEGER NOT NULL DEFAULT 0,
        holiton_count INTEGER NOT NULL DEFAULT 0,
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kalia_events (
        event_id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT,
        full_name TEXT,
        telegram_message_id BIGINT NOT NULL,
        occurred_at_utc TEXT NOT NULL
        )
        """
    )

    for table in ("user_counts", "monthly_counts"):
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
            "pyha_count INTEGER NOT NULL DEFAULT 0"
        )
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
            "holiton_count INTEGER NOT NULL DEFAULT 0"
        )
    conn.execute(
        "ALTER TABLE user_counts ADD COLUMN IF NOT EXISTS username TEXT"
    )
    conn.execute(
        "ALTER TABLE user_counts ADD COLUMN IF NOT EXISTS full_name TEXT"
    )

    for table in ("user_counts", "monthly_counts"):
        conn.execute(f"UPDATE {table} SET pyha_count = 0 WHERE pyha_count IS NULL")
        conn.execute(
            f"UPDATE {table} SET holiton_count = 0 WHERE holiton_count IS NULL"
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
    
def get_pyhat(chat_id: str, user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT pyha_count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row[0] if row else 0


def _increment_count(
    conn,
    chat_id: str,
    user_id: str,
    month_key: str,
    username: str | None,
    full_name: str | None,
) -> int:
    conn.execute(
        """
        INSERT INTO user_counts (chat_id, user_id, count, pyha_count, username, full_name)
        VALUES (?, ?, 1, 0, ?, ?)
        ON CONFLICT(chat_id, user_id) DO UPDATE SET
            count = user_counts.count + 1,
            username = COALESCE(NULLIF(excluded.username, ''), user_counts.username),
            full_name = COALESCE(NULLIF(excluded.full_name, ''), user_counts.full_name)
        """,
        (chat_id, user_id, username, full_name),
    )
    conn.execute(
        """
        INSERT INTO monthly_counts (chat_id, user_id, year_month, count, pyha_count)
        VALUES (?, ?, ?, 1, 0)
        ON CONFLICT(chat_id, user_id, year_month) DO UPDATE SET
            count = monthly_counts.count + 1
        """,
        (chat_id, user_id, month_key),
    )
    return conn.execute(
        "SELECT count FROM user_counts WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    ).fetchone()[0]


def increment_count(
    chat_id: str,
    user_id: str,
    year_month: str | None = None,
    username: str | None = None,
    full_name: str | None = None,
) -> int:
    month_key = year_month or _current_year_month()

    with _get_connection() as conn:
        _init_db(conn)
        count = _increment_count(
            conn, chat_id, user_id, month_key, username, full_name
        )
        conn.commit()
        return count


def increment_kalia_count(
    chat_id: str,
    user_id: str,
    telegram_message_id: int,
    occurred_at: datetime,
    username: str | None = None,
    full_name: str | None = None,
) -> int:
    if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
        raise ValueError("occurred_at must be timezone-aware")

    occurred_at_utc = occurred_at.astimezone(timezone.utc)
    month_key = occurred_at_utc.strftime("%Y-%m")
    with _get_connection() as conn:
        _init_db(conn)
        count = _increment_count(
            conn, chat_id, user_id, month_key, username, full_name
        )
        conn.execute(
            """
            INSERT INTO kalia_events (
                event_id, chat_id, user_id, username, full_name,
                telegram_message_id, occurred_at_utc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                chat_id,
                user_id,
                username,
                full_name,
                telegram_message_id,
                occurred_at_utc.isoformat(),
            ),
        )
        conn.commit()
        return count


def pyha_increment(
    chat_id: str,
    user_id: str,
    year_month: str | None = None,
    username: str | None = None,
    full_name: str | None = None,
) -> int:
    month_key = year_month or _current_year_month()
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO user_counts (chat_id, user_id, count, pyha_count, username, full_name)
            VALUES (?, ?, 0, 1, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                pyha_count = user_counts.pyha_count + 1,
                username = COALESCE(NULLIF(excluded.username, ''), user_counts.username),
                full_name = COALESCE(NULLIF(excluded.full_name, ''), user_counts.full_name)
            """,
            (chat_id, user_id, username, full_name),
        )
        conn.execute(
            """
            INSERT INTO monthly_counts (chat_id, user_id, year_month, count, pyha_count)
            VALUES (?, ?, ?, 0, 1)
            ON CONFLICT(chat_id, user_id, year_month) DO UPDATE SET
                pyha_count = monthly_counts.pyha_count + 1
            """,
            (chat_id, user_id, month_key),
        )
        conn.commit()
        row = conn.execute(
            "SELECT pyha_count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row[0] if row else 0

def get_holiton(chat_id: str, user_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT holiton_count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row[0] if row else 0

def increment_holiton(
    chat_id: str,
    user_id: str,
    year_month: str | None = None,
    username: str | None = None,
    full_name: str | None = None,
) -> int:
    month_key = year_month or _current_year_month()
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO user_counts (chat_id, user_id, count, pyha_count, holiton_count, username, full_name)
            VALUES (?, ?, 0, 0, 1, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                holiton_count = user_counts.holiton_count + 1,
                username = COALESCE(NULLIF(excluded.username, ''), user_counts.username),
                full_name = COALESCE(NULLIF(excluded.full_name, ''), user_counts.full_name)
            """,
            (chat_id, user_id, username, full_name),
        )
        conn.execute(
            """
            INSERT INTO monthly_counts (chat_id, user_id, year_month, count, pyha_count, holiton_count)
            VALUES (?, ?, ?, 0, 0, 1)
            ON CONFLICT(chat_id, user_id, year_month) DO UPDATE SET
                holiton_count = monthly_counts.holiton_count + 1
            """,
            (chat_id, user_id, month_key),
        )
        conn.commit()
        row = conn.execute(
            "SELECT holiton_count FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row[0] if row else 0

def get_group_total(chat_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(count), 0) FROM user_counts WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
        return row[0] if row else 0
    
def get_group_pyhat(chat_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(pyha_count), 0) FROM user_counts WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
        return row[0] if row else 0

def get_group_holittomat(chat_id: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(holiton_count), 0) FROM user_counts WHERE chat_id = ?",
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


def get_cached_display_name(chat_id: str, user_id: str) -> str | None:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT username, full_name FROM user_counts WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return None

        username, full_name = row
        if username:
            return f"@{username}"
        if full_name:
            return full_name
        return None


def cache_user_name(
    chat_id: str,
    user_id: str,
    username: str | None,
    full_name: str | None,
) -> None:
    with _get_connection() as conn:
        _init_db(conn)
        conn.execute(
            """
            UPDATE user_counts
            SET username  = COALESCE(NULLIF(?, ''), username),
                full_name = COALESCE(NULLIF(?, ''), full_name)
            WHERE chat_id = ? AND user_id = ?
            """,
            (username, full_name, chat_id, user_id),
        )
        conn.commit()


def get_pyhascoreboard(chat_id: str, limit: int = 10) -> list[tuple[str, int]]:
    with _get_connection() as conn:
        _init_db(conn)
        return conn.execute(
            """
            SELECT user_id, pyha_count
            FROM user_counts
            WHERE chat_id = ?
            ORDER BY pyha_count DESC, user_id ASC
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
    
def get_monthly_pyhascoreboard(chat_id: str, year_month: str, limit: int = 10) -> list[tuple[str, int]]:
    with _get_connection() as conn:
        _init_db(conn)
        return conn.execute(
            """
            SELECT user_id, pyha_count
            FROM monthly_counts
            WHERE chat_id = ? AND year_month = ?
            ORDER BY pyha_count DESC, user_id ASC
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
    
def get_monthly_group_pyha_total(chat_id: str, year_month: str) -> int:
    with _get_connection() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT COALESCE(SUM(pyha_count), 0) FROM monthly_counts WHERE chat_id = ? AND year_month = ?",
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
            INSERT INTO monthly_reports (chat_id, year_month, sent_at)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, year_month) DO UPDATE SET sent_at = excluded.sent_at
            """,
            (chat_id, year_month, datetime.utcnow().isoformat()),
        )
        conn.commit()