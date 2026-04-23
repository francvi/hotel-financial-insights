from langfuse import get_client
from langfuse.langchain import CallbackHandler
from app.config import settings
from loguru import logger

langfuse_client = None
langfuse_handler = None


if (
    settings.LANGFUSE_BASE_URL
    and settings.LANGFUSE_PUBLIC_KEY
    and settings.LANGFUSE_SECRET_KEY
):
    langfuse_client = get_client()
    logger.info("Langfuse client initialized")
    langfuse_handler = CallbackHandler()
    logger.info("Langfuse callback handler initialized")
else:
    logger.warning(
        "Langfuse not configured. Enable it adding the corresponding .env vars."
    )
