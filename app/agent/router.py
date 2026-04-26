import json
from typing import Literal

from fastapi import APIRouter
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

import state
from integration.langfuse import langfuse_handler

router = APIRouter()

LANG_SYSTEM: dict[str, str] = {
    "en": "Respond entirely in English.",
    "es": "Responde completamente en español.",
}


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=50_000)


class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    history: list[HistoryItem] = Field(default=[], max_length=20)
    language: str = "en"


@router.post("/api/chat")
async def chat(body: ChatRequest) -> EventSourceResponse:
    lang_msg = SystemMessage(content=LANG_SYSTEM.get(body.language, LANG_SYSTEM["en"]))
    messages = [lang_msg]
    for turn in body.history:
        cls = HumanMessage if turn.role == "user" else AIMessage
        messages.append(cls(content=turn.content))
    messages.append(HumanMessage(content=body.message))

    async def token_stream():
        seen_tool_calls: set[str] = set()
        async for token, _metadata in state.agent.astream(
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
                text_blocks = [b for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
                if text_blocks:
                    yield {"data": json.dumps(text_blocks)}
            elif isinstance(getattr(token, "content", None), str) and token.content:
                yield {"data": json.dumps([{"type": "text", "text": token.content}])}

    return EventSourceResponse(token_stream())
