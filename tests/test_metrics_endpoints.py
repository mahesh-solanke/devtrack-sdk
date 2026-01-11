"""
Tests for v0.4.0 metrics endpoints (traffic, errors, performance, consumers)
"""

import os
import time
import uuid

import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.database import get_db, init_db
from devtrack_sdk.middleware.base import DevTrackMiddleware


@pytest.fixture
def app_with_middleware():
    """Create a FastAPI app with DevTrack middleware for testing."""
    db_path = f"/tmp/test_devtrack_{uuid.uuid4().hex}.db"

    if os.path.exists(db_path):
        os.unlink(db_path)

    db = init_db(db_path, read_only=False)  # Write mode for middleware

    app = FastAPI()
    app.include_router(devtrack_router)
    app.add_middleware(DevTrackMiddleware, db_instance=db)

    # Store db in app state so tests can access it
    app.state.db = db
    app.state.db_path = db_path

    @app.get("/")
    async def root():
        return {"message": "Hello"}

    @app.get("/error")
    def error_route():
        raise HTTPException(status_code=404, detail="Not Found")

    @app.get("/slow")
    async def slow_route():
        time.sleep(0.1)  # Simulate slow request
        return {"message": "Slow response"}

    @app.post("/users")
    async def create_user():
        return {"id": 1, "name": "Test User"}

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        return {"user_id": user_id}

    yield app

    # Cleanup
    try:
        if hasattr(app.state, "db"):
            app.state.db.close()
        if hasattr(app.state, "db_path") and os.path.exists(app.state.db_path):
            os.unlink(app.state.db_path)
    except Exception:
        pass


def clear_db_logs(app=None):
    """Clear all logs from the database."""
    try:
        if app and hasattr(app.state, "db"):
            # Use the db instance from app state if available
            db = app.state.db
        else:
            db = get_db(read_only=False)  # Need write access to delete logs
        db.delete_all_logs()
    except Exception:
        # Database might be closed, ignore
        pass


def test_traffic_metrics_endpoint(app_with_middleware):
    """Test /__devtrack__/metrics/traffic endpoint."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # Generate some traffic
    for _ in range(5):
        client.get("/")
        time.sleep(0.01)  # Small delay to create different time buckets

    # Test traffic endpoint
    response = client.get("/__devtrack__/metrics/traffic")
    assert response.status_code == 200

    data = response.json()
    assert "traffic" in data
    assert isinstance(data["traffic"], list)

    # Should have traffic data
    if len(data["traffic"]) > 0:
        traffic_entry = data["traffic"][0]
        assert "time_bucket" in traffic_entry
        assert "request_count" in traffic_entry
        assert isinstance(traffic_entry["request_count"], int)
        assert traffic_entry["request_count"] > 0

    # Test with hours parameter
    response = client.get("/__devtrack__/metrics/traffic?hours=1")
    assert response.status_code == 200
    data = response.json()
    assert "traffic" in data


def test_error_metrics_endpoint(app_with_middleware):
    """Test /__devtrack__/metrics/errors endpoint."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # Generate some requests with errors
    client.get("/error")  # 404
    client.get("/error")  # 404
    client.get("/")  # 200

    # Test errors endpoint
    response = client.get("/__devtrack__/metrics/errors")
    assert response.status_code == 200

    data = response.json()
    assert "error_trends" in data
    assert "top_failing_routes" in data

    # Check error trends structure
    if len(data["error_trends"]) > 0:
        trend = data["error_trends"][0]
        assert "time_bucket" in trend
        assert "total_requests" in trend
        assert "error_count" in trend
        assert "error_rate" in trend
        assert isinstance(trend["error_rate"], (int, float))

    # Check top failing routes
    assert isinstance(data["top_failing_routes"], list)
    if len(data["top_failing_routes"]) > 0:
        route = data["top_failing_routes"][0]
        assert "route" in route
        assert "error_count" in route
        assert "error_rate" in route

    # Test with hours parameter
    response = client.get("/__devtrack__/metrics/errors?hours=12")
    assert response.status_code == 200


