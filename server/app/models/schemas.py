from typing import Any, Literal

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


class EvaluationCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    type: str = "MINI_QUIZ"
    knowledge_point: str = Field(..., min_length=1)


class EvaluationAnswer(BaseModel):
    question_id: str = Field(..., min_length=1)
    answer: str = ""


class EvaluationSubmit(BaseModel):
    answers: list[EvaluationAnswer]
    time_spent_seconds: int | None = None


class LearningPathCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    subject: str = "数据结构"
    goal: str = "考试与面试冲刺"


class PathAdjustRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    knowledge_point: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)


class ResourceFeedbackCreate(BaseModel):
    resource_id: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)
    feedback: Literal["USEFUL", "NOT_USEFUL"]
    user_id: str | None = None
    comment: str | None = None
