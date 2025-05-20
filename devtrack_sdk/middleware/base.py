from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from devtrack_sdk.middleware.extractor import extract_devtrack_log_data


class DevTrackMiddleware(BaseHTTPMiddleware):
    stats = []

    def __init__(
        self,
        app,
        exclude_path: list[str] = [],
    ):
        self.skip_paths = [
            "/__devtrack__/stats",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health",
            "/metrics",
        ]
        try:
            if not isinstance(exclude_path, list):
                raise TypeError("exclude_path must be a list")
            self.skip_paths += exclude_path
        except TypeError as e:
            print(f"[DevTrackMiddleware] Error in exclude_path: {e}")
            raise e

        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.skip_paths:
            return await call_next(request)

        start_time = datetime.now(timezone.utc)
        try:
            response = await call_next(request)
            log_data = extract_devtrack_log_data(request, response, start_time)
            DevTrackMiddleware.stats.append(log_data)
            return response

        except Exception as e:
            print("[DevTrackMiddleware] Tracking error:", e)

        return response
