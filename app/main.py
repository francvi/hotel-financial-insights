from app.insights.insights_generator import gen_insight
from app.kpis.kpi_calculator import kpi_service

kpis_data = kpi_service.format_occupancy_markdown()
print(f"KPIs \n\n{kpis_data}")
insights = gen_insight(kpi_results=kpis_data)

print(insights.model_dump_json())

with open("app/static/insights.json", "w", encoding="utf-8") as f:
    f.write(insights.model_dump_json())
