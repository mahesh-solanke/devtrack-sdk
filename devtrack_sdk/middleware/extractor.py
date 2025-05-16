import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import Request, Response


def extract_devtrack_log_data(
    request: Request, response: Response, start_time: datetime
) -> Dict[str, Any]:
    duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000  # in ms
    headers = request.headers

    # Capture query params and request body (optional: filter sensitive keys)
    query_params = dict(request.query_params)
    response_size = int(response.headers.get("content-length", 0))

    # Safe fallback if user-agent or referer is missing
    user_agent = headers.get("user-agent", "")
    referer = headers.get("referer", "")

    # Simulated user ID and role - replace with actual auth extraction logic
    user_id = headers.get("x-user-id")
    role = headers.get("x-user-role")

    return {
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "timestamp": start_time.isoformat(),
        "client_ip": request.client.host if request.client else "unknown",
        "duration_ms": round(duration, 2),
        "user_agent": user_agent,
        "referer": referer,
        "query_params": query_params,
        "request_body": {},  # Optional: you may add filtered body capture here
        "response_size": response_size,
        "user_id": user_id,
        "role": role,
        "trace_id": str(uuid.uuid4()),  # You can inject this into response headers too
    }
