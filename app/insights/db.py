import sqlite3

from insights.insights_generator import LLMInsightsResponse

from db_config import DB_PATH


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_en TEXT NOT NULL,
            text_es TEXT NOT NULL,
            value TEXT NOT NULL,
            recommendation_en TEXT NOT NULL,
            recommendation_es TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def read_from_db() -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT text_en, text_es, value, recommendation_en, recommendation_es FROM insights"
    ).fetchall()
    conn.close()
    if not rows:
        return None
    return {"insights": [dict(row) for row in rows]}


def write_to_db(data: LLMInsightsResponse) -> None:
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("DELETE FROM insights")
        conn.executemany(
            """INSERT INTO insights
               (text_en, text_es, value, recommendation_en, recommendation_es)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (item.text_en, item.text_es, item.value, item.recommendation_en, item.recommendation_es)
                for item in data.insights
            ],
        )
    conn.close()


def clear_rows() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM insights")
    conn.commit()
    conn.close()
