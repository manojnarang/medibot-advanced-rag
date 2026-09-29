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


_MAX_DISTINCT_VALUES_TO_SHOW = 15


def get_schema_summary() -> str:
    """Human-readable schema dump (table + columns), including the actual
    distinct values for low-cardinality TEXT columns (status, department,
    claim_type, etc.) - context for Component 4's NL -> SQL prompt, so the
    model filters on real values instead of guessing plausible-sounding ones
    that don't exist and silently return zero rows. High-cardinality columns
    (names, IDs, free text) are left alone since listing every value would
    be noise.
    """
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
                col_name, col_type = col["name"], col["type"]
                line = f"  - {col_name} ({col_type})"
                if col_type.upper() == "TEXT":
                    distinct = conn.execute(
                        f"SELECT DISTINCT {col_name} FROM {table_name} "
                        f"WHERE {col_name} IS NOT NULL LIMIT {_MAX_DISTINCT_VALUES_TO_SHOW + 1}"
                    ).fetchall()
                    values = [row[0] for row in distinct]
                    if 0 < len(values) <= _MAX_DISTINCT_VALUES_TO_SHOW:
                        line += f" - values: {values}"
                lines.append(line)
    return "\n".join(lines)
