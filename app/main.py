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

import state  # noqa: E402
from agent.agent import build_agent_with_context  # noqa: E402
from agent.router import router as agent_router  # noqa: E402
from feedback.db import init_db as init_feedback_db  # noqa: E402
from feedback.router import router as feedback_router  # noqa: E402
from insights.router import router as insights_router  # noqa: E402
from load_insights import load_insights  # noqa: E402
from load_suggestions import load_suggestions  # noqa: E402
from suggestions.router import router as suggestions_router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_feedback_db()
    state.insights = load_insights()
    state.suggestions = load_suggestions()
    state.agent = build_agent_with_context(state.insights)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(feedback_router)

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
