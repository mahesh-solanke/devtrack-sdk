from django.urls import path

from .django_views import DevTrackView, delete_logs_view, stats_view, track_view

# URL patterns for DevTrack Django integration
devtrack_urlpatterns = [
    path("__devtrack__/track", track_view, name="devtrack_track"),
    path("__devtrack__/stats", stats_view, name="devtrack_stats"),
    path("__devtrack__/logs", delete_logs_view, name="devtrack_delete_logs"),
]

# Alternative using class-based view
devtrack_cbv_urlpatterns = [
    path("__devtrack__/", DevTrackView.as_view(), name="devtrack_view"),
]
