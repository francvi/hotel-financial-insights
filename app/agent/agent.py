from langchain.agents import create_agent
from app.config import settings
from app.kpis import kpi_service

from .system_prompt import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from app.integration.openai import init_chat_llm

llm = init_chat_llm(model="gpt-5.4-mini", temperature=0.1)


def build_agent(tools=None, system_prompt=None):
    return create_agent(
        model=llm,
        tools=tools
        or [
            kpi_service.overall_kpis_annual,
            kpi_service.kpis_by_hotel_annual,
            kpi_service.kpis_monthly,
            kpi_service.kpis_by_hotel_period,
            kpi_service.departmental_kpis_annual,
            kpi_service.departmental_kpis_monthly,
            kpi_service.get_portafolio_context,
           
        ],
        system_prompt=system_prompt or _BASE_SYSTEM_PROMPT,
    )


def build_agent_with_context(insights: dict):
    from loguru import logger
    from logging_config import divider, log_block

    items = insights.get("insights", [])
    context_lines = "\n".join(f"- {i['text_en']}: {i['value']}" for i in items)
    system_prompt = f"{_BASE_SYSTEM_PROMPT}\n\n## Latest Insights:\n{context_lines}"

    logger.info(
        divider(
            f"AGENT INITIALIZED  {len(system_prompt):,} chars | {len(items)} insight(s)"
        )
    )
    logger.debug(divider("SYSTEM PROMPT"))
    log_block(system_prompt.splitlines(), level="DEBUG")
    logger.debug(divider())

    return build_agent(system_prompt=system_prompt)
