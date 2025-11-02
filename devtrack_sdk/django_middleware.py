import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from .database import DevTrackDB


class DevTrackDjangoMiddleware(MiddlewareMixin):
    """
    Django middleware for request tracking with DuckDB integration
    """

    _db_instance: Optional[DevTrackDB] = None

    def __init__(
        self, get_response=None, exclude_path: list[str] = None, db_path: str = None
    ):
        self.get_response = get_response
        self.skip_paths = [
            "/__devtrack__/stats",
            "/__devtrack__/logs",
            "/admin/",
            "/static/",
            "/media/",
            "/favicon.ico",
            "/health",
            "/metrics",
        ]
        if exclude_path:
            self.skip_paths.extend(exclude_path)

        # Initialize database if not already done
        if DevTrackDjangoMiddleware._db_instance is None:
            db_path = db_path or getattr(
                settings, "DEVTRACK_DB_PATH", "devtrack_logs.db"
            )
            DevTrackDjangoMiddleware._db_instance = DevTrackDB(db_path)

        super().__init__(get_response)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path in self.skip_paths:
            return self.get_response(request)

        start_time = datetime.now(timezone.utc)

        # Process the request
        response = self.get_response(request)

        try:
            log_data = self._extract_devtrack_log_data(request, response, start_time)
            # Store in DuckDB instead of in-memory list
            DevTrackDjangoMiddleware._db_instance.insert_log(log_data)
        except Exception as e:
            print(f"[DevTrackDjangoMiddleware] Logging error: {e}")

        return response

    def _extract_devtrack_log_data(
        self, request: HttpRequest, response: HttpResponse, start_time: datetime
    ) -> Dict[str, Any]:
        """Extract tracking data from Django request/response"""
        duration = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds() * 1000  # in ms

        # Get path pattern (Django doesn't have route objects like FastAPI)
        path_pattern = (
            request.resolver_match.route if request.resolver_match else request.path
        )

        # Capture query params
        query_params = dict(request.GET)

        # Capture request body
        request_body = {}
        if request.content_type == "application/json":
            try:
                request_body = (
                    json.loads(request.body.decode("utf-8")) if request.body else {}
                )
            except Exception as e:
                request_body = {"error": f"Invalid JSON: {str(e)}"}
        elif request.content_type == "application/x-www-form-urlencoded":
            request_body = dict(request.POST)
        else:
            request_body = {"error": "Unsupported content type"}

        # Filter sensitive data
        if "password" in request_body:
            request_body["password"] = "***"

        # Get response size
        response_size = len(response.content) if hasattr(response, "content") else 0

        # Get headers
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referer = request.META.get("HTTP_REFERER", "")

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Get user info if authenticated
        user_id = None
        role = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.id)
            role = getattr(request.user, "role", None) or "user"

        return {
            "path": request.path,
            "path_pattern": path_pattern,
            "method": request.method,
            "status_code": response.status_code,
            "timestamp": start_time.isoformat(),
            "client_ip": client_ip,
            "duration_ms": round(duration, 2),
            "user_agent": user_agent,
            "referer": referer,
            "query_params": query_params,
            "path_params": (
                dict(request.resolver_match.kwargs) if request.resolver_match else {}
            ),
            "request_body": request_body,
            "response_size": response_size,
            "user_id": user_id,
            "role": role,
            "trace_id": str(uuid.uuid4()),
        }

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get the real client IP address"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip or "unknown"
