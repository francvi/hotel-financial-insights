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
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# Add app/ to sys.path so existing internal imports (load_insights, agent.system_prompt, etc.) work
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import build_agent  # noqa: E402
from agent.system_prompt import SYSTEM_PROMPT  # noqa: E402
from insights.db import clear_rows  # noqa: E402
from suggestions.db import clear as clear_suggestions  # noqa: E402
from suggestions.generator import gen_followup  # noqa: E402
from load_insights import load_insights  # noqa: E402
from load_suggestions import load_suggestions  # noqa: E402
from integration.langfuse import langfuse_handler, langfuse_client
from feedback.db import init_db as init_feedback_db  # noqa: E402
from feedback.router import router as feedback_router  # noqa: E402

_insights: dict = {}
_suggestions: dict = {}
_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _insights, _suggestions, _agent
    init_feedback_db()
    _insights = load_insights()
    _suggestions = load_suggestions()
    _agent = _build_agent_with_context(_insights)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(feedback_router)


# ── API ────────────────────────────────────────────────────────────────────


def _build_agent_with_context(insights: dict):

    context_lines = "\n".join(
        f"- {item['text_en']}: {item['value']}" for item in insights.get("insights", [])
    )
    system_prompt = f"{SYSTEM_PROMPT}\n\n## Live KPI Snapshot\n{context_lines}"

    return build_agent(
        system_prompt=system_prompt,
    )


@app.get("/api/insights")
async def get_insights() -> JSONResponse:
    return JSONResponse(_insights)


@app.get("/api/suggestions")
async def get_suggestions() -> JSONResponse:
    return JSONResponse(_suggestions)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=50_000)


LANG_SYSTEM: dict[str, str] = {
    "en": "Respond entirely in English.",
    "es": "Responde completamente en español.",
}


class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    history: list[HistoryItem] = Field(default=[], max_length=20)
    language: str = "en"


@app.post("/api/chat")
async def chat(body: ChatRequest) -> EventSourceResponse:
    lang_msg = SystemMessage(content=LANG_SYSTEM.get(body.language, LANG_SYSTEM["en"]))
    messages = [lang_msg]
    for turn in body.history:
        cls = HumanMessage if turn.role == "user" else AIMessage
        messages.append(cls(content=turn.content))
    messages.append(HumanMessage(content=body.message))

    async def token_stream():
        seen_tool_calls: set[str] = set()
        async for token, _metadata in _agent.astream(
            {"messages": messages},
            stream_mode="messages",
            config={
                "callbacks": [langfuse_handler] if langfuse_handler else [],
                "metadata": {"source": "chat_engine"},
            },
        ):
            if isinstance(token, ToolMessage):
                continue

            tool_call_chunks = getattr(token, "tool_call_chunks", [])
            for chunk in tool_call_chunks:
                call_id = chunk.get("id") or str(chunk.get("index", 0))
                name = chunk.get("name", "")
                if name and call_id not in seen_tool_calls:
                    seen_tool_calls.add(call_id)
                    yield {"data": json.dumps([{"type": "tool_use", "name": name}])}
            if tool_call_chunks:
                continue

            blocks = getattr(token, "content_blocks", None)
            if blocks:
                text_blocks = [
                    b for b in blocks if isinstance(b, dict) and b.get("type") == "text"
                ]
                if text_blocks:
                    yield {"data": json.dumps(text_blocks)}
            elif isinstance(getattr(token, "content", None), str) and token.content:
                yield {"data": json.dumps([{"type": "text", "text": token.content}])}

    return EventSourceResponse(token_stream())


class FollowupRequest(BaseModel):
    history: list[HistoryItem] = Field(default=[], max_length=20)
    last_response: str = Field(max_length=50_000)


@app.post("/api/suggestions/followup")
async def followup_suggestions(body: FollowupRequest) -> JSONResponse:
    lines = []
    for turn in body.history:
        role = "User" if turn.role == "user" else "Assistant"
        lines.append(f"{role}: {turn.content}")
    lines.append(f"Assistant: {body.last_response}")
    conversation = "\n".join(lines)
    result = gen_followup(conversation=conversation)
    return JSONResponse(result.model_dump())


@app.post("/api/suggestions/refresh")
async def refresh_suggestions() -> JSONResponse:
    global _suggestions
    clear_suggestions()
    _suggestions = load_suggestions()
    return JSONResponse(_suggestions)


@app.post("/api/insights/refresh")
async def refresh_insights() -> JSONResponse:
    global _insights, _suggestions, _agent
    clear_rows()
    clear_suggestions()
    _insights = load_insights()
    _suggestions = load_suggestions()
    _agent = _build_agent_with_context(_insights)
    return JSONResponse(_insights)


# ── Static files — must be mounted last so API routes take precedence ──────
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="static",
)
