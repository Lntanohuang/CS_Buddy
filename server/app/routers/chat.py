import json
from uuid import uuid4

from fastapi import APIRouter, Request
from langchain_core.messages import HumanMessage
from sse_starlette.sse import EventSourceResponse

from app.agent.graph import build_graph
from app.models.schemas import ChatRequest, SSEEvent

router = APIRouter(prefix="/chat", tags=["chat"])
graph = build_graph()


def _detect_active_skill(message: str) -> str:
    lower = message.lower()
    if "出题" in message or "练习" in message or "quiz" in lower:
        return "quiz"
    if any(kw in message for kw in ["讲讲", "解释", "什么是", "原理", "怎么", "如何", "区别"]) or any(
        kw in lower for kw in ["explain", "how", "what is"]
    ):
        return "explain"
    return "clarify"


def _serialize_sse_event(event: SSEEvent) -> dict[str, str]:
    payload = json.dumps(event.model_dump(exclude_none=True), ensure_ascii=False)
    return {"data": payload}


def _extract_chunk_text(chunk: object) -> str:
    content = getattr(chunk, "content", None)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)

    return ""


@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> EventSourceResponse:
    active_skill = _detect_active_skill(payload.message)
    initial_state = {
        "messages": [HumanMessage(content=payload.message)],
        "active_skill": active_skill,
    }

    async def event_generator():
        try:
            async for event in graph.astream_events(initial_state, version="v2"):
                if await request.is_disconnected():
                    break

                if event.get("event") != "on_chat_model_stream":
                    continue

                chunk = event.get("data", {}).get("chunk")
                token = _extract_chunk_text(chunk)
                if not token:
                    continue

                yield _serialize_sse_event(SSEEvent(type="token", content=token))

            yield _serialize_sse_event(
                SSEEvent(type="done", data={"message_id": str(uuid4())})
            )
        except Exception as exc:
            yield _serialize_sse_event(
                SSEEvent(type="error", content=f"服务暂时不可用：{exc}")
            )

    return EventSourceResponse(event_generator())
