import sqlite3

from suggestions.generator import LLMSuggestionsResponse

from db_config import DB_PATH


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_en TEXT NOT NULL,
            text_es TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def read_from_db() -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT text_en, text_es FROM suggestions").fetchall()
    conn.close()
    if not rows:
        return None
    return {"suggestions": [dict(row) for row in rows]}


def write_to_db(data: LLMSuggestionsResponse) -> None:
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("DELETE FROM suggestions")
        conn.executemany(
            "INSERT INTO suggestions (text_en, text_es) VALUES (?, ?)",
            [(item.text_en, item.text_es) for item in data.suggestions],
        )
    conn.close()


def clear() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM suggestions")
    conn.commit()
    conn.close()
