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


class ProfileUpdate(BaseModel):
    major: str | None = None
    current_level: str | None = None
    learning_goal: str | None = None
    preferred_style: str | None = None
    cognitive_style: str | None = None
    error_patterns: list[str] | None = None
    daily_time_minutes: int | None = None
    knowledge_mastery: dict[str, float] | None = None
    weak_points: list[str] | None = None
    style_weights: dict[str, float] | None = None
    subjects: list[str] | None = None
    profile_complete: bool | None = None