def test_performance_metrics_endpoint(app_with_middleware):
    """Test /__devtrack__/metrics/perf endpoint."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # Generate requests with varying latencies
    client.get("/")  # Fast
    client.get("/slow")  # Slow (100ms)
    client.get("/slow")  # Slow
    client.get("/")  # Fast

    # Test performance endpoint
    response = client.get("/__devtrack__/metrics/perf")
    assert response.status_code == 200

    data = response.json()
    assert "latency_over_time" in data
    assert "overall_stats" in data

    # Check overall stats structure
    overall = data["overall_stats"]
    assert "p50" in overall
    assert "p95" in overall
    assert "p99" in overall
    assert "avg" in overall

    # Check latency over time
    if len(data["latency_over_time"]) > 0:
        perf_entry = data["latency_over_time"][0]
        assert "time_bucket" in perf_entry
        assert "p50" in perf_entry
        assert "p95" in perf_entry
        assert "p99" in perf_entry
        assert "avg" in perf_entry

    # Test with hours parameter
    response = client.get("/__devtrack__/metrics/perf?hours=6")
    assert response.status_code == 200


def test_consumers_endpoint(app_with_middleware):
    """Test /__devtrack__/consumers endpoint."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # Generate requests with different user agents (to simulate different consumers)
    client.get("/", headers={"User-Agent": "Consumer1/1.0"})
    client.get("/", headers={"User-Agent": "Consumer1/1.0"})
    client.get("/users/1", headers={"User-Agent": "Consumer2/2.0"})
    client.post(
        "/users", json={"name": "Test"}, headers={"User-Agent": "Consumer2/2.0"}
    )

    # Test consumers endpoint
    response = client.get("/__devtrack__/consumers")
    assert response.status_code == 200

    data = response.json()
    assert "segments" in data
    assert isinstance(data["segments"], list)

    # Should have consumer segments
    if len(data["segments"]) > 0:
        segment = data["segments"][0]
        assert "client_identifier" in segment or "client_identifier_hash" in segment
        assert "request_count" in segment
        assert "unique_endpoints" in segment
        assert "avg_latency_ms" in segment
        assert "error_count" in segment
        assert "error_rate" in segment
        assert isinstance(segment["request_count"], int)
        assert isinstance(segment["error_rate"], (int, float))

    # Test with hours parameter
    response = client.get("/__devtrack__/consumers?hours=12")
    assert response.status_code == 200


def test_dashboard_endpoint(app_with_middleware):
    """Test /__devtrack__/dashboard endpoint."""
    client = TestClient(app_with_middleware)

    # Test dashboard endpoint
    response = client.get("/__devtrack__/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Check that HTML contains expected content
    html_content = response.text
    assert (
        "html" in html_content.lower()
        or "react" in html_content.lower()
        or "devtrack" in html_content.lower()
    )


def test_dashboard_assets_endpoint(app_with_middleware):
    """Test /__devtrack__/dashboard/assets endpoint."""
    client = TestClient(app_with_middleware)

    # Try to access a non-existent asset (should return 404)
    response = client.get("/__devtrack__/dashboard/assets/nonexistent.js")
    assert response.status_code == 404

    # If assets exist, they should be served
    # This depends on whether the dashboard is built
    # We'll just verify the endpoint exists and handles requests


def test_metrics_endpoints_with_no_data(app_with_middleware):
    """Test metrics endpoints with empty database."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # All endpoints should return empty data, not errors
    endpoints = [
        "/__devtrack__/metrics/traffic",
        "/__devtrack__/metrics/errors",
        "/__devtrack__/metrics/perf",
        "/__devtrack__/consumers",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        # Should not have error key
        assert "error" not in data or data.get("error") is None


def test_metrics_endpoints_error_handling(app_with_middleware):
    """Test metrics endpoints handle errors gracefully."""
    client = TestClient(app_with_middleware)

    # Test with invalid hours parameter (should use default)
    response = client.get("/__devtrack__/metrics/traffic?hours=invalid")
    # Should either work with default or return 422 validation error
    assert response.status_code in [200, 422]

    # Test with negative hours (should use default or validate)
    response = client.get("/__devtrack__/metrics/traffic?hours=-1")
    assert response.status_code in [200, 422]


def test_integrated_metrics_workflow(app_with_middleware):
    """Test complete workflow: generate traffic, then check all metrics."""
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    # Generate diverse traffic
    client.get("/")  # Success
    client.get("/")  # Success
    client.get("/error")  # Error
    client.get("/slow")  # Slow request
    client.post("/users", json={"name": "Test"})  # POST
    client.get("/users/1")  # GET with param

    # Wait a moment for processing
    time.sleep(0.1)

    # Check all metrics endpoints
    traffic_response = client.get("/__devtrack__/metrics/traffic")
    assert traffic_response.status_code == 200

    errors_response = client.get("/__devtrack__/metrics/errors")
    assert errors_response.status_code == 200

    perf_response = client.get("/__devtrack__/metrics/perf")
    assert perf_response.status_code == 200

    consumers_response = client.get("/__devtrack__/consumers")
    assert consumers_response.status_code == 200

    # Verify data consistency
    errors_data = errors_response.json()
    if "error_trends" in errors_data and len(errors_data["error_trends"]) > 0:
        # Should have at least one error
        total_errors = sum(
            trend.get("error_count", 0) for trend in errors_data["error_trends"]
        )
        assert total_errors >= 1  # At least one error from /error endpoint
