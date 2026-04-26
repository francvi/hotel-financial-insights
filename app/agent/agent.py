from langchain.agents import create_agent
from app.config import settings
from app.integration.ollama import init_chat_llm
from app.kpis import kpi_service

from .system_prompt import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT

llm = None

if settings.CHATBOT_LLM_PROVIDER == "ollama":
    from app.integration.ollama import init_chat_llm

    llm = init_chat_llm(model="llama3.2:latest", temperature=0.1)

if settings.CHATBOT_LLM_PROVIDER == "openai":
    from app.integration.openai import init_chat_llm

    llm = init_chat_llm(model="gpt-4.1", temperature=0.1)


def build_agent(tools=None, system_prompt=None):
    return create_agent(
        model=llm,
        tools=tools
        or [
            kpi_service.overall_kpis_annual,
            kpi_service.kpis_by_hotel_annual,
            kpi_service.kpis_monthly,
            kpi_service.get_portafolio_context,
        ],
        system_prompt=system_prompt or _BASE_SYSTEM_PROMPT,
    )


def build_agent_with_context(insights: dict):
    context_lines = "\n".join(
        f"- {item['text_en']}: {item['value']}" for item in insights.get("insights", [])
    )
    system_prompt = f"{_BASE_SYSTEM_PROMPT}\n\n## Live KPI Snapshot\n{context_lines}"
    return build_agent(system_prompt=system_prompt)
