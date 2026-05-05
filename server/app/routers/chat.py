import asyncio
import json
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request
from langchain_core.messages import HumanMessage
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from sse_starlette.sse import EventSourceResponse

from app.agent.graph import build_graph
from app.agent.tools import RETRIEVAL_TRACE
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


def _serialize_sse_event(event: SSEEvent) -> dict[str, str]:
    payload = json.dumps(
        event.model_dump(exclude_none=True),
        ensure_ascii=False,
        separators=(",", ":"),
    )
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


def _build_retrieved_contexts(retrieval_trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for trace_entry in retrieval_trace:
        for result in trace_entry.get("results", []):
            if not isinstance(result, dict):
                continue
            contexts.append(
                {
                    "source": result.get("source", ""),
                    "course": result.get("course", ""),
                    "header_1": result.get("header_1", ""),
                    "header_2": result.get("header_2", ""),
                    "header_3": result.get("header_3", ""),
                    "score": result.get("score"),
                }
            )
    return contexts


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
    }
    if memory_context:
        initial_state["memory_context"] = memory_context

    langfuse_handler = _create_langfuse_handler(payload.session_id, "orchestrator")
    config = {"configurable": {"thread_id": payload.session_id}}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    async def event_generator():
        start_time = time.time()
        monotonic_start = time.monotonic()
        full_response = ""
        retrieval_trace: list[dict[str, Any]] = []
        retrieval_token = RETRIEVAL_TRACE.set(retrieval_trace)
        tool_starts: dict[str, tuple[str, float]] = {}
        tool_calls: list[dict[str, Any]] = []
        graph_path: list[str] = []
        graph_nodes = {
            "orchestrator",
            "explain_agent",
            "quiz_agent",
            "clarify_agent",
            "tools",
        }
        route_trace: dict[str, Any] = {}
        try:
            async for event in graph.astream_events(initial_state, version="v2", config=config):
                if await request.is_disconnected():
                    break

                event_type = event.get("event")
                event_name = event.get("name", "")
                run_id = str(event.get("run_id", ""))

                if event_type == "on_chain_start" and event_name in graph_nodes:
                    graph_path.append(event_name)
                elif event_type == "on_chain_end" and event_name == "orchestrator":
                    output = event.get("data", {}).get("output") or {}
                    if isinstance(output, dict):
                        route = output.get("orchestrator_trace") or output
                        if isinstance(route, dict):
                            route_trace = route
                elif event_type == "on_tool_start":
                    tool_starts[run_id] = (event_name, time.monotonic())
                elif event_type == "on_tool_end":
                    tool_name, tool_start = tool_starts.pop(
                        run_id,
                        (event_name, time.monotonic()),
                    )
                    tool_calls.append(
                        {
                            "name": tool_name,
                            "duration_ms": int((time.monotonic() - tool_start) * 1000),
                        }
                    )

                if event_type != "on_chat_model_stream":
                    continue

                chunk = event.get("data", {}).get("chunk")
                token = _extract_chunk_text(chunk)
                if not token:
                    continue

                full_response += token
                yield _serialize_sse_event(SSEEvent(type="token", content=token))

            latency_ms = int((time.time() - start_time) * 1000)
            active_skill = str(route_trace.get("active_skill") or "explain")
            trace = {
                "skill_id": active_skill,
                "intent": route_trace.get("intent"),
                "resource_type": route_trace.get("resource_type"),
                "intent_confidence": route_trace.get("confidence"),
                "intent_reason": route_trace.get("reason"),
                "orchestrator": {
                    "router": route_trace.get("router"),
                    "selected_node": route_trace.get("selected_node"),
                    "selected_skill": route_trace.get("selected_skill"),
                },
                "tool_calls": tool_calls,
                "retrieved_contexts": _build_retrieved_contexts(retrieval_trace),
                "graph_path": graph_path,
                "latency_ms": int((time.monotonic() - monotonic_start) * 1000),
            }

            # retrieval log
            assistant_message_id = str(uuid4())
            try:
                retrieved_contexts = _build_retrieved_contexts(retrieval_trace)
                await log_retrieval(
                    session_id=payload.session_id,
                    message_id=assistant_message_id,
                    user_id=payload.user_id,
                    query=payload.message,
                    skill=active_skill,
                    retrieved_chunks=retrieved_contexts,
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
                SSEEvent(type="done", data={"message_id": assistant_message_id, "trace": trace})
            )
        except Exception as exc:
            yield _serialize_sse_event(
                SSEEvent(type="error", content=f"服务暂时不可用：{exc}")
            )
        finally:
            RETRIEVAL_TRACE.reset(retrieval_token)
            if langfuse_handler:
                get_client().flush()

    return EventSourceResponse(event_generator())
