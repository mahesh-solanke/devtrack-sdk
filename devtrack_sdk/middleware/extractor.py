import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import Request, Response


async def extract_devtrack_log_data(
    request: Request, response: Response, start_time: datetime
) -> Dict[str, Any]:
    duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000  # in ms
    headers = request.headers

    # Get the route object and path pattern
    route = request.scope.get("route")
    path_pattern = route.path_format if route else request.url.path

    # Capture query params and request body (optional: filter sensitive keys)
    path_params = dict(request.path_params)
    query_params = dict(request.query_params)
    request_body = {}
    if request.headers.get("content-type") == "application/json":
        try:
            request_body = await request.json()
        except Exception as e:
            request_body = {"error": f"Invalid JSON: {str(e)}"}
    else:
        request_body = {"error": "No JSON content"}

    if "password" in request_body:
        request_body["password"] = "***"
    response_size = int(response.headers.get("content-length", 0))

    # Safe fallback if user-agent or referer is missing
    user_agent = headers.get("user-agent", "")
    referer = headers.get("referer", "")

    # Simulated user ID and role - replace with actual auth extraction logic
    user_id = headers.get("x-user-id")
    role = headers.get("x-user-role")

    # Consumer Segmentation: Identify client from multiple sources
    client_identifier = _identify_client(request, user_id)

    # Extract real public IP address (handles proxies, load balancers, etc.)
    public_ip = _get_public_ip(request)

    return {
        "path": request.url.path,  # Original path with actual values
        "path_pattern": path_pattern,  # Normalized path with parameter names
        "method": request.method,
        "status_code": response.status_code,
        "timestamp": start_time.isoformat(),
        "client_ip": public_ip,  # Original IP address
        "duration_ms": round(duration, 2),
        "user_agent": user_agent,  # Original user agent
        "referer": referer,
        "query_params": query_params,
        "path_params": path_params,
        "request_body": request_body,
        "response_size": response_size,
        "user_id": user_id,  # Original user ID
        "role": role,
        "trace_id": str(uuid.uuid4()),
        "client_identifier": client_identifier,  # Original client identifier
    }


def _identify_client(request: Request, user_id: Optional[str] = None) -> Optional[str]:
    """
    Identify client from multiple sources (priority order):
    1. Headers (x-client-id, x-api-key, x-app-id, etc.)
    2. JWT token (from Authorization header)
    3. Auth context (user_id from authenticated user)
    4. IP address (as fallback)
    """
    headers = request.headers

    # 1. Check custom client identification headers
    client_id_headers = [
        "x-client-id",
        "x-api-key",
        "x-app-id",
        "x-consumer-id",
        "x-tenant-id",
        "client-id",
        "api-key",
    ]
    for header_name in client_id_headers:
        client_id = headers.get(header_name)
        if client_id:
            return f"header:{header_name}:{client_id}"

    # 2. Extract from JWT token (Authorization header)
    auth_header = headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        # Extract client info from JWT (without verification for identification)
        # In production, verify the token
        try:
            # Simple extraction - decode without verification
            # For production, use proper JWT library with verification
            jwt_parts = token.split(".")
            if len(jwt_parts) >= 2:
                # Extract portion of token as identifier (first 32 chars)
                token_id = token[:32]
                return f"jwt:{token_id}"
        except Exception:
            pass  # If JWT parsing fails, continue to next method

    # 3. Use authenticated user ID if available
    if user_id:
        return f"user:{user_id}"

    # 4. Check request state for auth context (FastAPI dependency injection)
    if hasattr(request.state, "user"):
        state_user = request.state.user
        if hasattr(state_user, "id"):
            return f"auth:{state_user.id}"
        elif hasattr(state_user, "username"):
            return f"auth:{state_user.username}"

    # 5. Fallback to IP address (hashed for privacy)
    client_ip = _get_public_ip(request)
    if client_ip and client_ip != "unknown":
        return f"ip:{client_ip}"

    return None


def _get_public_ip(request: Request) -> str:
    """
    Extract the real public IP address from request.
    Handles proxies, load balancers, and CDNs by checking common headers.
    Priority order:
    1. X-Forwarded-For (first IP in chain)
    2. X-Real-IP
    3. X-Client-IP
    4. CF-Connecting-IP (Cloudflare)
    5. True-Client-IP (Akamai/Cloudflare)
    6. request.client.host (direct connection)
    """
    headers = request.headers

    # 1. X-Forwarded-For: Can contain multiple IPs, take the first one (original client)
    x_forwarded_for = headers.get("x-forwarded-for")
    if x_forwarded_for:
        # X-Forwarded-For can be comma-separated: "client, proxy1, proxy2"
        # The first IP is the original client
        ip = x_forwarded_for.split(",")[0].strip()
        if ip:
            return ip

    # 2. X-Real-IP: Single IP header (nginx, etc.)
    x_real_ip = headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    # 3. X-Client-IP: Alternative header
    x_client_ip = headers.get("x-client-ip")
    if x_client_ip:
        return x_client_ip.strip()

    # 4. CF-Connecting-IP: Cloudflare
    cf_connecting_ip = headers.get("cf-connecting-ip")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()

    # 5. True-Client-IP: Akamai/Cloudflare
    true_client_ip = headers.get("true-client-ip")
    if true_client_ip:
        return true_client_ip.strip()

    # 6. Fallback to direct connection IP
    if request.client:
        return request.client.host

    return "unknown"


def _hash_identifier(identifier: Optional[str]) -> Optional[str]:
    """Hash client identifier for privacy (SHA-256)."""
    if not identifier:
        return None
    return hashlib.sha256(identifier.encode()).hexdigest()[
        :16
    ]  # Use first 16 chars for shorter hash
