import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)

logger.add(
    LOG_DIR / "agent.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
    colorize=False,
)


def divider(label: str = "", width: int = 56) -> str:
    if label:
        pad = max(0, width - len(label) - 3)
        return f"┌─ {label} {'─' * pad}"
    return "└" + "─" * width


def log_block(lines: list[str], *, level: str = "INFO") -> None:
    """Log each line prefixed with │  at the given level."""
    emit = getattr(logger, level.lower())
    for line in lines:
        emit(f"│  {line}")
