from fastapi import APIRouter
from fastapi.responses import JSONResponse

import state
from agent.agent import build_agent_with_context
from insights.db import clear_rows
from load_insights import load_insights
from suggestions.db import clear as clear_suggestions
from load_suggestions import load_suggestions

router = APIRouter()


@router.get("/api/insights")
async def get_insights() -> JSONResponse:
    return JSONResponse(state.insights)


@router.post("/api/insights/refresh")
async def refresh_insights() -> JSONResponse:
    clear_rows()
    clear_suggestions()
    state.insights = load_insights()
    state.suggestions = load_suggestions()
    state.agent = build_agent_with_context(state.insights)
    return JSONResponse(state.insights)
