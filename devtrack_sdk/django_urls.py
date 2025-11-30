from django.urls import path

from .django_views import (
    DevTrackView,
    consumers_view,
    dashboard_assets_view,
    dashboard_view,
    delete_logs_view,
    metrics_errors_view,
    metrics_perf_view,
    metrics_traffic_view,
    stats_view,
    track_view,
)

# URL patterns for DevTrack Django integration
devtrack_urlpatterns = [
    path("__devtrack__/track", track_view, name="devtrack_track"),
    path("__devtrack__/stats", stats_view, name="devtrack_stats"),
    path("__devtrack__/logs", delete_logs_view, name="devtrack_delete_logs"),
    path(
        "__devtrack__/metrics/traffic",
        metrics_traffic_view,
        name="devtrack_metrics_traffic",
    ),
    path(
        "__devtrack__/metrics/errors",
        metrics_errors_view,
        name="devtrack_metrics_errors",
    ),
    path(
        "__devtrack__/metrics/perf",
        metrics_perf_view,
        name="devtrack_metrics_perf",
    ),
    path("__devtrack__/consumers", consumers_view, name="devtrack_consumers"),
    path("__devtrack__/dashboard", dashboard_view, name="devtrack_dashboard"),
    path(
        "__devtrack__/dashboard/assets/<path:file_path>",
        dashboard_assets_view,
        name="devtrack_dashboard_assets",
    ),
]

# Alternative using class-based view
devtrack_cbv_urlpatterns = [
    path("__devtrack__/", DevTrackView.as_view(), name="devtrack_view"),
]
