"""
Tests for Django integration
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

# Import Django components
from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware
from devtrack_sdk.django_urls import devtrack_urlpatterns
from devtrack_sdk.django_views import stats_view, track_view

# Configure Django settings for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")


class DevTrackDjangoMiddlewareTest(TestCase):
    """Test Django middleware functionality"""

    def setUp(self):
        self.factory = RequestFactory()
        # Create a mock get_response function
        self.mock_get_response = Mock()
        # Use a temporary database file to avoid lock conflicts
        self.temp_db = tempfile.mktemp(suffix=".db")
        # Reset the middleware's database instance to use temp file
        if DevTrackDjangoMiddleware._db_instance is not None:
            DevTrackDjangoMiddleware._db_instance.close()
        DevTrackDjangoMiddleware._db_instance = None
        # Create middleware with temp database path
        self.middleware = DevTrackDjangoMiddleware(
            self.mock_get_response, db_path=self.temp_db
        )

    def tearDown(self):
        """Clean up temporary database file"""
        # Close and clean up database instance
        if DevTrackDjangoMiddleware._db_instance:
            DevTrackDjangoMiddleware._db_instance.close()
            DevTrackDjangoMiddleware._db_instance = None
        # Remove temp file if it exists
        if os.path.exists(self.temp_db):
            try:
                os.unlink(self.temp_db)
            except OSError:
                pass

    def test_middleware_initialization(self):
        """Test middleware initializes correctly"""
        self.assertIsNotNone(self.middleware)
        self.assertIn("/__devtrack__/stats", self.middleware.skip_paths)
        self.assertIn("/admin/", self.middleware.skip_paths)

    def test_skip_paths_work(self):
        """Test that skip paths are properly excluded"""
        request = self.factory.get("/__devtrack__/stats")
        mock_response = Mock()
        self.mock_get_response.return_value = mock_response

        # Should not track this path
        with patch.object(
            self.middleware, "_extract_devtrack_log_data"
        ) as mock_extract:
            self.middleware(request)
            mock_extract.assert_not_called()
            self.mock_get_response.assert_called_once_with(request)

    def test_tracks_normal_requests(self):
        """Test that normal requests are tracked"""
        request = self.factory.get("/api/test")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test"
        self.mock_get_response.return_value = mock_response

        with patch.object(
            self.middleware, "_extract_devtrack_log_data"
        ) as mock_extract:
            self.middleware(request)
            mock_extract.assert_called_once()
            self.mock_get_response.assert_called_once_with(request)

    def test_extract_log_data(self):
        """Test data extraction from request/response"""
        request = self.factory.post(
            "/api/test",
            data=json.dumps({"test": "data"}),
            content_type="application/json",
        )
        request.META["HTTP_USER_AGENT"] = "test-agent"
        request.META["HTTP_REFERER"] = "http://test.com"

        response = Mock()
        response.status_code = 200
        response.content = b"response"

        # Use a real datetime for start_time
        start_time = datetime.now(timezone.utc)

        log_data = self.middleware._extract_devtrack_log_data(
            request, response, start_time
        )

        self.assertEqual(log_data["path"], "/api/test")
        self.assertEqual(log_data["method"], "POST")
        self.assertEqual(log_data["status_code"], 200)
        self.assertEqual(log_data["user_agent"], "test-agent")
        self.assertEqual(log_data["referer"], "http://test.com")
        self.assertIn("trace_id", log_data)

    def test_custom_exclude_paths(self):
        """Test custom exclude paths functionality"""
        # Use the same temp database for consistency
        custom_middleware = DevTrackDjangoMiddleware(
            self.mock_get_response,
            exclude_path=["/custom/path/"],
            db_path=self.temp_db,
        )
        self.assertIn("/custom/path/", custom_middleware.skip_paths)


class DevTrackDjangoViewsTest(TestCase):
    """Test Django views functionality"""

    def setUp(self):
        self.factory = RequestFactory()
        # Clear database before each test to avoid test data interference
        # Ensure database instance exists and is in write mode
        if DevTrackDjangoMiddleware._db_instance is None:
            import tempfile

            from devtrack_sdk.database import DevTrackDB

            db_path = tempfile.mktemp(suffix=".db")
            DevTrackDjangoMiddleware._db_instance = DevTrackDB(db_path, read_only=False)
        # Ensure it's not read-only (recreate if needed)
        if DevTrackDjangoMiddleware._db_instance.read_only:
            db_path = DevTrackDjangoMiddleware._db_instance.db_path
            DevTrackDjangoMiddleware._db_instance.close()
            from devtrack_sdk.database import DevTrackDB

            DevTrackDjangoMiddleware._db_instance = DevTrackDB(db_path, read_only=False)
        DevTrackDjangoMiddleware._db_instance.delete_all_logs()

    def test_stats_view(self):
        """Test stats view returns correct format"""
        request = self.factory.get("/__devtrack__/stats")
        response = stats_view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("total", data)
        self.assertIn("entries", data)

    def test_track_view(self):
        """Test track view accepts data"""
        test_data = {
            "path": "/api/test",
            "path_pattern": "/api/test",
            "method": "POST",
            "status_code": 200,
            "timestamp": "2024-01-01T00:00:00Z",
            "duration_ms": 100.0,
            "client_ip": "127.0.0.1",
            "user_agent": "test-agent",
            "referer": "",
            "query_params": {},
            "path_params": {},
            "request_body": {},
            "response_size": 0,
            "user_id": None,
            "role": None,
            "trace_id": "test-trace-id",
        }
        request = self.factory.post(
            "/__devtrack__/track",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        response = track_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["ok"], True)

        # Check that data was added to stats
        stats_request = self.factory.get("/__devtrack__/stats")
        stats_response = stats_view(stats_request)
        stats_data = json.loads(stats_response.content)
        entries = stats_data["entries"]
        self.assertGreater(len(entries), 0, "No entries found in stats")
        # Verify the test data fields are present in at least one entry
        # Database adds id and created_at, so we check core fields
        found = False
        for entry in entries:
            # Check key fields that should match
            if (
                entry.get("path") == test_data["path"]
                and entry.get("path_pattern") == test_data["path_pattern"]
                and entry.get("method") == test_data["method"]
                and entry.get("status_code") == test_data["status_code"]
                and abs(entry.get("duration_ms", 0) - test_data["duration_ms"]) < 0.01
            ):
                found = True
                break
        self.assertTrue(found, "Test data not found in stats entries")

    def test_track_view_invalid_json(self):
        """Test track view handles invalid JSON"""
        request = self.factory.post(
            "/__devtrack__/track", data="invalid json", content_type="application/json"
        )

        response = track_view(request)
        # Invalid JSON should result in an error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data["ok"], False)
        self.assertIn("error", data)


class DevTrackDjangoURLsTest(TestCase):
    """Test Django URL patterns"""

    def test_url_patterns_exist(self):
        """Test that URL patterns are properly defined"""
        self.assertTrue(len(devtrack_urlpatterns) > 0)

        # Check for expected URL patterns
        url_names = [pattern.name for pattern in devtrack_urlpatterns]
        self.assertIn("devtrack_track", url_names)
        self.assertIn("devtrack_stats", url_names)

    def test_url_patterns_paths(self):
        """Test that URL patterns have correct paths"""
        paths = [pattern.pattern.regex.pattern for pattern in devtrack_urlpatterns]
        self.assertIn(r"^__devtrack__/track\Z", paths)
        self.assertIn(r"^__devtrack__/stats\Z", paths)
