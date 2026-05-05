from fastapi import APIRouter, Query

from app.db.collections import retrieval_logs

router = APIRouter(prefix="/observability", tags=["observability"])


def _public_doc(document: dict) -> dict:
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


@router.get("/retrieval-logs")
async def get_retrieval_logs(
    user_id: str | None = None,
    session_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    query: dict[str, str | None] = {}
    if user_id is not None:
        query["user_id"] = user_id
    if session_id is not None:
        query["session_id"] = session_id

    cursor = retrieval_logs().find(query).sort("timestamp", -1).limit(limit)
    return [_public_doc(document) async for document in cursor]
