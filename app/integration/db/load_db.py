import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DB_NAME = os.getenv("DB_NAME", "hotel_kpi.db")
CSV_FILE = "data/hotel_financial_dataset_upgraded.csv"

base_dir = os.getcwd()
print(base_dir)
csv_file = os.path.join(base_dir, CSV_FILE)
print(csv_file)
sqlite_db = os.path.join(base_dir, DB_NAME)

# Only create DB and import CSV if DB does not exist
if not os.path.exists(sqlite_db):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_file)

    # Connect to SQLite database (creates new DB)
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Write DataFrame to SQL table
    df.to_sql("hotel_kpi", conn, if_exists="replace", index=False)

    # Test query: fetch first 5 rows
    cursor.execute("SELECT * FROM hotel_kpi LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Close connection
    conn.close()
else:
    print(f"Database '{DB_NAME}' already exists. Skipping import.")
