import sqlite3

from pydantic import ValidationError

from insights.db import DB_PATH, clear_rows, init_db, read_from_db, write_to_db
from insights.insights_generator import LLMInsightsResponse, gen_insight
from kpis.kpi_calculator import kpi_service


def load_insights() -> dict:
    init_db()

    try:
        raw = read_from_db()
        if raw is not None:
            LLMInsightsResponse.model_validate(raw)
            return raw
    except ValidationError:
        clear_rows()
    except sqlite3.Error:
        DB_PATH.unlink(missing_ok=True)
        init_db()

    kpis_data = kpi_service.format_kpi_markdown()
    data = gen_insight(kpi_results=kpis_data)
    write_to_db(data)
    return data.model_dump()
