import argparse
import os
import sqlite3
import sys

import psycopg

from utils.migration import migrate_sqlite_to_postgres


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy KaliaBot data from SQLite into PostgreSQL."
    )
    parser.add_argument(
        "--sqlite",
        default=os.path.join(os.getenv("DATA_DIR", "data"), "user_count.db"),
        help="Path to the source SQLite database.",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL connection URL (defaults to DATABASE_URL).",
    )
    args = parser.parse_args()

    try:
        migrate_sqlite_to_postgres(args.sqlite, args.database_url)
    except (OSError, ValueError, RuntimeError, sqlite3.Error, psycopg.Error) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
