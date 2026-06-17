from typing import Annotated

from fastapi import APIRouter, Depends

from app.controller import SettingController
from app.dependencies import require_super_admin
from app.models.responses import Response, Status
from app.models.schemas import SettingsUpdate
from app.redis.settings import get_cached_settings, set_cached_settings, invalidate_settings


router = APIRouter(
    prefix="/settings",
    tags=["Writer"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("", response_model=Response)
async def get_settings() -> Response:
    cached = await get_cached_settings()
    if cached:
        return Response(status=Status.success, data=cached)
    settings = await SettingController.get_all()
    await set_cached_settings(settings)
    return Response(status=Status.success, data=settings)


@router.patch("", response_model=Response)
async def update_settings(body: SettingsUpdate) -> Response:
    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        await SettingController.set(key=key, value=str(value).lower() if isinstance(value, bool) else str(value))
    await invalidate_settings()
    settings = await SettingController.get_all()
    await set_cached_settings(settings)
    return Response(status=Status.success, data=settings)
