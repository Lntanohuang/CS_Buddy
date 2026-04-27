from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    user_id: str | None = None


class SSEEvent(BaseModel):
    type: str
    content: str | None = None
    data: dict[str, Any] | None = None
