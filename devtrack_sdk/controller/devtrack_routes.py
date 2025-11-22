from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from devtrack_sdk.database import get_db

router = APIRouter()


@router.get("/__devtrack__/stats", include_in_schema=False)
async def stats(
    limit: Optional[int] = Query(None, description="Limit number of entries returned"),
    offset: int = Query(0, description="Offset for pagination"),
    path_pattern: Optional[str] = Query(None, description="Filter by path pattern"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
):
    """Get DevTrack statistics and logs from DuckDB."""
    db = get_db()

    try:
        # Get summary stats
        summary = db.get_stats_summary()

        # Get logs based on filters
        if path_pattern:
            entries = db.get_logs_by_path(path_pattern, limit)
        elif status_code:
            entries = db.get_logs_by_status_code(status_code, limit)
        else:
            entries = db.get_all_logs(limit, offset)

        return {
            "summary": summary,
            "total": db.get_logs_count(),
            "entries": entries,
            "filters": {
                "limit": limit,
                "offset": offset,
                "path_pattern": path_pattern,
                "status_code": status_code,
            },
        }
    except Exception as e:
        return {"error": f"Failed to retrieve stats: {str(e)}"}


@router.delete("/__devtrack__/logs", include_in_schema=False)
async def delete_logs(
    all_logs: bool = Query(False, description="Delete all logs"),
    path_pattern: Optional[str] = Query(
        None, description="Delete logs by path pattern"
    ),
    status_code: Optional[int] = Query(None, description="Delete logs by status code"),
    older_than_days: Optional[int] = Query(
        None, description="Delete logs older than N days"
    ),
    log_ids: Optional[str] = Query(
        None, description="Comma-separated list of log IDs to delete"
    ),
):
    """Delete logs from the database with various filtering options."""
    db = get_db()

    try:
        deleted_count = 0

        if all_logs:
            deleted_count = db.delete_all_logs()
        elif path_pattern:
            deleted_count = db.delete_logs_by_path(path_pattern)
        elif status_code:
            deleted_count = db.delete_logs_by_status_code(status_code)
        elif older_than_days:
            deleted_count = db.delete_logs_older_than(older_than_days)
        elif log_ids:
            # Parse comma-separated IDs
            try:
                ids = [int(id.strip()) for id in log_ids.split(",") if id.strip()]
                deleted_count = db.delete_logs_by_ids(ids)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid log IDs format")
        else:
            raise HTTPException(status_code=400, detail="No deletion criteria provided")

        return {
            "message": f"Successfully deleted {deleted_count} log entries",
            "deleted_count": deleted_count,
            "criteria": {
                "all_logs": all_logs,
                "path_pattern": path_pattern,
                "status_code": status_code,
                "older_than_days": older_than_days,
                "log_ids": log_ids,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logs: {str(e)}")


@router.delete("/__devtrack__/logs/{log_id}", include_in_schema=False)
async def delete_log_by_id(log_id: int):
    """Delete a specific log by its ID."""
    db = get_db()

    try:
        deleted_count = db.delete_logs_by_id(log_id)

        if deleted_count == 0:
            return {
                "message": f"No log found with ID {log_id}",
                "deleted_count": 0,
                "log_id": log_id,
            }

        return {
            "message": f"Successfully deleted log with ID {log_id}",
            "deleted_count": deleted_count,
            "log_id": log_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete log: {str(e)}")


@router.get("/__devtrack__/metrics/traffic", include_in_schema=False)
async def metrics_traffic(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get traffic metrics over time."""
    db = get_db()
    try:
        traffic_data = db.get_traffic_over_time(hours=hours)
        return {"traffic": traffic_data}
    except Exception as e:
        return {"error": f"Failed to retrieve traffic metrics: {str(e)}"}


@router.get("/__devtrack__/metrics/errors", include_in_schema=False)
async def metrics_errors(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get error trends and top failing routes."""
    db = get_db()
    try:
        error_data = db.get_error_trends(hours=hours)
        return error_data
    except Exception as e:
        return {"error": f"Failed to retrieve error metrics: {str(e)}"}


@router.get("/__devtrack__/metrics/perf", include_in_schema=False)
async def metrics_perf(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get performance metrics (p50/p95/p99 latency)."""
    db = get_db()
    try:
        perf_data = db.get_performance_metrics(hours=hours)
        return perf_data
    except Exception as e:
        return {"error": f"Failed to retrieve performance metrics: {str(e)}"}


@router.get("/__devtrack__/consumers", include_in_schema=False)
async def consumers(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get consumer segmentation data."""
    db = get_db()
    try:
        segments_data = db.get_consumer_segments(hours=hours)
        return segments_data
    except Exception as e:
        return {"error": f"Failed to retrieve consumer segments: {str(e)}"}


@router.get(
    "/__devtrack__/dashboard", include_in_schema=False, response_class=HTMLResponse
)
async def dashboard(request: Request):
    """Serve the DevTrack dashboard HTML page."""
    try:
        # Get the path to the dashboard HTML file
        dashboard_path = Path(__file__).parent.parent / "dashboard" / "index.html"

        if not dashboard_path.exists():
            raise HTTPException(status_code=404, detail="Dashboard file not found")

        # Read the HTML content
        html_content = dashboard_path.read_text(encoding="utf-8")

        # Replace the hardcoded API URL with a dynamic one based on the request
        base_url = str(request.base_url).rstrip("/")
        api_url = f"{base_url}/__devtrack__/stats"
        html_content = html_content.replace(
            'const API_URL = "http://localhost:8000/__devtrack__/stats";',
            f'const API_URL = "{api_url}";',
        )

        # Replace metrics API URLs
        traffic_url_old = (
            "const TRAFFIC_API_URL = "
            '"http://localhost:8000/__devtrack__/metrics/traffic";'
        )
        traffic_url_new = (
            f'const TRAFFIC_API_URL = "{base_url}/__devtrack__/metrics/traffic";'
        )
        html_content = html_content.replace(traffic_url_old, traffic_url_new)

        errors_url_old = (
            "const ERRORS_API_URL = "
            '"http://localhost:8000/__devtrack__/metrics/errors";'
        )
        errors_url_new = (
            f'const ERRORS_API_URL = "{base_url}/__devtrack__/metrics/errors";'
        )
        html_content = html_content.replace(errors_url_old, errors_url_new)
        html_content = html_content.replace(
            'const PERF_API_URL = "http://localhost:8000/__devtrack__/metrics/perf";',
            f'const PERF_API_URL = "{base_url}/__devtrack__/metrics/perf";',
        )
        html_content = html_content.replace(
            'const CONSUMERS_API_URL = "http://localhost:8000/__devtrack__/consumers";',
            f'const CONSUMERS_API_URL = "{base_url}/__devtrack__/consumers";',
        )

        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load dashboard: {str(e)}"
        )
