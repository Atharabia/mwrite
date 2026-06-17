import json

from app.redis import client

_CACHE_KEY = "settings:all"
_CACHE_TTL = 3600


async def get_cached_settings() -> dict[str, str] | None:
    raw = await client.get(_CACHE_KEY)
    return json.loads(raw) if raw else None


async def set_cached_settings(settings: dict[str, str]) -> None:
    await client.set(_CACHE_KEY, json.dumps(settings), ex=_CACHE_TTL)


async def invalidate_settings() -> None:
    await client.delete(_CACHE_KEY)


async def get_settings() -> dict[str, str]:
    from app.controller.setting import SettingController
    cached = await get_cached_settings()
    if cached:
        return cached
    settings = await SettingController.get_all()
    await set_cached_settings(settings)
    return settings
