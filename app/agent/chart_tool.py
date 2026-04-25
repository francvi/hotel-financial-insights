import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool
from app.kpis import kpi_service

@tool
def generate_time_series_chart(kpi_name: str, year: int = 2025) -> str:
    """
    Generates a time series chart for a given KPI comparing REAL vs BUDGET data over the months of a given year.
    Returns a Markdown string with the base64 encoded image.
    Use this tool when the user asks to draw or display a chart/graph of a KPI's evolution or time series.
    """
    try:
        # Get the monthly data for the specified year
        monthly_data = kpi_service.kpis_monthly(year=year)
        
        if monthly_data.empty:
            return f"No data found for the year {year}."

        # The data columns should have `{kpi_name}_REAL` and `{kpi_name}_BUDGET`
        # However, kpi_name could be passed differently. Let's make it robust by making it uppercase.
        kpi_name = kpi_name.upper()
        real_col = f"{kpi_name}_REAL"
        budget_col = f"{kpi_name}_BUDGET"

        if real_col not in monthly_data.columns or budget_col not in monthly_data.columns:
            available_kpis = [col.replace('_REAL', '') for col in monthly_data.columns if col.endswith('_REAL')]
            return f"Error: KPI '{kpi_name}' not found. Available KPIs: {', '.join(available_kpis)}"

        # Sort by month to ensure correct chronological plotting
        if 'MES' in monthly_data.columns:
            monthly_data = monthly_data.sort_values(by='MES')
            months = monthly_data['MES'].tolist()
        else:
            months = list(range(1, len(monthly_data) + 1))

        real_values = monthly_data[real_col].tolist()
        budget_values = monthly_data[budget_col].tolist()

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(months, real_values, label=f'{kpi_name} REAL', marker='o', color='#6366F1', linewidth=2)
        plt.plot(months, budget_values, label=f'{kpi_name} BUDGET', marker='x', color='#94A3B8', linestyle='--', linewidth=2)

        plt.title(f'Monthly Evolution: {kpi_name} ({year})', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel(kpi_name, fontsize=12)
        
        # Use month names or numbers for X-axis
        plt.xticks(months, [f'M{m}' for m in months])
        
        plt.legend(loc='best', frameon=True, shadow=True)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()

        # Create charts directory if it doesn't exist
        import os
        import time
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        charts_dir = os.path.join(static_dir, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Generate a unique filename
        filename = f"chart_{kpi_name}_{year}_{int(time.time())}.png"
        filepath = os.path.join(charts_dir, filename)

        # Save plot to file
        plt.savefig(filepath, format='png', dpi=100)
        
        # Close the plot to free memory
        plt.close()

        # Return Markdown syntax pointing to the static file
        # FastAPI mounts static at /
        markdown_image = f"![Time Series Chart - {kpi_name}](/charts/{filename})\n\n"
        markdown_image += f"*Here is the chart for {kpi_name} comparing REAL and BUDGET for the year {year}.*"
        
        return markdown_image

    except Exception as e:
        return f"An error occurred while generating the chart: {str(e)}"
