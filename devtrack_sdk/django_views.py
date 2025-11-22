import json

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .database import DevTrackDB
from .django_middleware import DevTrackDjangoMiddleware


def get_db_instance() -> DevTrackDB:
    """Get the database instance from middleware"""
    if DevTrackDjangoMiddleware._db_instance is None:
        db_path = getattr(settings, "DEVTRACK_DB_PATH", "devtrack_logs.db")
        DevTrackDjangoMiddleware._db_instance = DevTrackDB(db_path)
    return DevTrackDjangoMiddleware._db_instance


@csrf_exempt
@require_http_methods(["POST"])
def track_view(request):
    """Django view for manual log tracking"""
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
        if data and not data.get("error"):
            db = get_db_instance()
            db.insert_log(data)
            return JsonResponse({"ok": True, "message": "Log tracked successfully"})
        else:
            return JsonResponse({"ok": False, "error": "Invalid data"}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def stats_view(request):
    """Django view for retrieving statistics from DuckDB"""
    try:
        db = get_db_instance()

        # Get query parameters
        # Default to None (no limit) to return all records, or use provided limit
        limit_str = request.GET.get("limit")
        limit = int(limit_str) if limit_str else None
        offset = int(request.GET.get("offset", 0))
        path_pattern = request.GET.get("path_pattern")
        status_code = request.GET.get("status_code")

        # Get logs based on filters
        if path_pattern:
            entries = db.get_logs_by_path(path_pattern, limit=limit)
        elif status_code:
            entries = db.get_logs_by_status_code(int(status_code), limit=limit)
        else:
            entries = db.get_all_logs(limit=limit)

        # Get summary statistics
        stats_summary = db.get_stats_summary()

        return JsonResponse(
            {
                "summary": stats_summary,
                "total": len(entries),
                "entries": entries,
                "filters": {
                    "limit": limit,
                    "offset": offset,
                    "path_pattern": path_pattern,
                    "status_code": status_code,
                },
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_logs_view(request):
    """Django view for deleting logs"""
    try:
        db = get_db_instance()

        # Get query parameters
        all_logs = request.GET.get("all_logs", "false").lower() == "true"
        path_pattern = request.GET.get("path_pattern")
        status_code = request.GET.get("status_code")
        older_than_days = request.GET.get("older_than_days")
        log_ids = request.GET.get("log_ids")

        deleted_count = 0

        if all_logs:
            deleted_count = db.delete_all_logs()
        elif path_pattern:
            deleted_count = db.delete_logs_by_path(path_pattern)
        elif status_code:
            deleted_count = db.delete_logs_by_status_code(int(status_code))
        elif older_than_days:
            deleted_count = db.delete_logs_older_than(int(older_than_days))
        elif log_ids:
            # Parse comma-separated log IDs
            ids = [int(id.strip()) for id in log_ids.split(",") if id.strip()]
            deleted_count = sum(db.delete_logs_by_id(log_id) for log_id in ids)
        else:
            return JsonResponse({"error": "No deletion criteria specified"}, status=400)

        return JsonResponse(
            {
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
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class DevTrackView(View):
    """Class-based view for DevTrack endpoints"""

    def get(self, request, *args, **kwargs):
        """Handle GET requests for stats"""
        return stats_view(request)

    def post(self, request, *args, **kwargs):
        """Handle POST requests for tracking"""
        return track_view(request)

    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests for log deletion"""
        return delete_logs_view(request)
