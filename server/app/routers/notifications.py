from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pymongo import ReturnDocument

from app.db.collections import notifications
from app.models.schemas import NotificationCreate
from app.notifications.service import create_notification, list_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _public_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


@router.post("")
async def post_notification(payload: NotificationCreate) -> dict:
    return await create_notification(
        user_id=payload.user_id,
        notification_type=payload.type,
        title=payload.title,
        content=payload.content,
        action_url=payload.action_url,
    )


@router.get("")
async def get_notifications(
    user_id: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
) -> list[dict]:
    return await list_notifications(user_id=user_id, limit=limit)


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
