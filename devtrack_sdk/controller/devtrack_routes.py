import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse

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
    db = get_db(read_only=True)

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
    db = get_db(read_only=False)

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
    db = get_db(read_only=False)

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
    db = get_db(read_only=True)
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
    db = get_db(read_only=True)
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
    db = get_db(read_only=True)
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
    db = get_db(read_only=True)
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
        # Check for built React app first
        dashboard_dist = Path(__file__).parent.parent / "dashboard" / "dist"
        dashboard_index = dashboard_dist / "index.html"

        # Fallback to old HTML if built version doesn't exist
        if not dashboard_index.exists():
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
            perf_url_old = (
                "const PERF_API_URL = "
                '"http://localhost:8000/__devtrack__/metrics/perf";'
            )
            perf_url_new = (
                f'const PERF_API_URL = "{base_url}/__devtrack__/metrics/perf";'
            )
            html_content = html_content.replace(perf_url_old, perf_url_new)
            consumers_url_old = (
                "const CONSUMERS_API_URL = "
                '"http://localhost:8000/__devtrack__/consumers";'
            )
            consumers_url_new = (
                f'const CONSUMERS_API_URL = "{base_url}/__devtrack__/consumers";'
            )
            html_content = html_content.replace(consumers_url_old, consumers_url_new)

            return HTMLResponse(content=html_content)

        # Serve built React app
        html_content = dashboard_index.read_text(encoding="utf-8")

        # Inject API URLs into the HTML
        base_url = str(request.base_url).rstrip("/")
        api_url = f"{base_url}/__devtrack__/stats"
        traffic_url = f"{base_url}/__devtrack__/metrics/traffic"
        errors_url = f"{base_url}/__devtrack__/metrics/errors"
        perf_url = f"{base_url}/__devtrack__/metrics/perf"
        consumers_url = f"{base_url}/__devtrack__/consumers"

        # Replace API URL placeholders
        html_content = html_content.replace(
            "window.API_URL = window.API_URL || '/__devtrack__/stats';",
            f"window.API_URL = '{api_url}';",
        )
        traffic_placeholder = (
            "window.TRAFFIC_API_URL = window.TRAFFIC_API_URL || "
            "'/__devtrack__/metrics/traffic';"
        )
        html_content = html_content.replace(
            traffic_placeholder, f"window.TRAFFIC_API_URL = '{traffic_url}';"
        )
        errors_placeholder = (
            "window.ERRORS_API_URL = window.ERRORS_API_URL || "
            "'/__devtrack__/metrics/errors';"
        )
        html_content = html_content.replace(
            errors_placeholder, f"window.ERRORS_API_URL = '{errors_url}';"
        )
        perf_placeholder = (
            "window.PERF_API_URL = window.PERF_API_URL || "
            "'/__devtrack__/metrics/perf';"
        )
        html_content = html_content.replace(
            perf_placeholder, f"window.PERF_API_URL = '{perf_url}';"
        )
        consumers_placeholder = (
            "window.CONSUMERS_API_URL = window.CONSUMERS_API_URL || "
            "'/__devtrack__/consumers';"
        )
        html_content = html_content.replace(
            consumers_placeholder, f"window.CONSUMERS_API_URL = '{consumers_url}';"
        )

        # Rewrite asset paths to use FastAPI route
        # Vite builds with relative paths (./assets/...) when base is './'
        html_content = re.sub(
            r'(href|src)=["\'](\.\/)?assets\/([^"\']+)["\']',
            r'\1="/__devtrack__/dashboard/assets/\3"',
            html_content,
        )

        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load dashboard: {str(e)}"
        )


@router.get("/__devtrack__/dashboard/assets/{file_path:path}", include_in_schema=False)
async def dashboard_assets(file_path: str):
    """Serve static assets from the built React dashboard."""
    dashboard_dist = Path(__file__).parent.parent / "dashboard" / "dist" / "assets"
    asset_path = dashboard_dist / file_path

    if not asset_path.exists() or not str(asset_path).startswith(str(dashboard_dist)):
        raise HTTPException(status_code=404, detail="Asset not found")

    return FileResponse(asset_path)
