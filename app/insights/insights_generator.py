from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import List


class InsightItem(BaseModel):
    text: str = Field(..., description="Human-readable insight text")
    value: str = Field(
        ..., description="Numeric or textual value associated with the insight"
    )
    recommendation: str = Field(
        ..., description="1-2 sentence actionable next step tied to this specific insight"
    )


class LLMInsightsResponse(BaseModel):
    insights: List[InsightItem] = Field(
        ..., description="List of structured financial insights"
    )


LLM_MODEL = "llama3.2:latest"
llm = ChatOllama(model=LLM_MODEL)
structured_llm = llm.with_structured_output(LLMInsightsResponse)


def gen_insight(kpi_results: str) -> LLMInsightsResponse:
    response = structured_llm.invoke(
        f"""You're an expert Financial Analyst working for a Hotel Group. You'll receive KPIs results and your task is to extract valuable insights from those. Focus on the top 3 with more impact on the business.

        [OUTPUT]

        **text**: 1-2 sentences describing the finding/insight.
        **value**: Key numeric value/metric of the insight. For example: "-45%", "+1000 USD", "<0.7", etc.
        **recommendation**: 1-2 sentences describing a concrete, actionable next step the hotel management should take based on this specific insight.

        [KPIs]
        {kpi_results}
        """
    )

    return response
