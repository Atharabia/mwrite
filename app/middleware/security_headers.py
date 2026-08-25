from fastapi import Request
from fastapi.responses import Response

_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: blob:; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "connect-src 'self'"
)

_CSP_READER_POST = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
    "https://cdnjs.cloudflare.com https://unpkg.com "
    "https://cdn.plot.ly https://d3js.org; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
    "https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
    "img-src 'self' data: blob: https:; "
    "font-src 'self' https://cdn.jsdelivr.net "
    "https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
    "connect-src 'self' https:"
)


async def security_headers(request: Request, call_next: object) -> Response:
    response: Response = await call_next(request)  # type: ignore[operator]
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if request.url.path.startswith("/blog/"):
        response.headers["Content-Security-Policy"] = _CSP_READER_POST
    else:
        response.headers["Content-Security-Policy"] = _CSP
    return response
