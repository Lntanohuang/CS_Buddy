from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Query

from app.db.collections import resource_feedbacks, retrieval_logs
from app.models.schemas import ResourceFeedbackCreate

router = APIRouter(prefix="/resources", tags=["resources"])


def _public_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


@router.post("/feedback")
async def post_resource_feedback(payload: ResourceFeedbackCreate) -> dict:
    now = datetime.now(timezone.utc)
    selector = {
        "resource_id": payload.resource_id,
        "message_id": payload.message_id,
        "user_id": payload.user_id,
    }
    await resource_feedbacks().update_one(
        selector,
        {
            "$set": {
                "feedback": payload.feedback,
                "comment": payload.comment,
                "updated_at": now,
            },
            "$setOnInsert": {
                "feedback_id": f"rf_{uuid4().hex}",
                "resource_id": payload.resource_id,
                "message_id": payload.message_id,
                "user_id": payload.user_id,
                "created_at": now,
            },
        },
        upsert=True,
    )
    await retrieval_logs().update_many(
        {"message_id": payload.message_id},
        {"$set": {"feedback": payload.feedback, "feedback_updated_at": now}},
    )
    document = await resource_feedbacks().find_one(selector)
    return _public_doc(document) or {}


@router.get("/feedback")
async def get_resource_feedback(
    user_id: str | None = None,
    resource_id: str | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    query: dict[str, str | None] = {}
    if user_id is not None:
        query["user_id"] = user_id
    if resource_id is not None:
        query["resource_id"] = resource_id

    cursor = resource_feedbacks().find(query).sort("updated_at", -1).limit(limit)
    return [_public_doc(document) or document async for document in cursor]
