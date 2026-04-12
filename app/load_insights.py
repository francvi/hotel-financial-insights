import json
from pathlib import Path

from insights.insights_generator import gen_insight
from kpis.kpi_calculator import kpi_service

# Always read and write the same file so the cache is reused across restarts
_CACHE = Path(__file__).parent / "insights.json"


def load_insights() -> dict:
    if _CACHE.exists():
        with open(_CACHE) as f:
            return json.load(f)

    kpis_data = kpi_service.format_occupancy_markdown()
    data = gen_insight(kpi_results=kpis_data)

    with open(_CACHE, "w", encoding="utf-8") as f:
        f.write(data.model_dump_json())

    return data.model_dump()
