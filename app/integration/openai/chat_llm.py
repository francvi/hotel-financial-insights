from langchain_openai import ChatOpenAI
from app.config import settings


def init_chat_llm(model: str = "gpt-5.4-mini", temperature: float = 0.0) -> ChatOpenAI:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")
    llm = ChatOpenAI(
        model=model, temperature=temperature, api_key=settings.OPENAI_API_KEY
    )

    return llm
