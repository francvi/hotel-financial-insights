import sqlite3
from pathlib import Path

import pandas as pd

from db_config import DB_PATH
from integration.db.load_db import ensure_loaded

ensure_loaded()

sqlite_db = str(DB_PATH)


class KpiService:
    # rn = rooms nights
    # Definición única de la lógica del negocio
    METRIC_FORMULAS = {
        # 1. CONTROL DE COSTES Y EFICIENCIA OPERATIVA (OPEX & LABOR)
        "CPOR": lambda d: d["ROOMS_OPEX"] / d["RN"],
        "CPH": lambda d: d["ROOMS_OPEX"] / d["HABITACIONES"],
        "LBC": lambda d: d["ROOMS_PERSONNEL"] / d["ROOMS_REVENUE"],
        "LPC_TOTAL": lambda d: (d["ROOMS_PERSONNEL"] + d["FB_PERSONNEL"])
        / d["OPERATING_REVENUE"],
        "UNDISTRIB_OPEX_Pct": lambda d: d["UNDISTRIB_OPEX"] / d["OPERATING_REVENUE"],
        "F&B_CPOR": lambda d: d["FB_OPEX"] / d["RN"],
        "F&B_CPH": lambda d: d["FB_OPEX"] / d["HABITACIONES"],
        "F&B_LBC": lambda d: d["FB_PERSONNEL"] / d["FB_REVENUE"],
        # 2. ANÁLISIS DETALLADO (ALIMENTOS Y BEBIDAS)
        "Food_Cost_Pct": lambda d: d["FOOD_COST"] / d["FOOD_REVENUE"],
        "Beverage_Cost_Pct": lambda d: d["BEVERAGE_COST"] / d["BEVERAGE_REVENUE"],
        "F&B_GOP_MARGIN": lambda d: d["FB_PROFIT"] / d["FB_REVENUE"],
        "F&B_REVPAR": lambda d: d["FB_REVENUE"] / d["HABITACIONES"],
        "F&B_GOPPAR": lambda d: d["FB_PROFIT"] / d["HABITACIONES"],
        "BANQUETS_CONTRIBUTION": lambda d: d["BANQUETS_REVENUE"] / d["FB_REVENUE"],
        "FB_PENSION_PCT": lambda d: d["FB_PENSION"] / d["FB_REVENUE"],
        # 3. REVENUE MANAGEMENT AVANZADO (VENTA Y CAPTACIÓN)
        "OCC": lambda d: d["RN"] / d["HABITACIONES"],
        "ADR": lambda d: d["ROOMS_REVENUE"] / d["RN"],
        "REVPAR": lambda d: d["ROOMS_REVENUE"] / d["HABITACIONES"],
        "TRevPAR": lambda d: d["OPERATING_REVENUE"] / d["HABITACIONES"],
        "RevPOR": lambda d: d["OPERATING_REVENUE"] / d["RN"],
        "AR": lambda d: d["OPERATING_REVENUE"] / d["RN"],
        "UPGRADE_PEN": lambda d: d["ROOMS_REV_UPGRADES"] / d["ROOMS_REV_ALOJAMIENTO"],
        "NON_ROOMS_REVENUE_PCT": lambda d: (d["OPERATING_REVENUE"] - d["ROOMS_REVENUE"])
        / d["OPERATING_REVENUE"],
        "ANCILLARY_REV_POR": lambda d: (d["DAY_PASS"] + d["OTHER_DEPT_REVENUE"])
        / d["RN"],
        "OTHER_REV_POR": lambda d: d["OTHER_DEPT_REVENUE"] / d["RN"],
        # 4. RENTABILIDAD FINAL (RESULTADOS)
        "GOP": lambda d: d["GOP"],
        "GOPPAR": lambda d: d["GOP"] / d["HABITACIONES"],
        "GOP_MARGIN": lambda d: d["GOP"] / d["OPERATING_REVENUE"],
        "PROFIT_POR": lambda d: d["GOP"] / d["RN"],
        # 5. DESGLOSE DEPARTAMENTAL (valores absolutos para breakdown)
        "OPERATING_REVENUE": lambda d: d["OPERATING_REVENUE"],
        "ROOMS_REVENUE": lambda d: d["ROOMS_REVENUE"],
        "ROOMS_OPEX": lambda d: d["ROOMS_OPEX"],
        "ROOMS_PERSONNEL": lambda d: d["ROOMS_PERSONNEL"],
        "ROOMS_PROFIT": lambda d: d["ROOMS_REVENUE"] - d["ROOMS_OPEX"] - d["ROOMS_PERSONNEL"],
        "ROOMS_PROFIT_MARGIN": lambda d: (d["ROOMS_REVENUE"] - d["ROOMS_OPEX"] - d["ROOMS_PERSONNEL"]) / d["ROOMS_REVENUE"],
        "FB_REVENUE": lambda d: d["FB_REVENUE"],
        "FB_OPEX": lambda d: d["FB_OPEX"],
        "FB_PERSONNEL": lambda d: d["FB_PERSONNEL"],
        "FB_PROFIT": lambda d: d["FB_PROFIT"],
        "UNDISTRIB_OPEX": lambda d: d["UNDISTRIB_OPEX"],
    }

    DEPARTMENTAL_METRICS = [
        "OPERATING_REVENUE",
        "ROOMS_REVENUE", "ROOMS_OPEX", "ROOMS_PERSONNEL", "ROOMS_PROFIT", "ROOMS_PROFIT_MARGIN",
        "FB_REVENUE", "FB_OPEX", "FB_PERSONNEL", "FB_PROFIT", "F&B_GOP_MARGIN",
        "UNDISTRIB_OPEX", "UNDISTRIB_OPEX_Pct",
        "GOP", "GOP_MARGIN",
    ]

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.df = None
        self.categories = {
            "Opex_Labor": [
                "CPOR",
                "CPH",
                "LBC",
                "LPC_TOTAL",
                "UNDISTRIB_OPEX_Pct",
                "F&B_CPOR",
                "F&B_CPH",
                "F&B_LBC",
            ],
            "Food_Beverage": [
                "Food_Cost_Pct",
                "Beverage_Cost_Pct",
                "F&B_GOP_MARGIN",
                "F&B_REVPAR",
                "F&B_GOPPAR",
                "BANQUETS_CONTRIBUTION",
                "FB_PENSION_PCT",
            ],
            "Revenue_Management": [
                "OCC",
                "ADR",
                "REVPAR",
                "TRevPAR",
                "RevPOR",
                "AR",
                "UPGRADE_PEN",
                "NON_ROOMS_REVENUE_PCT",
                "ANCILLARY_REV_POR",
                "OTHER_REV_POR",
            ],
            "Profitability": ["GOP", "GOPPAR", "GOP_MARGIN", "PROFIT_POR"],
        }
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        pnl = pd.read_sql_query("SELECT * FROM pnl", conn)
        hotels = pd.read_sql_query("SELECT * FROM hotels", conn)
        conn.close()

        df = pnl.merge(hotels, on="HOTEL", how="left")
        # Drop rows with no operations (seasonal closures / future REAL placeholders)
        df = df[df["HABITACIONES"] > 0].copy()
        self.df = df

    def _agg_real_budget(self, group_cols: list, metrics_to_calc: list) -> pd.DataFrame:
        # 1. Definir columnas base necesarias para calcular las métricas solicitadas
        base_cols = [
            "RN",
            "HABITACIONES",
            "ROOMS_REVENUE",
            "OPERATING_REVENUE",
            "GOP",
            "FB_REVENUE",
            "FB_PROFIT",
            "FOOD_COST",
            "FOOD_REVENUE",
            "BEVERAGE_COST",
            "BEVERAGE_REVENUE",
            "ROOMS_OPEX",
            "ROOMS_PERSONNEL",
            "FB_OPEX",
            "FB_PERSONNEL",
            "BANQUETS_REVENUE",
            "FB_PENSION",
            "UNDISTRIB_OPEX",
            "ROOMS_REV_UPGRADES",
            "ROOMS_REV_ALOJAMIENTO",
            "DAY_PASS",
            "OTHER_DEPT_REVENUE",
        ]

        # 2. Agrupar y Sumar totales absolutos (Ponderado Real)
        agg = self.df.groupby(group_cols + ["ESCENARIO"])[base_cols].sum().unstack()

        res = pd.DataFrame(index=agg.index)

        # 3. Motor de cálculo automático con protección contra 0
        for m in metrics_to_calc:
            if m in self.METRIC_FORMULAS:
                # Extraemos los bloques de datos
                real_data = agg.xs("REAL", level=1, axis=1)
                budget_data = agg.xs("BUDGET", level=1, axis=1)

                # Cálculo vectorizado de la métrica para REAL y BUDGET
                res[f"{m}_REAL"] = self.METRIC_FORMULAS[m](real_data)
                res[f"{m}_BUDGET"] = self.METRIC_FORMULAS[m](budget_data)

                # Variacion absoluta (manejando NaNs automáticamente)
                res[f"{m}_VAR"] = res[f"{m}_REAL"] - res[f"{m}_BUDGET"]

        return res.fillna(0).reset_index()

    def overall_kpis_annual(self) -> pd.DataFrame:
        """Retrieves all kpis by year"""
        all_kpis = [kpi for category in self.categories.values() for kpi in category]
        return self._agg_real_budget(["ANIO"], all_kpis)

    def kpis_by_hotel_annual(self) -> pd.DataFrame:
        """Retrieves all kpis by hotel by year"""
        all_kpis = [kpi for category in self.categories.values() for kpi in category]
        return self._agg_real_budget(["HOTEL", "ANIO"], all_kpis)

    def kpis_monthly(self, year: int = 2025) -> pd.DataFrame:
        """Retrieves all kpis by month for the given year"""
        df_original = self.df
        try:
            self.df = self.df[self.df["ANIO"] == year].copy()
            metrics = [
                metric for category in self.categories.values() for metric in category
            ]
            return self._agg_real_budget(["MES"], metrics)
        except Exception as e:
            print(f"Error occurred while calculating monthly KPIs for {year}: {e}")
            return pd.DataFrame()
        finally:
            self.df = df_original

    def departmental_kpis_annual(self, year: int | None = None) -> pd.DataFrame:
        """Retrieves Rooms, F&B, and Undistributed departmental revenue/opex/personnel/profit breakdown by year. Optionally filter to a specific year."""
        df_original = self.df
        try:
            if year is not None:
                self.df = self.df[self.df["ANIO"] == year].copy()
            return self._agg_real_budget(["ANIO"], self.DEPARTMENTAL_METRICS)
        finally:
            self.df = df_original

    def departmental_kpis_monthly(self, year: int = 2025) -> pd.DataFrame:
        """Retrieves Rooms, F&B, and Undistributed departmental revenue/opex/personnel/profit breakdown month by month for the given year."""
        df_original = self.df
        try:
            self.df = self.df[self.df["ANIO"] == year].copy()
            return self._agg_real_budget(["MES"], self.DEPARTMENTAL_METRICS)
        finally:
            self.df = df_original

    def format_kpi_markdown(self) -> str:
        annual = self.overall_kpis_annual()
        by_hotel = self.kpis_by_hotel_annual()
        monthly = self.kpis_monthly(year=2025)

        def auto_format(val, col_name):
            if pd.isna(val):
                return "N/A"
            name = col_name.upper()

            pct_columns = {
                "OCC_REAL",
                "LBC",
                "F&B_LBC",
                "LPC_TOTAL",
                "UNDISTRIB_OPEX_PCT",
                "FOOD_COST_PCT",
                "BEVERAGE_COST_PCT",
                "F&B_GOP_MARGIN",
                "GOP_MARGIN",
                "NON_ROOMS_REVENUE_PCT",
                "UPGRADE_PEN",
                "BANQUETS_CONTRIBUTION",
                "FB_PENSION_PCT",
            }
            pct_columns_expanded = {
                f"{base}{suf}" for base in pct_columns for suf in ["_REAL", "_BUDGET"]
            }
            pct_columns_variation = {
                f"{base}{suf}" for base in pct_columns for suf in ["_VAR"]
            }

            millions_columns = {
                "GOP",
                "OPERATING_REVENUE",
                "ROOMS_REVENUE",
                "FB_REVENUE",
                "TOTAL_DEPT_PROFIT",
                "ROOMS_PROFIT",
                "FB_PROFIT",
            }

            millions_columns_expanded = {
                f"{base}{suf}"
                for base in millions_columns
                for suf in ["_REAL", "_BUDGET", "_VAR"]
            }
            # Millions with 2 decimals
            if name in millions_columns_expanded:
                return f"${val / 1_000_000:.2f}M"
            # Percentages with 1 decimal
            if name in pct_columns_expanded:
                return f"{val * 100:.1f}%"
            if name in pct_columns_variation:
                return f"{val:.2f}"
            # Standard USD with 2 decimals
            return f"${val:.2f}"

        # Overall annual
        md = "## Overall Annual KPIs (REAL vs BUDGET)\n"
        for cat_name, metrics in self.categories.items():
            md += f"### Category: {cat_name.replace('_', ' ')}\n"
            arows = []
            for _, r in annual.iterrows():
                row = {"Year": int(r["ANIO"])}
                for m in metrics:
                    row[f"{m}_Real"] = auto_format(r.get(f"{m}_REAL"), f"{m}_REAL")
                    row[f"{m}_Bdg"] = auto_format(r.get(f"{m}_BUDGET"), f"{m}_BUDGET")
                    row[f"{m}_Var"] = auto_format(r.get(f"{m}_VAR"), f"{m}_VAR")
                arows.append(row)
            md += pd.DataFrame(arows).to_markdown(index=False) + "\n\n"

        # Monthly 2025
        md += "## Monthly KPIs 2025 (REAL vs BUDGET)\n"

        for cat_name, metrics in self.categories.items():
            md += f"### Category: {cat_name.replace('_', ' ')}\n"  #
            mrows = []
            for _, r in monthly.iterrows():
                row = {"Month": int(r["MES"])}
                for m in metrics:
                    row[f"{m}_Real"] = auto_format(r.get(f"{m}_REAL"), f"{m}_REAL")
                    row[f"{m}_Bdg"] = auto_format(r.get(f"{m}_BUDGET"), f"{m}_BUDGET")
                    row[f"{m}_Var"] = auto_format(r.get(f"{m}_VAR"), f"{m}_VAR")
                mrows.append(row)
            md += pd.DataFrame(mrows).to_markdown(index=False) + "\n\n"

        md += "## Hotel Ranking 2025 REAL (by RevPAR)\n"

        key_metrics = ["OCC", "ADR", "REVPAR", "GOP_MARGIN", "GOPPAR", "GOP"]
        real_2025 = by_hotel[by_hotel["ANIO"] == 2025].copy()
        real_2025 = real_2025.sort_values("REVPAR_REAL", ascending=False)

        h_rows = []
        for _, r in real_2025.iterrows():
            row = {"Hotel": r["HOTEL"]}
            for m in key_metrics:
                row[m] = auto_format(r.get(f"{m}_REAL"), m + "_REAL")
            h_rows.append(row)
        md += pd.DataFrame(h_rows).to_markdown(index=False) + "\n\n"

        return md

    def get_portafolio_context(self) -> str:
        """Retrieves the hotel portfolio details"""
        context_cols = [
            "HOTEL",
            "CONTINENTE",
            "PAIS",
            "CATEGORIA",
            "TOTAL_HABITACIONES",
        ]
        df_context = self.df[context_cols].drop_duplicates().sort_values("HOTEL")

        md = "## Perfil del Portafolio de Activos\n"
        md += "Este portafolio incluye los hoteles con sus características geográficas y de categoría:\n\n"
        md += df_context.to_markdown(index=False) + "\n\n"

        return md


kpi_service = KpiService(db_path=sqlite_db)

# Generar y mostrar los resultados en consola
# print(kpi_service.format_kpi_markdown())
