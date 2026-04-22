from suggestions.db import clear, init_db, read_from_db, write_to_db
from suggestions.generator import gen_suggestions
from kpis.kpi_calculator import kpi_service


def load_suggestions() -> dict:
    init_db()

    cached = read_from_db()
    if cached is not None:
        return cached

    kpis_data = kpi_service.format_kpi_markdown()
    data = gen_suggestions(kpi_results=kpis_data)
    write_to_db(data)
    return data.model_dump()
