from typing import Optional

from fastapi import APIRouter, HTTPException, Query

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
