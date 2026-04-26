from pathlib import Path

from config.settings import settings

DB_PATH = Path(__file__).parent.parent / settings.DB_NAME
