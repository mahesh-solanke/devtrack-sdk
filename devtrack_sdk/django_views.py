import json
import re
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .database import DevTrackDB
from .django_middleware import DevTrackDjangoMiddleware


def get_db_instance() -> DevTrackDB:
    """Get the database instance from middleware"""
    if DevTrackDjangoMiddleware._db_instance is None:
        db_path = getattr(settings, "DEVTRACK_DB_PATH", "devtrack_logs.db")
        DevTrackDjangoMiddleware._db_instance = DevTrackDB(db_path, read_only=False)
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
            entries = db.get_all_logs(limit=limit, offset=offset)

        # Get summary statistics
        stats_summary = db.get_stats_summary()

        return JsonResponse(
            {
                "summary": stats_summary,
                "total": db.get_logs_count(),
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
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


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
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


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


@require_http_methods(["GET"])
def metrics_traffic_view(request):
    """Django view for traffic metrics over time"""
    try:
        db = get_db_instance()
        hours = int(request.GET.get("hours", 24))
        traffic_data = db.get_traffic_over_time(hours=hours)
        return JsonResponse({"traffic": traffic_data})
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


@require_http_methods(["GET"])
def metrics_errors_view(request):
    """Django view for error trends and top failing routes"""
    try:
        db = get_db_instance()
        hours = int(request.GET.get("hours", 24))
        error_data = db.get_error_trends(hours=hours)
        return JsonResponse(error_data)
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


@require_http_methods(["GET"])
def metrics_perf_view(request):
    """Django view for performance metrics (p50/p95/p99 latency)"""
    try:
        db = get_db_instance()
        hours = int(request.GET.get("hours", 24))
        perf_data = db.get_performance_metrics(hours=hours)
        return JsonResponse(perf_data)
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


@require_http_methods(["GET"])
def consumers_view(request):
    """Django view for consumer segmentation data"""
    try:
        db = get_db_instance()
        hours = int(request.GET.get("hours", 24))
        segments_data = db.get_consumer_segments(hours=hours)
        return JsonResponse(segments_data)
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"[DevTrack stats_view] Error: {e}\n{error_details}")
        return JsonResponse({"error": str(e), "details": error_details}, status=500)


@require_http_methods(["GET"])
def dashboard_view(request):
    """Django view for serving the DevTrack dashboard"""
    try:
        # Check for built React app first
        # __file__ is in devtrack_sdk/django_views.py, so parent is devtrack_sdk/
        dashboard_dist = Path(__file__).parent / "dashboard" / "dist"
        dashboard_index = dashboard_dist / "index.html"

        # Fallback to old HTML if built version doesn't exist
        if not dashboard_index.exists():
            dashboard_path = Path(__file__).parent / "dashboard" / "index.html"
            if not dashboard_path.exists():
                return HttpResponse(
                    "Dashboard file not found", status=404, content_type="text/plain"
                )

            # Read the HTML content
            html_content = dashboard_path.read_text(encoding="utf-8")

            # Replace the hardcoded API URL with a dynamic one based on the request
            base_url = request.build_absolute_uri("/").rstrip("/")
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

            return HttpResponse(html_content, content_type="text/html")

        # Serve built React app
        html_content = dashboard_index.read_text(encoding="utf-8")

        # Inject API URLs into the HTML
        base_url = request.build_absolute_uri("/").rstrip("/")
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

        # Rewrite asset paths to use Django static files or direct path
        html_content = re.sub(
            r'(href|src)=["\'](\.\/)?assets\/([^"\']+)["\']',
            r'\1="/__devtrack__/dashboard/assets/\3"',
            html_content,
        )

        return HttpResponse(html_content, content_type="text/html")
    except Exception as e:
        return HttpResponse(
            f"Failed to load dashboard: {str(e)}", status=500, content_type="text/plain"
        )


@require_http_methods(["GET"])
def dashboard_assets_view(request, file_path):
    """Django view for serving dashboard static assets"""
    try:
        from django.http import FileResponse

        # __file__ is in devtrack_sdk/django_views.py, so parent is devtrack_sdk/
        dashboard_dist = Path(__file__).parent / "dashboard" / "dist" / "assets"
        asset_path = dashboard_dist / file_path

        if not asset_path.exists() or not str(asset_path).startswith(
            str(dashboard_dist)
        ):
            return HttpResponse(
                "Asset not found", status=404, content_type="text/plain"
            )

        return FileResponse(open(asset_path, "rb"))
    except Exception as e:
        return HttpResponse(
            f"Failed to load asset: {str(e)}", status=500, content_type="text/plain"
        )
