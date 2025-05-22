from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message

from devtrack_sdk.middleware.extractor import extract_devtrack_log_data


class DevTrackMiddleware(BaseHTTPMiddleware):
    stats = []

    def __init__(self, app, exclude_path: list[str] = []):
        self.skip_paths = [
            "/__devtrack__/stats",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health",
            "/metrics",
        ]
        self.skip_paths += exclude_path if isinstance(exclude_path, list) else []
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.skip_paths:
            return await call_next(request)

        start_time = datetime.now(timezone.utc)

        # ✅ Read and buffer the body
        body = await request.body()

        async def receive() -> Message:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        # ✅ Rebuild the request with the modified receive function
        request = Request(request.scope, receive)

        response = await call_next(request)

        try:
            log_data = await extract_devtrack_log_data(request, response, start_time)
            DevTrackMiddleware.stats.append(log_data)
        except Exception as e:
            print(f"[DevTrackMiddleware] Logging error: {e}")

        return response
