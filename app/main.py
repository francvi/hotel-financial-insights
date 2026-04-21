"""
FastAPI server — Hotel Financial Insights
Run from project root: uvicorn app.server:app --reload
"""

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# Add app/ to sys.path so existing internal imports (load_insights, agent.system_prompt, etc.) work
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import build_agent  # noqa: E402
from agent.system_prompt import SYSTEM_PROMPT  # noqa: E402
from insights.db import clear_rows  # noqa: E402
from load_insights import load_insights  # noqa: E402

_insights: dict = {}
_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _insights, _agent
    _insights = load_insights()
    _agent = _build_agent_with_context(_insights)
    yield


app = FastAPI(lifespan=lifespan)


# ── API ────────────────────────────────────────────────────────────────────


def _build_agent_with_context(insights: dict):
    context_lines = "\n".join(
        f"- {item['text']}: {item['value']}" for item in insights.get("insights", [])
    )
    return build_agent(
        system_prompt=f"{SYSTEM_PROMPT}\n\n## Live KPI Snapshot\n{context_lines}"
    )


@app.get("/api/insights")
async def get_insights() -> JSONResponse:
    return JSONResponse(_insights)


@app.post("/api/insights/refresh")
async def refresh_insights() -> JSONResponse:
    global _insights, _agent
    clear_rows()
    _insights = load_insights()
    _agent = _build_agent_with_context(_insights)
    return JSONResponse(_insights)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    history: list[HistoryItem] = Field(default=[], max_length=20)


@app.post("/api/chat")
async def chat(body: ChatRequest) -> EventSourceResponse:
    messages = []
    for turn in body.history:
        cls = HumanMessage if turn.role == "user" else AIMessage
        messages.append(cls(content=turn.content))
    messages.append(HumanMessage(content=body.message))

    async def token_stream():
        async for token, _metadata in _agent.astream(
            {"messages": messages}, stream_mode="messages"
        ):
            blocks = getattr(token, "content_blocks", None)
            if blocks:
                yield {"data": json.dumps(blocks)}

    return EventSourceResponse(token_stream())


# ── Static files — must be mounted last so API routes take precedence ──────
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="static",
)
