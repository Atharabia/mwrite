from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_NAME: str = "Mwrite"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False

    DATABASE_URL: str = Field(min_length=1)

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_VIEW_FLUSH_INTERVAL: int = 60

    JWT_SECRET_KEY: str = Field(min_length=1)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    ADMIN_EMAIL: str = Field(min_length=1)
    ADMIN_PASSWORD: str = Field(min_length=1)
