from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pymongo import ReturnDocument

from app.db.collections import notifications
from app.models.schemas import NotificationCreate

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _public_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


async def create_notification_document(payload: NotificationCreate) -> dict:
    now = datetime.now(timezone.utc)
    document = {
        "id": f"noti_{uuid4().hex}",
        "user_id": payload.user_id,
        "type": payload.type,
        "title": payload.title,
        "content": payload.content,
        "is_read": False,
        "action_url": payload.action_url,
        "created_at": now,
        "updated_at": now,
    }
    await notifications().insert_one(document)
    return _public_doc(document) or document


@router.post("")
async def post_notification(payload: NotificationCreate) -> dict:
    return await create_notification_document(payload)


@router.get("")
async def get_notifications(
    user_id: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
) -> list[dict]:
    cursor = (
        notifications()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [_public_doc(document) or document async for document in cursor]


@router.patch("/{notification_id}/read")
async def patch_notification_read(notification_id: str) -> dict:
    result = await notifications().find_one_and_update(
        {"id": notification_id},
        {"$set": {"is_read": True, "updated_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER,
    )
    document = _public_doc(result)
    if document is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return document


@router.patch("/read-all")
async def patch_notifications_read_all(user_id: str = Query(..., min_length=1)) -> dict:
    result = await notifications().update_many(
        {"user_id": user_id, "is_read": False},
        {"$set": {"is_read": True, "updated_at": datetime.now(timezone.utc)}},
    )
    return {"updated_count": result.modified_count}
