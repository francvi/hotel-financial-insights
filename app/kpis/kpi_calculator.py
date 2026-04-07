import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "hotel_kpi.db")

base_dir = os.getcwd()
sqlite_db = os.path.join(base_dir, DB_NAME)


class KpiService:
    """
    A class to connect to SQLite and calculate occupancy rate KPIs with separate overall and per-hotel functions.
    """

    def __init__(self, db_path: str, table_name: str = "hotel_kpi"):
        self.db_path = db_path
        self.table_name = table_name
        self.df = None
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        self.df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)
        self.df["month"] = pd.to_datetime(self.df["month"])
        conn.close()
        self.df["occupancy_pct"] = self.df["occupancy_rate"] * 100

    def overall_occupancy_rate(self) -> dict:
        df = self.df.copy()
        df["year"] = df["month"].dt.year
        latest_year = df["year"].max()
        prev_year = latest_year - 1

        yearly = df.groupby("year")["occupancy_pct"].mean().reset_index()
        yearly["YoY"] = yearly["occupancy_pct"].diff()

        monthly_df = df[df["year"] == latest_year].copy()
        monthly_df["month"] = monthly_df["month"].dt.to_period("M").astype(str)
        monthly = monthly_df.groupby("month")["occupancy_pct"].mean().reset_index()
        monthly["YoY"] = monthly["occupancy_pct"].diff()

        return {"yearly": yearly, "monthly": monthly}

    def occupancy_rate_by_hotel(self) -> dict:
        df = self.df.copy()
        df["year"] = df["month"].dt.year
        latest_year = df["year"].max()

        yearly = (
            df.groupby(["hotel_name", "year"])["occupancy_pct"].mean().reset_index()
        )
        yearly["YoY"] = yearly.groupby("hotel_name")["occupancy_pct"].diff()

        monthly_df = df[df["year"] == latest_year].copy()
        monthly_df["month"] = monthly_df["month"].dt.to_period("M").astype(str)
        monthly = (
            monthly_df.groupby(["hotel_name", "month"])["occupancy_pct"]
            .mean()
            .reset_index()
        )
        monthly["YoY"] = monthly.groupby("hotel_name")["occupancy_pct"].diff()

        return {"yearly": yearly, "monthly": monthly}

    def format_occupancy_markdown(self) -> str:
        """
        Formats overall and by hotel occupancy rate into markdown tables suitable for LLM consumption.
        """
        overall = self.overall_occupancy_rate()
        by_hotel = self.occupancy_rate_by_hotel()

        md = "## Overall Occupancy Rate\n"
        md += "### Yearly\n"
        md += overall["yearly"].to_markdown(index=False) + "\n\n"
        md += "### Monthly\n"
        md += overall["monthly"].to_markdown(index=False) + "\n\n"

        md += "## Occupancy Rate by Hotel\n"
        md += "### Yearly\n"
        md += by_hotel["yearly"].to_markdown(index=False) + "\n\n"
        md += "### Monthly\n"
        md += by_hotel["monthly"].to_markdown(index=False) + "\n"

        return md


kpi_service = KpiService(db_path=sqlite_db)
markdown_output = kpi_service.format_occupancy_markdown()
