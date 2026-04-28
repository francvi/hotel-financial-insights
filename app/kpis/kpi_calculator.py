import sqlite3
from pathlib import Path

import pandas as pd

from db_config import DB_PATH
from integration.db.load_db import ensure_loaded

ensure_loaded()

sqlite_db = str(DB_PATH)


class KpiService:
    METRIC_FORMULAS = {
        # 1. CONTROL DE COSTES Y EFICIENCIA OPERATIVA (OPEX & LABOR)
        "CPOR": lambda d: abs(d["ROOMS_OPEX"]) / d["RN"],
        "CPH": lambda d: abs(d["ROOMS_OPEX"]) / d["HABITACIONES"],
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
        "RN": lambda d: d["RN"],
        "HABITACIONES": lambda d:d["HABITACIONES"]
    }

    DEPARTMENTAL_METRICS = [
        "OPERATING_REVENUE",
        "ROOMS_REVENUE", "ROOMS_OPEX", "ROOMS_PERSONNEL", "ROOMS_PROFIT", "ROOMS_PROFIT_MARGIN",
        "FB_REVENUE", "FB_OPEX", "FB_PERSONNEL", "FB_PROFIT", "F&B_GOP_MARGIN",
        "UNDISTRIB_OPEX", "UNDISTRIB_OPEX_Pct",
        "GOP", "GOP_MARGIN","RN","HABITACIONES"
    ]

    DEPARTMENTAL_CATEGORIES = {
        "Revenue": ["OPERATING_REVENUE", "ROOMS_REVENUE", "FB_REVENUE"],
        "Rooms": ["ROOMS_OPEX", "ROOMS_PERSONNEL", "ROOMS_PROFIT", "ROOMS_PROFIT_MARGIN"],
        "F&B": ["FB_OPEX", "FB_PERSONNEL", "FB_PROFIT", "F&B_GOP_MARGIN"],
        "Undistributed & GOP": ["UNDISTRIB_OPEX", "UNDISTRIB_OPEX_Pct", "GOP", "GOP_MARGIN"],
        "General" : ["RN", "HABITACIONES"]
    }

    # Column bases that represent ratios/percentages (0–1 scale in DB)
    PCT_BASES = frozenset({
        "OCC", "LBC", "F&B_LBC", "LPC_TOTAL", "UNDISTRIB_OPEX_PCT",
        "FOOD_COST_PCT", "BEVERAGE_COST_PCT", "F&B_GOP_MARGIN", "GOP_MARGIN",
        "NON_ROOMS_REVENUE_PCT", "UPGRADE_PEN", "BANQUETS_CONTRIBUTION",
        "FB_PENSION_PCT", "ROOMS_PROFIT_MARGIN",
    })

    # Column bases that represent large monetary amounts (shown in millions)
    MILLIONS_BASES = frozenset({
        "GOP", "OPERATING_REVENUE", "ROOMS_REVENUE", "FB_REVENUE",
        "ROOMS_PROFIT", "FB_PROFIT", "ROOMS_OPEX", "ROOMS_PERSONNEL",
        "FB_OPEX", "FB_PERSONNEL", "UNDISTRIB_OPEX",
    })

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.df = None
        self.categories = {
            "Opex_Labor": [
                "CPOR", "CPH", "LBC", "LPC_TOTAL", "UNDISTRIB_OPEX_Pct",
                "F&B_CPOR", "F&B_CPH", "F&B_LBC",
            ],
            "Food_Beverage": [
                "Food_Cost_Pct", "Beverage_Cost_Pct", "F&B_GOP_MARGIN",
                "F&B_REVPAR", "F&B_GOPPAR", "BANQUETS_CONTRIBUTION", "FB_PENSION_PCT",
            ],
            "Revenue_Management": [
                "OCC", "ADR", "REVPAR", "TRevPAR", "RevPOR", "AR",
                "UPGRADE_PEN", "NON_ROOMS_REVENUE_PCT", "ANCILLARY_REV_POR", "OTHER_REV_POR",
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
        df = df[df["HABITACIONES"] > 0].copy()
        self.df = df

    def _agg_real_budget(self, group_cols: list, metrics_to_calc: list) -> pd.DataFrame:
        base_cols = [
            "RN", "HABITACIONES", "ROOMS_REVENUE", "OPERATING_REVENUE", "GOP",
            "FB_REVENUE", "FB_PROFIT", "FOOD_COST", "FOOD_REVENUE", "BEVERAGE_COST",
            "BEVERAGE_REVENUE", "ROOMS_OPEX", "ROOMS_PERSONNEL", "FB_OPEX", "FB_PERSONNEL",
            "BANQUETS_REVENUE", "FB_PENSION", "UNDISTRIB_OPEX", "ROOMS_REV_UPGRADES",
            "ROOMS_REV_ALOJAMIENTO", "DAY_PASS", "OTHER_DEPT_REVENUE",
        ]
        agg = self.df.groupby(group_cols + ["ESCENARIO"])[base_cols].sum().unstack()
        res = pd.DataFrame(index=agg.index)
        for m in metrics_to_calc:
            if m in self.METRIC_FORMULAS:
                real_data = agg.xs("REAL", level=1, axis=1)
                budget_data = agg.xs("BUDGET", level=1, axis=1)
                res[f"{m}_REAL"] = self.METRIC_FORMULAS[m](real_data)
                res[f"{m}_BUDGET"] = self.METRIC_FORMULAS[m](budget_data)
                res[f"{m}_VAR"] = res[f"{m}_REAL"] - res[f"{m}_BUDGET"]
        return res.fillna(0).reset_index()

    @staticmethod
    def _auto_format(val: float, col_name: str) -> str:
        if pd.isna(val):
            return "N/A"
        name = col_name.upper()
        for suffix in ("_REAL", "_BUDGET", "_VAR"):
            if name.endswith(suffix):
                base = name[: -len(suffix)]
                is_var = suffix == "_VAR"
                if base in KpiService.PCT_BASES:
                    return f"{val * 100:.1f}%" if not is_var else f"{val:+.2f}pp"
                if base in KpiService.MILLIONS_BASES:
                    return f"${val / 1_000_000:.2f}M"
                
                break
        return f"${val:.2f}"

    def _df_to_markdown(
        self,
        df: pd.DataFrame,
        group_cols: list[str],
        categories: dict[str, list[str]],
    ) -> str:
        sections = []
        for cat_name, metrics in categories.items():
            rows = []
            for _, r in df.iterrows():
                row = {}
                for col in group_cols:
                    row[col] = int(r[col]) if col in ("ANIO", "MES") else r[col]
                for m in metrics:
                    if f"{m}_REAL" in r.index:
                        row[f"{m} Real"] = self._auto_format(r[f"{m}_REAL"], f"{m}_REAL")
                        row[f"{m} Bdg"]  = self._auto_format(r[f"{m}_BUDGET"], f"{m}_BUDGET")
                        row[f"{m} Var"]  = self._auto_format(r[f"{m}_VAR"], f"{m}_VAR")
                rows.append(row)
            table = pd.DataFrame(rows).to_markdown(index=False)
            sections.append(f"### {cat_name.replace('_', ' ')}\n{table}")
        return "\n\n".join(sections)

    def overall_kpis_annual(self) -> str:
        """[GLOBAL PORTFOLIO] Retrieves consolidated KPIs aggregated across the entire hotel chain, grouped ONLY by year (REAL vs BUDGET). DOES NOT breakdown by individual hotel."""
        all_kpis = [kpi for cat in self.categories.values() for kpi in cat]
        df = self._agg_real_budget(["ANIO"], all_kpis)
        return "## Annual KPIs — All Hotels Combined\n\n" + self._df_to_markdown(df, ["ANIO"], self.categories)

    def kpis_by_hotel_annual(self) -> str:
        """[INDIVIDUAL LEVEL] Retrieves KPIs broken down specifically BY EACH HOTEL and by year (REAL vs BUDGET). Useful for analyzing individual property performance."""
        all_kpis = [kpi for cat in self.categories.values() for kpi in cat]
        df = self._agg_real_budget(["HOTEL", "ANIO"], all_kpis)
        return "## Annual KPIs by Hotel\n\n" + self._df_to_markdown(df, ["HOTEL", "ANIO"], self.categories)
    
    def kpis_by_hotel_period(self,
                              hotels: list[str] | str | None = None, 
                              years: list[int] | int | None = None, 
                              category: str | None = None,
                              metrics: list[str] | str | None = None) -> str:
        """
        [INDIVIDUAL LEVEL] Retrieves monthly KPIs by hotel.
        Args:
            hotels: Name or list of hotel names.
            years: Year or list of years.
            category: 'Opex_Labor', 'Food_Beverage', 'Revenue_Management', 'Profitability', 'Revenue', 'Rooms', 'F&B', 'Undistributed & GOP', 'General'.
            metrics: Specific list of metrics (e.g., ['OCC', 'ADR', 'GOP']). Use this if specific KPIs are requested.
        """
        df_original = self.df
        try:
            if isinstance(hotels, str):
                hotels = [hotels]
            if isinstance(years, int):
                years = [years]
            if isinstance(metrics, str): 
                metrics = [metrics]
            if hotels:
                hotels_upper = [h.upper() for h in hotels]
                self.df = self.df[self.df["HOTEL"].str.upper().isin(hotels_upper)]
            if years:
                self.df = self.df[self.df["ANIO"].isin(years)]
            if self.df.empty:
                return "No data found for the requested hotels/years."

            #Select Category of metric
            target_metrics = self.DEPARTMENTAL_METRICS
            target_categories = self.DEPARTMENTAL_CATEGORIES
            scope_name = "Departmental Summary"
         
            if metrics:
                #Filter specific metrics
                target_metrics = [m for m in metrics if m in self.METRIC_FORMULAS]
                if target_metrics:
                    target_categories = {"Custom Metrics": target_metrics}
                    scope_name = "Custom Selection"

            elif category:
                if category in self.categories:
                    target_metrics = self.categories[category]
                    target_categories = {category: target_metrics}
                    scope_name = category
                elif category in self.DEPARTMENTAL_CATEGORIES:
                    target_metrics = self.DEPARTMENTAL_CATEGORIES[category]
                    target_categories = {category: target_metrics}
                    scope_name = category
                elif category in self.METRIC_FORMULAS:
                    target_metrics = [category]
                    target_categories = {"Custom Metrics": target_metrics}
                    scope_name = category

            if not target_metrics:
                 return "Error: No valid metrics found to calculate."

            df = self._agg_real_budget(["HOTEL", "ANIO", "MES"], target_metrics)
            title_scope = ", ".join(hotels) if hotels else "All Hotels"
            
            return f"## Historical Monthly KPIs: {title_scope} - {scope_name}\n\n" + \
                   self._df_to_markdown(df, ["HOTEL", "ANIO", "MES"], target_categories)
                   
        finally:
            self.df = df_original

    def kpis_monthly(self, year: int = 2025) -> str:
        """[GLOBAL PORTFOLIO] Retrieves consolidated KPIs for the entire chain, grouped ONLY by month for a specific year (REAL vs BUDGET). DOES NOT breakdown by individual hotel."""
        df_original = self.df
        try:
            self.df = self.df[self.df["ANIO"] == year].copy()
            all_kpis = [kpi for cat in self.categories.values() for kpi in cat]
            df = self._agg_real_budget(["MES"], all_kpis)
            return f"## Monthly KPIs {year}\n\n" + self._df_to_markdown(df, ["MES"], self.categories)
        except Exception as e:
            return f"Error retrieving monthly KPIs for {year}: {e}"
        finally:
            self.df = df_original

    def departmental_kpis_annual(self, year: int | None = None) -> str:
        """[GLOBAL PORTFOLIO] Retrieves Rooms, F&B, and Undistributed departmental revenue/opex/personnel/profit breakdown by year (REAL vs BUDGET). Optionally filter to a specific year."""
        df_original = self.df
        try:
            if year is not None:
                self.df = self.df[self.df["ANIO"] == year].copy()
            df = self._agg_real_budget(["ANIO"], self.DEPARTMENTAL_METRICS)
            title = f"## Departmental KPIs — {year if year else 'All Years'}\n\n"
            return title + self._df_to_markdown(df, ["ANIO"], self.DEPARTMENTAL_CATEGORIES)
        finally:
            self.df = df_original

    def departmental_kpis_monthly(self, year: int = 2025) -> str:
        """Retrieves Rooms, F&B, and Undistributed departmental revenue/opex/personnel/profit breakdown month by month for the given year (REAL vs BUDGET)."""
        df_original = self.df
        try:
            self.df = self.df[self.df["ANIO"] == year].copy()
            df = self._agg_real_budget(["MES"], self.DEPARTMENTAL_METRICS)
            return f"## Monthly Departmental KPIs {year}\n\n" + self._df_to_markdown(df, ["MES"], self.DEPARTMENTAL_CATEGORIES)
        finally:
            self.df = df_original

    def format_kpi_markdown(self) -> str:
        all_kpis = [kpi for cat in self.categories.values() for kpi in cat]

        annual = self._agg_real_budget(["ANIO"], all_kpis)

        df_orig = self.df
        self.df = self.df[self.df["ANIO"] == 2025].copy()
        monthly = self._agg_real_budget(["MES"], all_kpis)
        self.df = df_orig

        by_hotel = self._agg_real_budget(["HOTEL", "ANIO"], all_kpis)

        md = "## Overall Annual KPIs (REAL vs BUDGET)\n"
        for cat_name, metrics in self.categories.items():
            md += f"### Category: {cat_name.replace('_', ' ')}\n"
            rows = []
            for _, r in annual.iterrows():
                row = {"Year": int(r["ANIO"])}
                for m in metrics:
                    row[f"{m}_Real"] = self._auto_format(r.get(f"{m}_REAL"), f"{m}_REAL")
                    row[f"{m}_Bdg"]  = self._auto_format(r.get(f"{m}_BUDGET"), f"{m}_BUDGET")
                    row[f"{m}_Var"]  = self._auto_format(r.get(f"{m}_VAR"), f"{m}_VAR")
                rows.append(row)
            md += pd.DataFrame(rows).to_markdown(index=False) + "\n\n"

        md += "## Monthly KPIs 2025 (REAL vs BUDGET)\n"
        for cat_name, metrics in self.categories.items():
            md += f"### Category: {cat_name.replace('_', ' ')}\n"
            rows = []
            for _, r in monthly.iterrows():
                row = {"Month": int(r["MES"])}
                for m in metrics:
                    row[f"{m}_Real"] = self._auto_format(r.get(f"{m}_REAL"), f"{m}_REAL")
                    row[f"{m}_Bdg"]  = self._auto_format(r.get(f"{m}_BUDGET"), f"{m}_BUDGET")
                    row[f"{m}_Var"]  = self._auto_format(r.get(f"{m}_VAR"), f"{m}_VAR")
                rows.append(row)
            md += pd.DataFrame(rows).to_markdown(index=False) + "\n\n"

        md += "## Hotel Ranking 2025 REAL (by RevPAR)\n"
        key_metrics = ["OCC", "ADR", "REVPAR", "GOP_MARGIN", "GOPPAR", "GOP"]
        real_2025 = by_hotel[by_hotel["ANIO"] == 2025].copy()
        real_2025 = real_2025.sort_values("REVPAR_REAL", ascending=False)
        rows = []
        for _, r in real_2025.iterrows():
            row = {"Hotel": r["HOTEL"]}
            for m in key_metrics:
                row[m] = self._auto_format(r.get(f"{m}_REAL"), f"{m}_REAL")
            rows.append(row)
        md += pd.DataFrame(rows).to_markdown(index=False) + "\n\n"

        return md

    def get_portafolio_context(self) -> str:
        """Retrieves the hotel portfolio details"""
        context_cols = ["HOTEL", "CONTINENTE", "PAIS", "CATEGORIA", "TOTAL_HABITACIONES","MESES_OPEN","PERIOD_CLOSE"]
        df_context = self.df[context_cols].drop_duplicates().sort_values("HOTEL")
        md = "## Perfil del Portafolio de Activos\n"
        md += "Este portafolio incluye los hoteles con sus características geográficas y de categoría:\n\n"
        md += df_context.to_markdown(index=False) + "\n\n"
        return md


kpi_service = KpiService(db_path=sqlite_db)
