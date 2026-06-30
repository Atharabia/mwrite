from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limiter import limiter
from app.middleware.security_headers import security_headers


async def _rate_limit_exceeded_handler_with_type(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )


class MiddlewareRegistry:
    @staticmethod
    def register_middlewares(app: FastAPI) -> None:
        app.state.limiter = limiter
        app.add_exception_handler(
            RateLimitExceeded,
            _rate_limit_exceeded_handler_with_type,
        )
        app.middleware("http")(security_headers)
