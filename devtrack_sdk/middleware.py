
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import httpx

EXCLUDED_PATHS = ["/track", "/stats"]

class DevTrackMiddleware(BaseHTTPMiddleware):
    stats = []  # class-level log store

    def __init__(self, app, api_key: str, backend_url: str):
        super().__init__(app)
        self.api_key = api_key
        self.backend_url = backend_url

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        response = await call_next(request)

        try:
            payload = {
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "client": request.client.host,
            }
            # Optional: Add generic error message for common error codes
            if response.status_code >= 400:
                payload["error_message"] = {
                    400: "Bad Request",
                    401: "Unauthorized",
                    403: "Forbidden",
                    404: "Not Found",
                    500: "Internal Server Error"
                }.get(response.status_code, "Unknown Error")
            else:
                payload["error_message"] = None

            DevTrackMiddleware.stats.append(payload)

            headers = {"x-api-key": self.api_key}
            async with httpx.AsyncClient() as client:
                await client.post(self.backend_url, json=payload, headers=headers)
        except Exception as e:
            print(f"[DevTrackMiddleware] Error tracking request: {e}")

        return response
