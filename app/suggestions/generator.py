from typing import List

from pydantic import BaseModel, Field

from integration.langfuse import langfuse_handler
from integration.openai import init_chat_llm


llm = init_chat_llm(model="gpt-5.4-nano", temperature=0.7)


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
- Questions must be directly relevant to the specific hotels, metrics, and periods discussed
- Build on what was already covered — probe deeper, compare further, or explore adjacent angles
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
""",
        config={
            "callbacks": [langfuse_handler] if langfuse_handler else [],
            "metadata": {"source": "suggestions_engine"},
        },
    )
