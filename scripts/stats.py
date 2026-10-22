import argparse
import os
import sqlite3
import sys
from typing import Any

import psycopg
from utils.storage import get_database_connection

def resolve_db_path(explicit_path: str | None) -> str:
    if explicit_path:
        return explicit_path
    data_dir = os.getenv("DATA_DIR", "data")
    return os.path.join(data_dir, "user_count.db")


def get_scalar(conn: Any, sql: str, params: tuple = ()) -> int:
    row = conn.execute(sql, params).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def print_summary(conn: Any) -> None:
    total_users = get_scalar(conn, "SELECT COUNT(DISTINCT user_id) FROM user_counts")
    users_over_five = get_scalar(conn, "SELECT COUNT(DISTINCT user_id) FROM user_counts WHERE count > 5")
    total_kalia = get_scalar(conn, "SELECT COALESCE(SUM(count), 0) FROM user_counts")
    total_pyha = get_scalar(conn, "SELECT COALESCE(SUM(pyha_count), 0) FROM user_counts")


    print(f"Total unique users: {total_users}")
    print(f"User with more than 5 kalia: {users_over_five}")
    print(f"Total kalia count: {total_kalia}")
    print(f"Total pyha count: {total_pyha}")
    print()
    print("Per-chat breakdown:")

    rows = conn.execute(
        """
        SELECT
            chat_id,
            COUNT(DISTINCT user_id) AS users,
            COALESCE(SUM(count), 0) AS kalia_total,
            COALESCE(SUM(pyha_count), 0) AS pyha_total
        FROM user_counts
        GROUP BY chat_id
        ORDER BY users DESC, kalia_total DESC, chat_id ASC
        """
    ).fetchall()

    if not rows:
        print("No usage data found.")
        return

    for chat_id, users, kalia_total, pyha_total in rows:
        print(
            f"chat_id={chat_id} | users={users} | "
            f"kalia_total={kalia_total} | pyha_total={pyha_total}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print usage stats from the bot database."
    )
    parser.add_argument(
        "--db",
        dest="db_path",
        help=(
            "Path to a SQLite database file. If omitted, uses DATABASE_URL when "
            "set, otherwise $DATA_DIR/user_count.db."
        ),
    )
    args = parser.parse_args()

    db_path = resolve_db_path(args.db_path)
    uses_postgres = args.db_path is None and bool(os.getenv("DATABASE_URL"))

    if not uses_postgres and not os.path.exists(db_path):
        print(f"Database not found at: {db_path}", file=sys.stderr)
        print(
            "Set DATA_DIR correctly or pass --db /path/to/user_count.db",
            file=sys.stderr,
        )
        return 1

    try:
        with get_database_connection(db_path=args.db_path) as conn:
            print(
                "Database: PostgreSQL"
                if uses_postgres
                else f"Database: {db_path}"
            )
            print_summary(conn)
    except (sqlite3.Error, psycopg.Error) as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
