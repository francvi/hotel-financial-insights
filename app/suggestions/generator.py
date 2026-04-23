from typing import List

from pydantic import BaseModel, Field

from app.config import settings

from integration.langfuse import langfuse_handler, langfuse_client


llm = None

if settings.INSIGHTS_LLM_PROVIDER == "ollama":
    from app.integration.ollama import init_chat_llm

    llm = init_chat_llm(model="llama3.2:latest", temperature=0.7)

if settings.INSIGHTS_LLM_PROVIDER == "openai":
    from app.integration.openai import init_chat_llm

    llm = init_chat_llm(model="gpt-4.1", temperature=0.7)


class SuggestionItem(BaseModel):
    text_en: str = Field(..., description="Question in English")
    text_es: str = Field(..., description="Question in Spanish")


class LLMSuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem] = Field(
        ..., description="List of suggested questions for the user"
    )


structured_llm = llm.with_structured_output(LLMSuggestionsResponse)


def gen_followup(conversation: str) -> LLMSuggestionsResponse:
    return structured_llm.invoke(
        f"""You are a hotel financial analyst assistant. Given the conversation below, generate exactly 3 short follow-up questions the user might naturally ask next.

Rules:
- Questions must be directly relevant to what was just discussed
- Each question should be concise (max 10 words in English)
- Do not repeat questions already asked in the conversation
- Provide each question in both English and Spanish

[CONVERSATION]
{conversation}
""",
        config={
            "callbacks": [langfuse_handler] if langfuse_handler else [],
            "metadata": {"source": "suggestions_engine"},
        },
    )


def gen_suggestions(kpi_results: str) -> LLMSuggestionsResponse:
    return structured_llm.invoke(
        f"""You are a hotel financial analyst assistant. Given the KPI data below, generate exactly 6 specific, insightful questions a hotel group manager would want to ask.

Rules:
- Questions must be grounded in the actual data (reference specific hotels, months, or metrics that stand out)
- Cover a mix of: occupancy, ADR, RevPAR, GOP margin, budget variance, and trends
- Each question should be concise (max 10 words in English)
- Provide each question in both English and Spanish

[KPI DATA]
{kpi_results}
"""
    )
