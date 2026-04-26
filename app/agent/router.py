import json
import time
from typing import Literal

from fastapi import APIRouter
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from loguru import logger
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from agent.agent import build_agent_with_context
from integration.langfuse import langfuse_handler
from logging_config import divider, log_block

router = APIRouter()

LANG_SYSTEM: dict[str, str] = {
    "en": "Respond entirely in English.",
    "es": "Responde completamente en español.",
}


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=50_000)


class InsightItem(BaseModel):
    text_en: str
    value: str


class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    history: list[HistoryItem] = Field(default=[], max_length=20)
    language: str = "en"
    insights: list[InsightItem] = Field(default=[])


@router.post("/api/chat")
async def chat(body: ChatRequest) -> EventSourceResponse:
    agent = build_agent_with_context({"insights": [i.model_dump() for i in body.insights]})

    lang_msg = SystemMessage(content=LANG_SYSTEM.get(body.language, LANG_SYSTEM["en"]))
    messages = [lang_msg]
    for turn in body.history:
        cls = HumanMessage if turn.role == "user" else AIMessage
        messages.append(cls(content=turn.content))
    messages.append(HumanMessage(content=body.message))

    # ── Request header ────────────────────────────────────────
    logger.info(divider("CHAT REQUEST"))
    logger.info(f"│  Language : {body.language.upper()}  |  History : {len(body.history)} turn(s)")
    logger.info(f"│  User     : {body.message}")
    if body.insights:
        logger.info("│  Insights :")
        for ins in body.insights:
            logger.info(f"│    • {ins.text_en}  →  {ins.value}")
    logger.info(divider())

    async def token_stream():
        seen_tool_calls: set[str] = set()
        response_chunks: list[str] = []
        t0 = time.perf_counter()

        async for token, _metadata in agent.astream(
            {"messages": messages},
            stream_mode="messages",
            config={
                "callbacks": [langfuse_handler] if langfuse_handler else [],
                "metadata": {"source": "chat_engine"},
            },
        ):
            # ── Tool response ─────────────────────────────────
            if isinstance(token, ToolMessage):
                name = getattr(token, "name", "unknown")
                content = token.content if isinstance(token.content, str) else str(token.content)
                lines = content.splitlines()
                logger.info(divider(f"TOOL RESPONSE  {name}"))
                # First 20 lines to console (INFO), full output to file (DEBUG)
                log_block(lines[:20], level="INFO")
                if len(lines) > 20:
                    logger.info(f"│  … {len(lines) - 20} more line(s) — see log file")
                    log_block(lines[20:], level="DEBUG")
                logger.info(divider())
                continue

            tool_call_chunks = getattr(token, "tool_call_chunks", [])
            for chunk in tool_call_chunks:
                call_id = chunk.get("id") or str(chunk.get("index", 0))
                name = chunk.get("name", "")
                if name and call_id not in seen_tool_calls:
                    seen_tool_calls.add(call_id)
                    logger.info(f"⚙  Calling   : {name}")
                    yield {"data": json.dumps([{"type": "tool_use", "name": name}])}
            if tool_call_chunks:
                continue

            blocks = getattr(token, "content_blocks", None)
            if blocks:
                text_blocks = [b for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
                if text_blocks:
                    for b in text_blocks:
                        response_chunks.append(b.get("text", ""))
                    yield {"data": json.dumps(text_blocks)}
            elif isinstance(getattr(token, "content", None), str) and token.content:
                response_chunks.append(token.content)
                yield {"data": json.dumps([{"type": "text", "text": token.content}])}

        # ── Response summary ──────────────────────────────────
        elapsed = time.perf_counter() - t0
        full_response = "".join(response_chunks)
        logger.info(divider(f"RESPONSE  {elapsed:.1f}s"))
        log_block(full_response.splitlines(), level="INFO")
        logger.info(divider())

    return EventSourceResponse(token_stream())
