from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limiter import limiter
from app.middleware.security_headers import security_headers


class MiddlewareRegistry:
    @staticmethod
    def register_middlewares(app: FastAPI) -> None:
        app.state.limiter = limiter
        app.add_exception_handler(
            RateLimitExceeded, _rate_limit_exceeded_handler
        )
        app.middleware("http")(security_headers)
