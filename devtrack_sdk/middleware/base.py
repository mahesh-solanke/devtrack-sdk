from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message

from devtrack_sdk.database import get_db
from devtrack_sdk.middleware.extractor import extract_devtrack_log_data


class DevTrackMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_path: list[str] = [], db_instance=None):
        self.skip_paths = [
            "/__devtrack__/stats",
            "/__devtrack__/logs",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health",
            "/metrics",
        ]
        self.skip_paths += exclude_path if isinstance(exclude_path, list) else []
        self.db_instance = db_instance
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip logging for DevTrack endpoints and excluded paths
        if request.url.path in self.skip_paths or request.url.path.startswith(
            "/__devtrack__/"
        ):
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
            db = self.db_instance if self.db_instance else get_db(read_only=False)
            db.insert_log(log_data)
        except Exception as e:
            print(f"[DevTrackMiddleware] Logging error: {e}")

        return response
