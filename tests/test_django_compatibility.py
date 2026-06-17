"""
Compatibility tests for supported Django versions.
"""

import os
from datetime import datetime, timezone

import django
from django import VERSION as DJANGO_VERSION
from django.apps import apps
from django.conf import settings
from django.test import RequestFactory

from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware
from devtrack_sdk.django_urls import devtrack_urlpatterns
from devtrack_sdk.django_views import stats_view

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
if not apps.ready:
    django.setup()


def test_django_runtime_is_in_supported_ci_matrix():
    """Verify CI exercises the declared supported Django versions."""
    assert DJANGO_VERSION[:2] in {(4, 2), (5, 2)}


def test_django_52_middleware_and_urls_load_with_configured_settings():
    """Verify Django 5.2 can load DevTrack middleware, views, and URL patterns."""
    assert settings.configured
    assert DevTrackDjangoMiddleware.__module__ == "devtrack_sdk.django_middleware"
    assert callable(stats_view)
    assert {pattern.name for pattern in devtrack_urlpatterns} >= {
        "devtrack_track",
        "devtrack_stats",
        "devtrack_dashboard",
    }


def test_django_52_request_factory_extracts_request_data(tmp_path):
    """Verify request metadata extraction works with Django 5.2 request objects."""
    db_path = str(tmp_path / "devtrack_django_52.db")
    middleware = DevTrackDjangoMiddleware(lambda request: None, db_path=db_path)
    try:
        request = RequestFactory().get(
            "/api/widgets?limit=10", HTTP_USER_AGENT="pytest"
        )
        response = type("Response", (), {"status_code": 200, "content": b"ok"})()

        log_data = middleware._extract_devtrack_log_data(
            request, response, datetime.now(timezone.utc)
        )

        assert log_data["path"] == "/api/widgets"
        assert log_data["method"] == "GET"
        assert log_data["status_code"] == 200
        assert log_data["query_params"] == {"limit": ["10"]}
        assert log_data["user_agent"] == "pytest"
    finally:
        if DevTrackDjangoMiddleware._db_instance is not None:
            DevTrackDjangoMiddleware._db_instance.close()
            DevTrackDjangoMiddleware._db_instance = None
