import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "hotel_kpi.db")

base_dir = os.getcwd()
sqlite_db = os.path.join(base_dir, DB_NAME)


class KpiService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.df = None
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        pnl = pd.read_sql_query("SELECT * FROM pnl", conn)
        hotels = pd.read_sql_query("SELECT * FROM hotels", conn)
        conn.close()

        df = pnl.merge(hotels, on="HOTEL", how="left")
        # Drop rows with no operations (seasonal closures / future REAL placeholders)
        df = df[df["HABITACIONES"] > 0].copy()

        df["OCC"] = df["RN"] / df["HABITACIONES"]
        df["ADR"] = df["ROOMS_REVENUE"] / df["RN"].replace(0, pd.NA)
        df["REVPAR"] = df["ROOMS_REVENUE"] / df["HABITACIONES"]
        df["GOP_MARGIN"] = df["GOP"] / df["OPERATING_REVENUE"].replace(0, pd.NA)

        self.df = df

    def _agg_real_budget(self, group_cols: list, metric_cols: list) -> pd.DataFrame:
        real = (
            self.df[self.df["ESCENARIO"] == "REAL"]
            .groupby(group_cols)[metric_cols]
            .mean()
        )
        budget = (
            self.df[self.df["ESCENARIO"] == "BUDGET"]
            .groupby(group_cols)[metric_cols]
            .mean()
        )

        merged = real.join(budget, lsuffix="_REAL", rsuffix="_BUDGET").reset_index()
        for col in metric_cols:
            merged[f"{col}_VAR"] = merged[f"{col}_REAL"] - merged[f"{col}_BUDGET"]
        return merged

    def overall_kpis_annual(self) -> pd.DataFrame:
        """Returns all KPIs across all hotels aggregated by year"""
        return self._agg_real_budget(
            ["ANIO"], ["OCC", "ADR", "REVPAR", "GOP", "GOP_MARGIN"]
        )

    def kpis_by_hotel_annual(self) -> pd.DataFrame:
        """Returns all KPIs by hotel aggregated by year"""
        return self._agg_real_budget(
            ["HOTEL", "ANIO"], ["OCC", "ADR", "REVPAR", "GOP", "GOP_MARGIN"]
        )

    def kpis_monthly(self, year: int = 2025) -> pd.DataFrame:
        """Returns all KPIs aggregated by month for the given year"""

        df = self.df[self.df["ANIO"] == year]

        real = (
            df[df["ESCENARIO"] == "REAL"]
            .groupby("MES")[["OCC", "ADR", "REVPAR", "GOP_MARGIN"]]
            .mean()
        )
        budget = (
            df[df["ESCENARIO"] == "BUDGET"]
            .groupby("MES")[["OCC", "ADR", "REVPAR", "GOP_MARGIN"]]
            .mean()
        )

        merged = real.join(budget, lsuffix="_REAL", rsuffix="_BUDGET").reset_index()
        for col in ["OCC", "ADR", "REVPAR", "GOP_MARGIN"]:
            merged[f"{col}_VAR"] = merged[f"{col}_REAL"] - merged[f"{col}_BUDGET"]
        return merged

    def format_kpi_markdown(self) -> str:
        annual = self.overall_kpis_annual()
        by_hotel = self.kpis_by_hotel_annual()
        monthly = self.kpis_monthly(year=2025)

        def pct(val):
            if pd.isna(val):
                return "N/A"
            return f"{val * 100:.1f}%"

        def usd(val):
            if pd.isna(val):
                return "N/A"
            return f"{val:.2f}"

        # Overall annual
        md = "## Overall Annual KPIs (REAL vs BUDGET)\n"
        rows = []
        for _, r in annual.iterrows():
            rows.append(
                {
                    "Year": int(r["ANIO"]),
                    "Occ_Real": pct(r.get("OCC_REAL")),
                    "Occ_Bdg": pct(r.get("OCC_BUDGET")),
                    "Occ_Var": pct(r.get("OCC_VAR")),
                    "ADR_Real": usd(r.get("ADR_REAL")),
                    "ADR_Bdg": usd(r.get("ADR_BUDGET")),
                    "RevPAR_Real": usd(r.get("REVPAR_REAL")),
                    "RevPAR_Bdg": usd(r.get("REVPAR_BUDGET")),
                    "GOP_Margin_Real": pct(r.get("GOP_MARGIN_REAL")),
                    "GOP_Margin_Bdg": pct(r.get("GOP_MARGIN_BUDGET")),
                }
            )
        md += pd.DataFrame(rows).to_markdown(index=False) + "\n\n"

        # Monthly 2025
        md += "## Monthly KPIs 2025 (REAL vs BUDGET)\n"
        mrows = []
        for _, r in monthly.iterrows():
            mrows.append(
                {
                    "Month": int(r["MES"]),
                    "Occ_Real": pct(r.get("OCC_REAL")),
                    "Occ_Bdg": pct(r.get("OCC_BUDGET")),
                    "Occ_Var": pct(r.get("OCC_VAR")),
                    "ADR_Real": usd(r.get("ADR_REAL")),
                    "ADR_Var": usd(r.get("ADR_VAR")),
                    "RevPAR_Real": usd(r.get("REVPAR_REAL")),
                    "RevPAR_Var": usd(r.get("REVPAR_VAR")),
                    "GOP_Margin_Real": pct(r.get("GOP_MARGIN_REAL")),
                    "GOP_Margin_Var": pct(r.get("GOP_MARGIN_VAR")),
                }
            )
        md += pd.DataFrame(mrows).to_markdown(index=False) + "\n\n"

        # By hotel 2025 REAL
        real_2025 = self.df[
            (self.df["ESCENARIO"] == "REAL") & (self.df["ANIO"] == 2025)
        ]
        hotel_summary = (
            real_2025.groupby("HOTEL")[["OCC", "ADR", "REVPAR", "GOP_MARGIN", "GOP"]]
            .mean()
            .reset_index()
        )
        hotel_summary = hotel_summary.sort_values("REVPAR", ascending=False)
        hotel_summary["OCC"] = hotel_summary["OCC"].apply(pct)
        hotel_summary["ADR"] = hotel_summary["ADR"].apply(usd)
        hotel_summary["REVPAR"] = hotel_summary["REVPAR"].apply(usd)
        hotel_summary["GOP_MARGIN"] = hotel_summary["GOP_MARGIN"].apply(pct)
        hotel_summary["GOP"] = hotel_summary["GOP"].apply(lambda v: f"{v:,.0f}")
        hotel_summary.columns = [
            "Hotel",
            "Occ",
            "ADR",
            "RevPAR",
            "GOP_Margin",
            "GOP_Avg",
        ]

        md += "## Hotel Ranking 2025 REAL (by RevPAR)\n"
        md += hotel_summary.to_markdown(index=False) + "\n"

        return md


kpi_service = KpiService(db_path=sqlite_db)
