import sqlite3

from db_config import DB_PATH


def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id       TEXT    NOT NULL,
            rating           INTEGER NOT NULL CHECK(rating IN (1, -1)),
            comment          TEXT,
            message_content  TEXT,
            conversation     TEXT,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Migrate existing DBs that predate message_content / conversation columns
    for col, typedef in [("message_content", "TEXT"), ("conversation", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE feedback ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


_init_db()


def save_feedback(
    message_id: str,
    rating: int,
    comment: str | None,
    message_content: str | None,
    conversation: str | None,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    with conn:
        cur = conn.execute(
            """INSERT INTO feedback (message_id, rating, comment, message_content, conversation)
               VALUES (?, ?, ?, ?, ?)""",
            (message_id, rating, comment or None, message_content or None, conversation or None),
        )
        return cur.lastrowid
