from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from devtrack_sdk.middleware.extractor import extract_devtrack_log_data


class DevTrackMiddleware(BaseHTTPMiddleware):
    stats = []

    def __init__(self, app, api_key: str, backend_url: str = "/__devtrack__/track"):
        self.skip_paths = [backend_url, "/__devtrack__/stats"]
        self.api_key = api_key
        self.backend_url = backend_url
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
