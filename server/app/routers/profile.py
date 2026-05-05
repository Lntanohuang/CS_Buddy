from fastapi import APIRouter

from app.memory.service import ensure_default_profile, update_user_profile
from app.models.schemas import ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{user_id}")
async def get_profile(user_id: str) -> dict:
    return await ensure_default_profile(user_id)


@router.patch("/{user_id}")
async def patch_profile(user_id: str, payload: ProfileUpdate) -> dict:
    return await update_user_profile(
        user_id=user_id,
        updates=payload.model_dump(exclude_unset=True),
    )
