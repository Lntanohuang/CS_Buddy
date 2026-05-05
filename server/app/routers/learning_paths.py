from fastapi import APIRouter, Query

from app.learning_path.service import adjust_active_path, create_learning_path, get_or_create_active_path
from app.models.schemas import LearningPathCreate, PathAdjustRequest

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


@router.get("/active")
async def get_active_learning_path(
    user_id: str = Query(..., min_length=1),
    subject: str = "数据结构",
    goal: str = "考试与面试冲刺",
) -> dict:
    return await get_or_create_active_path(user_id=user_id, subject=subject, goal=goal)


@router.post("")
async def post_learning_path(payload: LearningPathCreate) -> dict:
    return await create_learning_path(
        user_id=payload.user_id,
        subject=payload.subject,
        goal=payload.goal,
    )


@router.post("/adjust")
async def post_learning_path_adjust(payload: PathAdjustRequest) -> dict:
    return await adjust_active_path(
        user_id=payload.user_id,
        knowledge_point=payload.knowledge_point,
        action=payload.action,
    )
