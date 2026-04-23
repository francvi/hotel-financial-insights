import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME", "hotel_kpi.db")
    CHATBOT_LLM_PROVIDER: str = os.getenv("CHATBOT_LLM_PROVIDER", "ollama")
    INSIGHTS_LLM_PROVIDER: str = os.getenv("INSIGHTS_LLM_PROVIDER", "ollama")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    LANGFUSE_SECRET_KEY: str | None = os.getenv(
        "LANGFUSE_SECRET_KEY",
    )
    LANGFUSE_PUBLIC_KEY: str | None = os.getenv(
        "LANGFUSE_PUBLIC_KEY",
    )
    LANGFUSE_BASE_URL: str | None = os.getenv(
        "LANGFUSE_BASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
