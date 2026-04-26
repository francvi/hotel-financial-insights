from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import state
from suggestions.db import clear as clear_suggestions
from suggestions.generator import gen_followup
from load_suggestions import load_suggestions

router = APIRouter()


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=50_000)


class FollowupRequest(BaseModel):
    history: list[HistoryItem] = Field(default=[], max_length=20)
    last_response: str = Field(max_length=50_000)


@router.get("/api/suggestions")
async def get_suggestions() -> JSONResponse:
    return JSONResponse(state.suggestions)


@router.post("/api/suggestions/followup")
async def followup_suggestions(body: FollowupRequest) -> JSONResponse:
    lines = []
    for turn in body.history:
        role = "User" if turn.role == "user" else "Assistant"
        lines.append(f"{role}: {turn.content}")
    lines.append(f"Assistant: {body.last_response}")
    result = gen_followup(conversation="\n".join(lines))
    return JSONResponse(result.model_dump())


@router.post("/api/suggestions/refresh")
async def refresh_suggestions() -> JSONResponse:
    clear_suggestions()
    state.suggestions = load_suggestions()
    return JSONResponse(state.suggestions)
