"""长期事件记忆：FAISS 向量存储 + MongoDB 持久化。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.db.collections import memory_events
from app.rag.embeddings import get_embeddings

_EVENT_STORE: FAISS | None = None
_INDEX_DIR = Path(__file__).resolve().parents[2] / "event_memory_index"


def _get_event_store() -> FAISS:
    """懒加载事件记忆 FAISS 索引。"""
    global _EVENT_STORE
    if _EVENT_STORE is not None:
        return _EVENT_STORE

    faiss_file = _INDEX_DIR / "index.faiss"
    if faiss_file.exists():
        _EVENT_STORE = FAISS.load_local(
            str(_INDEX_DIR),
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    else:
        # 创建空索引（用占位文档初始化）
        _EVENT_STORE = FAISS.from_documents(
            [Document(page_content="init", metadata={"type": "placeholder"})],
            get_embeddings(),
        )
        _INDEX_DIR.mkdir(parents=True, exist_ok=True)
        _EVENT_STORE.save_local(str(_INDEX_DIR))

    return _EVENT_STORE


def add_event(text: str, user_id: str, session_id: str) -> None:
    """添加一条事件记忆。"""
    store = _get_event_store()
    metadata = {
        "user_id": user_id,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.add_texts([text], metadatas=[metadata])
    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(_INDEX_DIR))


def search_events(
    query: str,
    user_id: str,
    top_k: int = 3,
    max_distance: float = 280.0,
) -> list[str]:
    """检索与查询相关的事件记忆。"""
    store = _get_event_store()
    results = store.similarity_search_with_score(query, k=top_k * 2)

    matched: list[str] = []
    for doc, distance in results:
        if doc.metadata.get("type") == "placeholder":
            continue
        if doc.metadata.get("user_id") != user_id:
            continue
        if distance > max_distance:
            continue
        matched.append(doc.page_content)
        if len(matched) >= top_k:
            break

    return matched


async def persist_event_to_mongo(
    event_text: str,
    user_id: str,
    session_id: str,
) -> None:
    """事件同时写入 MongoDB 用于持久化备份。"""
    await memory_events().insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "event_text": event_text,
        "created_at": datetime.now(timezone.utc),
    })
