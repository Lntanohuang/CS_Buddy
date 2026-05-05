from datetime import datetime, timezone
from uuid import uuid4

from app.db.collections import notifications


def _public_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    content: str,
    action_url: str | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    document = {
        "id": f"noti_{uuid4().hex}",
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "content": content,
        "is_read": False,
        "action_url": action_url,
        "created_at": now,
        "updated_at": now,
    }
    await notifications().insert_one(document)
    return _public_doc(document) or document


async def list_notifications(user_id: str, limit: int = 50) -> list[dict]:
    cursor = (
        notifications()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [_public_doc(document) or document async for document in cursor]
