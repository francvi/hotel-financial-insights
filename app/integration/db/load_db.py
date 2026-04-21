import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "hotel_kpi.db")

base_dir = os.getcwd()
sqlite_db = os.path.join(base_dir, DB_NAME)

PNL_CSV = os.path.join(base_dir, "data/DATASET_P&L.csv")
MASTER_CSV = os.path.join(base_dir, "data/TABLA_MAESTRA.csv")

if not os.path.exists(sqlite_db):
    pnl = pd.read_csv(PNL_CSV)
    master = pd.read_csv(MASTER_CSV)

    conn = sqlite3.connect(sqlite_db)

    pnl.to_sql("pnl", conn, if_exists="replace", index=False)
    master.to_sql("hotels", conn, if_exists="replace", index=False)

    print(f"Loaded {len(pnl)} P&L rows and {len(master)} hotel master rows into '{DB_NAME}'")
    conn.close()
else:
    print(f"Database '{DB_NAME}' already exists. Skipping import.")
