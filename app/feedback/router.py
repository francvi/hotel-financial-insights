import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from feedback.db import save_feedback

router = APIRouter()


class ConversationTurn(BaseModel):
    role: str
    content: str = Field(max_length=50_000)


class FeedbackRequest(BaseModel):
    message_id: str = Field(max_length=100)
    rating: int = Field(..., description="1 = thumbs up, -1 = thumbs down")
    comment: str | None = Field(default=None, max_length=2000)
    message_content: str | None = Field(default=None, max_length=50_000)
    conversation: list[ConversationTurn] = Field(default=[], max_length=10)


@router.post("/api/feedback")
async def submit_feedback(body: FeedbackRequest) -> JSONResponse:
    if body.rating not in (1, -1):
        raise HTTPException(status_code=422, detail="rating must be 1 or -1")
    conversation_json = json.dumps([t.model_dump() for t in body.conversation]) if body.conversation else None
    row_id = save_feedback(
        body.message_id,
        body.rating,
        body.comment,
        body.message_content,
        conversation_json,
    )
    return JSONResponse({"id": row_id})
