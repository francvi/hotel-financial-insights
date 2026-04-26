import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str = "hotel_financial_insights.db"
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    LANGFUSE_SECRET_KEY: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_BASE_URL: str | None = os.getenv("LANGFUSE_BASE_URL")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
