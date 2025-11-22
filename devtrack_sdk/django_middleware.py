import hashlib
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
            # Store in DuckDB directly (synchronous write)
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

        # Consumer Segmentation: Identify client from multiple sources
        client_identifier = self._identify_client(request, user_id)
        client_identifier_hash = (
            self._hash_identifier(client_identifier) if client_identifier else None
        )

        # Hash all PII for privacy: user_id, IP address, user_agent
        user_id_hash = self._hash_identifier(user_id) if user_id else None
        ip_hash = (
            self._hash_identifier(client_ip)
            if client_ip and client_ip != "unknown"
            else None
        )
        user_agent_hash = self._hash_identifier(user_agent) if user_agent else None

        return {
            "path": request.path,
            "path_pattern": path_pattern,
            "method": request.method,
            "status_code": response.status_code,
            "timestamp": start_time.isoformat(),
            "client_ip": ip_hash or client_ip,  # Hashed IP (fallback if hash fails)
            "duration_ms": round(duration, 2),
            "user_agent": user_agent_hash or user_agent,  # Hashed user_agent
            "referer": referer,  # Referer is less sensitive, keep as-is
            "query_params": query_params,
            "path_params": (
                dict(request.resolver_match.kwargs) if request.resolver_match else {}
            ),
            "request_body": request_body,
            "response_size": response_size,
            "user_id": user_id_hash or user_id,  # Hashed user_id (fallback if fails)
            "role": role,  # Role is not PII, keep as-is
            "trace_id": str(uuid.uuid4()),
            "client_identifier": client_identifier,  # Original (internal use only)
            "client_identifier_hash": client_identifier_hash,  # Hashed for privacy
        }

    def _identify_client(
        self, request: HttpRequest, user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Identify client from multiple sources (priority order):
        1. Headers (x-client-id, x-api-key, x-app-id, etc.)
        2. JWT token (from Authorization header)
        3. Auth context (user_id from authenticated user)
        4. IP address (as fallback)
        """
        # 1. Check custom client identification headers
        client_id_headers = [
            "HTTP_X_CLIENT_ID",
            "HTTP_X_API_KEY",
            "HTTP_X_APP_ID",
            "HTTP_X_CONSUMER_ID",
            "HTTP_X_TENANT_ID",
            "HTTP_CLIENT_ID",
            "HTTP_API_KEY",
        ]
        for header_name in client_id_headers:
            client_id = request.META.get(header_name)
            if client_id:
                # Convert Django header name back to original
                original_header = (
                    header_name.replace("HTTP_", "").replace("_", "-").lower()
                )
                return f"header:{original_header}:{client_id}"

        # 2. Extract from JWT token (Authorization header)
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            try:
                # Simple extraction - use first 32 chars as identifier
                token_id = token[:32]
                return f"jwt:{token_id}"
            except Exception:
                pass

        # 3. Use authenticated user ID if available
        if user_id:
            return f"user:{user_id}"

        # 4. Check request for auth context
        if hasattr(request, "user") and request.user.is_authenticated:
            if hasattr(request.user, "id"):
                return f"auth:{request.user.id}"
            elif hasattr(request.user, "username"):
                return f"auth:{request.user.username}"

        # 5. Fallback to IP address
        client_ip = self._get_client_ip(request)
        if client_ip and client_ip != "unknown":
            return f"ip:{client_ip}"

        return None

    def _hash_identifier(self, identifier: Optional[str]) -> Optional[str]:
        """Hash client identifier for privacy (SHA-256)."""
        if not identifier:
            return None
        return hashlib.sha256(identifier.encode()).hexdigest()[
            :16
        ]  # Use first 16 chars for shorter hash

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Get the real public client IP address.
        Handles proxies, load balancers, and CDNs by checking common headers.
        Priority order:
        1. X-Forwarded-For (first IP in chain)
        2. X-Real-IP
        3. X-Client-IP
        4. CF-Connecting-IP (Cloudflare)
        5. True-Client-IP (Akamai/Cloudflare)
        6. REMOTE_ADDR (direct connection)
        """
        # 1. X-Forwarded-For: Multiple IPs, take first (original client)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # X-Forwarded-For can be comma-separated: "client, proxy1, proxy2"
            # The first IP is the original client
            ip = x_forwarded_for.split(",")[0].strip()
            if ip:
                return ip

        # 2. X-Real-IP: Single IP header (nginx, etc.)
        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            return x_real_ip.strip()

        # 3. X-Client-IP: Alternative header
        x_client_ip = request.META.get("HTTP_X_CLIENT_IP")
        if x_client_ip:
            return x_client_ip.strip()

        # 4. CF-Connecting-IP: Cloudflare
        cf_connecting_ip = request.META.get("HTTP_CF_CONNECTING_IP")
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        # 5. True-Client-IP: Akamai/Cloudflare
        true_client_ip = request.META.get("HTTP_TRUE_CLIENT_IP")
        if true_client_ip:
            return true_client_ip.strip()

        # 6. Fallback to REMOTE_ADDR (direct connection)
        remote_addr = request.META.get("REMOTE_ADDR")
        if remote_addr:
            return remote_addr.strip()

        return "unknown"
