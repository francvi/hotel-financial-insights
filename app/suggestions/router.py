from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from suggestions.service import load as load_suggestions
from suggestions.db import clear as clear_suggestions
from suggestions.generator import gen_followup

router = APIRouter()


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=50_000)


class FollowupRequest(BaseModel):
    history: list[HistoryItem] = Field(default=[], max_length=20)
    last_response: str = Field(max_length=50_000)
    messages: list[HistoryItem] = Field(default=[], max_length=10)


@router.get("/api/suggestions")
async def get_suggestions() -> JSONResponse:
    return JSONResponse(load_suggestions())


@router.post("/api/suggestions/followup")
async def followup_suggestions(body: FollowupRequest) -> JSONResponse:
    if body.messages:
        lines = [
            f"{'User' if t.role == 'user' else 'Assistant'}: {t.content}"
            for t in body.messages
        ]
    else:
        lines = [
            f"{'User' if t.role == 'user' else 'Assistant'}: {t.content}"
            for t in body.history
        ]
        lines.append(f"Assistant: {body.last_response}")
    result = gen_followup(conversation="\n".join(lines))
    return JSONResponse(result.model_dump())


@router.post("/api/suggestions/refresh")
async def refresh_suggestions() -> JSONResponse:
    clear_suggestions()
    return JSONResponse(load_suggestions())
