import sqlite3
from pathlib import Path

from insights.insights_generator import LLMInsightsResponse

# NOTE: If InsightItem or LLMInsightsResponse fields change, drop and recreate the table
# manually (DELETE the DB file) — CREATE TABLE IF NOT EXISTS will not detect schema drift.
DB_PATH = Path(__file__).parent.parent.parent / "insights.db"


def init_db() -> None:
    """Create the insights table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            value TEXT NOT NULL,
            recommendation TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def read_from_db() -> dict | None:
    """Return cached insights as a dict, or None if the table is empty."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT text, value, recommendation FROM insights").fetchall()
    conn.close()
    if not rows:
        return None
    return {"insights": [dict(row) for row in rows]}


def write_to_db(data: LLMInsightsResponse) -> None:
    """Replace all rows with the new insights in a single transaction."""
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("DELETE FROM insights")
        conn.executemany(
            "INSERT INTO insights (text, value, recommendation) VALUES (?, ?, ?)",
            [(item.text, item.value, item.recommendation) for item in data.insights],
        )
    conn.close()


def clear_rows() -> None:
    """Delete all rows without removing the DB file (used on ValidationError recovery)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM insights")
    conn.commit()
    conn.close()
