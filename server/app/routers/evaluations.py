from fastapi import APIRouter, HTTPException, Query

from app.evaluation.service import create_evaluation, get_evaluation, list_evaluations
from app.models.schemas import EvaluationCreate

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("")
async def post_evaluation(payload: EvaluationCreate) -> dict:
    return await create_evaluation(
        user_id=payload.user_id,
        eval_type=payload.type,
        knowledge_point=payload.knowledge_point,
    )


@router.get("")
async def get_evaluations(
    user_id: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    return await list_evaluations(user_id=user_id, limit=limit)


@router.get("/{eval_id}")
async def get_evaluation_by_id(eval_id: str) -> dict:
    evaluation = await get_evaluation(eval_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return evaluation
