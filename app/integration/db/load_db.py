import sqlite3
from pathlib import Path

import pandas as pd

from db_config import DB_PATH

_base = Path(__file__).parent.parent.parent.parent
PNL_CSV = _base / "data" / "DATASET_P&L.csv"
MASTER_CSV = _base / "data" / "TABLA_MAESTRA.csv"


def ensure_loaded() -> None:
    conn = sqlite3.connect(DB_PATH)
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='pnl'"
    ).fetchone() is not None
    conn.close()

    if exists:
        return

    pnl = pd.read_csv(PNL_CSV)
    master = pd.read_csv(MASTER_CSV)

    conn = sqlite3.connect(DB_PATH)
    pnl.to_sql("pnl", conn, if_exists="replace", index=False)
    master.to_sql("hotels", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(pnl)} P&L rows and {len(master)} hotel master rows into '{DB_PATH.name}'")
