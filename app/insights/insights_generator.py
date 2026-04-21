from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import List


class InsightItem(BaseModel):
    text_en: str = Field(..., description="Insight text in English")
    text_es: str = Field(..., description="Insight text in Spanish")
    value: str = Field(..., description="Numeric or textual value associated with the insight, e.g. '-45%', '+1000 USD'")
    recommendation_en: str = Field(..., description="Actionable recommendation in English")
    recommendation_es: str = Field(..., description="Actionable recommendation in Spanish")


class LLMInsightsResponse(BaseModel):
    insights: List[InsightItem] = Field(..., description="List of structured financial insights")


LLM_MODEL = "llama3.2:latest"
llm = ChatOllama(model=LLM_MODEL)
structured_llm = llm.with_structured_output(LLMInsightsResponse)


def gen_insight(kpi_results: str) -> LLMInsightsResponse:
    response = structured_llm.invoke(
        f"""You're an expert Financial Analyst working for a Hotel Group. You'll receive KPIs results and your task is to extract valuable insights from those. Focus on the top 3 with more impact on the business.

        Provide each insight in both English and Spanish.

        [OUTPUT]

        **text_en**: 1-2 sentences describing the finding/insight in English.
        **text_es**: 1-2 sentences describing the finding/insight in Spanish.
        **value**: Key numeric value/metric of the insight. Language-agnostic. For example: "-45%", "+1000 USD", "<0.7", etc.
        **recommendation_en**: 1-2 sentences with a concrete, actionable next step in English.
        **recommendation_es**: 1-2 sentences with a concrete, actionable next step in Spanish.

        [KPIs]
        {kpi_results}
        """
    )

    return response
