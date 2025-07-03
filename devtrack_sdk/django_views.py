import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .django_middleware import DevTrackDjangoMiddleware


@csrf_exempt
@require_http_methods(["POST"])
def track_view(request):
    """Django view equivalent to FastAPI track endpoint"""
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        data = {"error": "Invalid JSON"}

    DevTrackDjangoMiddleware.stats.append(data)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def stats_view(request):
    """Django view equivalent to FastAPI stats endpoint"""
    return JsonResponse(
        {
            "total": len(DevTrackDjangoMiddleware.stats),
            "entries": DevTrackDjangoMiddleware.stats,
        }
    )


class DevTrackView(View):
    """Class-based view for DevTrack endpoints"""

    def get(self, request, *args, **kwargs):
        """Handle GET requests for stats"""
        return stats_view(request)

    def post(self, request, *args, **kwargs):
        """Handle POST requests for tracking"""
        return track_view(request)
