import asyncio
import json
import time
from uuid import uuid4

from fastapi import APIRouter, Request
from langchain_core.messages import HumanMessage
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from sse_starlette.sse import EventSourceResponse

from app.agent.graph import build_graph
from app.config import settings
from app.db.retrieval_logger import log_retrieval
from app.memory.service import (
    build_memory_context,
    generate_and_store_summary,
    should_trigger_summary,
)
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


_langfuse_env_set = False


def _create_langfuse_handler(session_id: str, skill: str) -> CallbackHandler | None:
    if not settings.LANGFUSE_PUBLIC_KEY:
        return None
    global _langfuse_env_set
    if not _langfuse_env_set:
        import os
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_BASE_URL
        _langfuse_env_set = True
    return CallbackHandler()


@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> EventSourceResponse:
    active_skill = _detect_active_skill(payload.message)

    # 获取当前会话消息数（从 checkpointer state）
    thread_config = {"configurable": {"thread_id": payload.session_id}}
    try:
        state_snapshot = graph.get_state(thread_config)
        current_messages = state_snapshot.values.get("messages", [])
        message_count = len(current_messages)
    except Exception:
        message_count = 0
        current_messages = []

    # 构建记忆上下文（Phase B + C）
    memory_context = await build_memory_context(
        session_id=payload.session_id,
        message_count=message_count,
        user_id=payload.user_id,
        query=payload.message,
    )

    initial_state = {
        "messages": [HumanMessage(content=payload.message)],
        "active_skill": active_skill,
    }
    if memory_context:
        initial_state["memory_context"] = memory_context

    langfuse_handler = _create_langfuse_handler(payload.session_id, active_skill)
    config = {"configurable": {"thread_id": payload.session_id}}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    async def event_generator():
        start_time = time.time()
        full_response = ""
        try:
            async for event in graph.astream_events(initial_state, version="v2", config=config):
                if await request.is_disconnected():
                    break

                if event.get("event") != "on_chat_model_stream":
                    continue

                chunk = event.get("data", {}).get("chunk")
                token = _extract_chunk_text(chunk)
                if not token:
                    continue

                full_response += token
                yield _serialize_sse_event(SSEEvent(type="token", content=token))

            latency_ms = int((time.time() - start_time) * 1000)

            # retrieval log
            try:
                await log_retrieval(
                    session_id=payload.session_id,
                    user_id=None,
                    query=payload.message,
                    skill=active_skill,
                    retrieved_chunks=[],
                    memory_context=memory_context or None,
                    response_length=len(full_response),
                    feedback=None,
                    latency_ms=latency_ms,
                )
            except Exception:
                pass

            # Phase B: 摘要触发（+2 因为本轮的 user + assistant 消息）
            new_count = message_count + 2
            if should_trigger_summary(new_count):
                # 从 checkpointer 获取最新完整历史
                try:
                    updated_state = graph.get_state(config)
                    all_messages = updated_state.values.get("messages", [])
                    asyncio.create_task(
                        generate_and_store_summary(
                            payload.session_id, all_messages, user_id=payload.user_id
                        )
                    )
                except Exception as e:
                    print(f"[memory] 摘要触发失败: {e}")

            yield _serialize_sse_event(
                SSEEvent(type="done", data={"message_id": str(uuid4())})
            )
        except Exception as exc:
            yield _serialize_sse_event(
                SSEEvent(type="error", content=f"服务暂时不可用：{exc}")
            )
        finally:
            if langfuse_handler:
                get_client().flush()

    return EventSourceResponse(event_generator())
