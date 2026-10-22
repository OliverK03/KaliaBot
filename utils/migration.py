import os
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import datetime

from utils.storage import get_database_connection

_MIGRATION_NAME = "sqlite_to_postgres_v1"
_TABLE_COLUMNS = {
    "user_counts": {
        "columns": (
            "chat_id",
            "user_id",
            "count",
            "pyha_count",
            "holiton_count",
            "username",
            "full_name",
        ),
        "required": ("chat_id", "user_id", "count"),
        "defaults": {"pyha_count": 0, "holiton_count": 0},
    },
    "monthly_counts": {
        "columns": (
            "chat_id",
            "user_id",
            "year_month",
            "count",
            "pyha_count",
            "holiton_count",
        ),
        "required": ("chat_id", "user_id", "year_month", "count"),
        "defaults": {"pyha_count": 0, "holiton_count": 0},
    },
    "monthly_reports": {
        "columns": ("chat_id", "year_month", "sent_at"),
        "required": ("chat_id", "year_month", "sent_at"),
        "defaults": {},
    },
}


def _read_sqlite_tables(sqlite_path: str) -> dict[str, list[tuple]]:
    tables: dict[str, list[tuple]] = {}
    with closing(sqlite3.connect(sqlite_path)) as source:
        source.row_factory = sqlite3.Row
        existing_tables = {
            row[0]
            for row in source.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

        for table, definition in _TABLE_COLUMNS.items():
            if table not in existing_tables:
                raise ValueError(f"SQLite database is missing required table: {table}")

            source_columns = {
                row[1] for row in source.execute(f"PRAGMA table_info({table})")
            }
            missing_required = set(definition["required"]) - source_columns
            if missing_required:
                raise ValueError(
                    f"SQLite table {table} is missing required columns: "
                    f"{', '.join(sorted(missing_required))}"
                )

            selected_columns = definition["columns"]
            query = ", ".join(
                column if column in source_columns else "NULL AS " + column
                for column in selected_columns
            )
            rows = source.execute(f"SELECT {query} FROM {table}").fetchall()
            defaults = definition["defaults"]
            tables[table] = [
                tuple(
                    defaults.get(column, row[column])
                    if row[column] is None and column in defaults
                    else row[column]
                    for column in selected_columns
                )
                for row in rows
            ]
    return tables


def _verify_import(target, source_tables: dict[str, list[tuple]]) -> None:
    totals_to_check = {
        "user_counts": ("count", "pyha_count", "holiton_count"),
        "monthly_counts": ("count", "pyha_count", "holiton_count"),
    }
    for table, rows in source_tables.items():
        imported_count = target.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        if imported_count != len(rows):
            raise RuntimeError(
                f"Verification failed for {table}: expected {len(rows)} rows, "
                f"found {imported_count}"
            )

        for column in totals_to_check.get(table, ()):
            column_index = _TABLE_COLUMNS[table]["columns"].index(column)
            expected_total = sum(row[column_index] or 0 for row in rows)
            imported_total = target.execute(
                f"SELECT COALESCE(SUM({column}), 0) FROM {table}"
            ).fetchone()[0]
            if imported_total != expected_total:
                raise RuntimeError(
                    f"Verification failed for {table}.{column}: "
                    f"expected {expected_total}, found {imported_total}"
                )


def migrate_sqlite_to_postgres(
    sqlite_path: str, database_url: str | None = None
) -> bool:
    """Copy the bot's SQLite tables into an empty PostgreSQL database once."""
    database_url = database_url or os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is required for the PostgreSQL migration")
    if not os.path.isfile(sqlite_path):
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    source_tables = _read_sqlite_tables(sqlite_path)
    with get_database_connection(database_url=database_url) as target:
        target.execute(
            """
            CREATE TABLE IF NOT EXISTS kaliabot_migrations (
                name TEXT PRIMARY KEY,
                completed_at TEXT NOT NULL
            )
            """
        )
        completed = target.execute(
            "SELECT 1 FROM kaliabot_migrations WHERE name = ?",
            (_MIGRATION_NAME,),
        ).fetchone()
        if completed:
            print("SQLite migration already completed; no data was changed.")
            return False

        for table in _TABLE_COLUMNS:
            existing_count = target.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            if existing_count:
                raise RuntimeError(
                    f"Refusing to import into non-empty PostgreSQL table {table}."
                )

        for table, rows in source_tables.items():
            if not rows:
                continue
            columns: Sequence[str] = _TABLE_COLUMNS[table]["columns"]
            column_sql = ", ".join(columns)
            placeholders = ", ".join("?" for _ in columns)
            target.executemany(
                f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})",
                rows,
            )

        _verify_import(target, source_tables)
        target.execute(
            "INSERT INTO kaliabot_migrations (name, completed_at) VALUES (?, ?)",
            (_MIGRATION_NAME, datetime.now().isoformat()),
        )

    print(
        "SQLite migration verified: "
        + ", ".join(
            f"{table}={len(rows)} rows" for table, rows in source_tables.items()
        )
    )
    return True
