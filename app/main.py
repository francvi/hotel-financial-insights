"""
FastAPI server — Hotel Financial Insights
Run from project root: uvicorn app.server:app --reload
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Add app/ to sys.path so internal imports work
sys.path.insert(0, str(Path(__file__).parent))

import logging_config  # noqa: F401, E402  — side-effect import: sets up loguru handlers
from agent.router import router as agent_router  # noqa: E402
from feedback.router import router as feedback_router  # noqa: E402
from insights.router import router as insights_router  # noqa: E402
from insights.service import load as load_insights  # noqa: E402
from suggestions.router import router as suggestions_router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_insights()  # warm up: generate insights if DB is empty
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(agent_router)
app.include_router(insights_router)
app.include_router(suggestions_router)
app.include_router(feedback_router)

# Must be mounted last so API routes take precedence
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="static",
)
