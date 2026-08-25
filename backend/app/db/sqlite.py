"""SQLite connection helper for mediassist.db.

Path comes from the MEDIASSIST_DB_PATH environment variable (see
app/core/config.py) - never hardcoded, so the same code runs on Windows and
Linux regardless of where the dataset lives on disk.
"""
import sqlite3
from contextlib import contextmanager

from app.core.config import get_settings

settings = get_settings()


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(settings.mediassist_db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def is_database_reachable() -> bool:
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def get_schema_summary() -> str:
    """Human-readable schema dump (table + columns) - useful context when
    building the NL -> SQL prompt for Component 4's sql_rag_chain."""
    lines: list[str] = []
    with get_connection() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for table in tables:
            table_name = table["name"]
            lines.append(f"Table: {table_name}")
            columns = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            for col in columns:
                lines.append(f"  - {col['name']} ({col['type']})")
    return "\n".join(lines)
