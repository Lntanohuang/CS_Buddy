import asyncio
from contextvars import ContextVar
from typing import Any

from langchain_core.tools import tool

RETRIEVAL_TRACE: ContextVar[list[dict[str, Any]] | None] = ContextVar(
    "RETRIEVAL_TRACE",
    default=None,
)


@tool
def get_profile(user_id: str) -> dict:
    """获取用户画像。"""
    from app.memory.service import load_user_profile, ensure_default_profile

    loop = asyncio.get_event_loop()
    profile = loop.run_until_complete(load_user_profile(user_id))
    if profile is None:
        profile = loop.run_until_complete(ensure_default_profile(user_id))
    return profile


@tool
def search_knowledge(query: str) -> str:
    """搜索课程知识库，返回与查询最相关的知识片段。"""
    from app.rag.retriever import retrieve

    results = retrieve(query)
    trace = RETRIEVAL_TRACE.get()
    if trace is not None:
        trace.append({"query": query, "results": results})

    if not results:
        return "知识库中未找到与该查询高度相关的内容。"

    parts = []
    for r in results:
        parts.append(f'【{r["course"]} - {r["source"]}】\n{r["content"]}')
    return "\n\n---\n\n".join(parts)
