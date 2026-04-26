import json
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).parent.parent / os.getenv("DB_NAME", "hotel_financial_insights.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id          TEXT PRIMARY KEY,
            module      TEXT NOT NULL,
            description TEXT,
            endpoint    TEXT NOT NULL,
            input       TEXT NOT NULL,
            criteria    TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id        TEXT NOT NULL,
            test_case_id  TEXT NOT NULL,
            response      TEXT,
            scores        TEXT,
            overall_score REAL,
            passed        INTEGER,
            latency_ms    INTEGER,
            error         TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def upsert_test_case(
    id: str,
    module: str,
    description: str,
    endpoint: str,
    input_payload: dict,
    criteria: list[str],
) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO test_cases (id, module, description, endpoint, input, criteria)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            module      = excluded.module,
            description = excluded.description,
            endpoint    = excluded.endpoint,
            input       = excluded.input,
            criteria    = excluded.criteria
        """,
        (id, module, description, endpoint, json.dumps(input_payload), json.dumps(criteria)),
    )
    conn.commit()
    conn.close()


def get_test_cases(module: str | None = None, case_id: str | None = None) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if case_id:
        rows = conn.execute("SELECT * FROM test_cases WHERE id = ?", (case_id,)).fetchall()
    elif module:
        rows = conn.execute("SELECT * FROM test_cases WHERE module = ?", (module,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM test_cases ORDER BY module, id").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["input"] = json.loads(d["input"])
        d["criteria"] = json.loads(d["criteria"])
        result.append(d)
    return result


def save_evaluation(
    run_id: str,
    test_case_id: str,
    response: str | None,
    scores: list[dict] | None,
    overall_score: float,
    passed: bool,
    latency_ms: int,
    error: str | None = None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO evaluations
            (run_id, test_case_id, response, scores, overall_score, passed, latency_ms, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            test_case_id,
            response,
            json.dumps(scores) if scores else None,
            overall_score,
            int(passed),
            latency_ms,
            error,
        ),
    )
    conn.commit()
    conn.close()


def get_run_results(run_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM evaluations WHERE run_id = ? ORDER BY id", (run_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["scores"] = json.loads(d["scores"]) if d["scores"] else []
        result.append(d)
    return result


def list_runs() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT
            run_id,
            MIN(created_at)               AS started_at,
            COUNT(*)                      AS total,
            SUM(passed)                   AS passed,
            COUNT(*) - SUM(passed)        AS failed,
            ROUND(AVG(overall_score), 3)  AS avg_score
        FROM evaluations
        GROUP BY run_id
        ORDER BY started_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_evaluation(test_case_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM evaluations WHERE test_case_id = ? ORDER BY created_at DESC LIMIT 1",
        (test_case_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["scores"] = json.loads(d["scores"]) if d["scores"] else []
    return d


def get_run_full(run_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT e.test_case_id, e.overall_score, e.passed, e.latency_ms, e.error,
               e.response, e.scores, e.created_at,
               t.description, t.module, t.endpoint, t.input, t.criteria
        FROM evaluations e
        JOIN test_cases t ON t.id = e.test_case_id
        WHERE e.run_id = ?
        ORDER BY t.module, e.test_case_id
    """, (run_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["scores"] = json.loads(d["scores"]) if d["scores"] else []
        d["input"] = json.loads(d["input"]) if d["input"] else {}
        d["criteria"] = json.loads(d["criteria"]) if d["criteria"] else []
        result.append(d)
    return result


def get_run_detail(run_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT e.test_case_id, e.overall_score, e.passed, e.latency_ms, e.error,
               t.description, t.module
        FROM evaluations e
        JOIN test_cases t ON t.id = e.test_case_id
        WHERE e.run_id = ?
        ORDER BY t.module, e.test_case_id
    """, (run_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
