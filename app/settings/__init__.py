from functools import lru_cache

from .config import Config


@lru_cache
def get_settings() -> Config:
    return Config()


Settings = get_settings()

__all__ = ["Settings"]
