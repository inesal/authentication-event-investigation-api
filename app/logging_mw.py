import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.settings import get_settings

settings = get_settings()
logger = logging.getLogger("lanl.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code >= 500:
            logger.error(
                "request_error",
                extra={
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency_ms": round(elapsed_ms, 2),
                },
            )
        elif elapsed_ms > settings.slow_request_ms:
            logger.warning(
                "slow_request",
                extra={
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency_ms": round(elapsed_ms, 2),
                },
            )
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response
