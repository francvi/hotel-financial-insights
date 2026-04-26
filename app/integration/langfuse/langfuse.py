from dotenv import load_dotenv

load_dotenv()

from langfuse.langchain import CallbackHandler
from app.config import settings
from loguru import logger

langfuse_handler = None


if (
    settings.LANGFUSE_BASE_URL
    and settings.LANGFUSE_PUBLIC_KEY
    and settings.LANGFUSE_SECRET_KEY
):
    langfuse_handler = CallbackHandler()
    logger.info("Langfuse callback handler initialized")
else:
    logger.warning(
        "Langfuse not configured. Enable it adding the corresponding .env vars."
    )
