from pydantic import BaseModel, Field
from typing import List
from app.config import settings

from integration.langfuse import langfuse_handler, langfuse_client


llm = None

if settings.INSIGHTS_LLM_PROVIDER == "ollama":
    from app.integration.ollama import init_chat_llm

    llm = init_chat_llm(model="llama3.2:latest", temperature=0.1)

if settings.INSIGHTS_LLM_PROVIDER == "openai":
    from app.integration.openai import init_chat_llm

    llm = init_chat_llm(model="gpt-4.1", temperature=0.1)


class InsightItem(BaseModel):
    text_en: str = Field(..., description="Insight text in English")
    text_es: str = Field(..., description="Insight text in Spanish")
    value: str = Field(
        ...,
        description="Numeric or textual value associated with the insight, e.g. '-45%', '+1000 USD'",
    )
    recommendation_en: str = Field(
        ..., description="Actionable recommendation in English"
    )
    recommendation_es: str = Field(
        ..., description="Actionable recommendation in Spanish"
    )


class LLMInsightsResponse(BaseModel):
    insights: List[InsightItem] = Field(
        ..., description="List of structured financial insights"
    )


structured_llm = llm.with_structured_output(LLMInsightsResponse)


def gen_insight(kpi_results: str, portfolio_context: str) -> LLMInsightsResponse:
    response = structured_llm.invoke(
        f"""You're an expert Financial Analyst working for a Hotel Group. You'll receive KPIs results and your task is to extract valuable insights from those. Focus on the top 3 with more impact on the business.

        Provide each insight in both English and Spanish.

        [OUTPUT]

        **text_en**: 1-2 sentences describing the finding/insight in English. Include clear references to the analysed period (month, year) if apply.
        **text_es**: 1-2 sentences describing the finding/insight in Spanish. Include clear references to the analysed period (month, year) if apply.
        **value**: Key numeric value/metric of the insight. Language-agnostic. For example: "-45%", "+1000 USD", "<0.7", etc.
        **recommendation_en**: 1-2 sentences with a concrete, actionable next step in English.
        **recommendation_es**: 1-2 sentences with a concrete, actionable next step in Spanish.

        [KPIs]
        {kpi_results}
        """,
        config={
            "callbacks": [langfuse_handler] if langfuse_handler else [],
            "metadata": {"source": "insights_engine"},
        },
    )

    return response
