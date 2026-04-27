from datetime import datetime, timezone
from typing import Any

from app.db.collections import retrieval_logs


async def log_retrieval(
    session_id: str,
    user_id: str | None,
    query: str,
    skill: str,
    retrieved_chunks: list[dict[str, Any]],
    memory_context: str | None,
    response_length: int,
    feedback: str | None,
    latency_ms: int,
) -> None:
    document = {
        "session_id": session_id,
        "user_id": user_id,
        "query": query,
        "skill": skill,
        "retrieved_chunks": retrieved_chunks,
        "memory_context": memory_context,
        "response_length": response_length,
        "feedback": feedback,
        "latency_ms": latency_ms,
        "timestamp": datetime.now(timezone.utc),
    }
    await retrieval_logs().insert_one(document)
