import os

import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.database import get_db, init_db
from devtrack_sdk.middleware.base import DevTrackMiddleware


def clear_db_logs(app=None):
    """Clear all logs from the database for testing."""
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


@pytest.fixture
def app_with_middleware():
    # Create a unique temporary database for testing
    import uuid

    from devtrack_sdk.database import _thread_local

    db_path = f"/tmp/test_devtrack_{uuid.uuid4().hex}.db"

    # Ensure the file doesn't exist
    if os.path.exists(db_path):
        os.unlink(db_path)

    # Initialize database with temporary file (write mode for middleware)
    db = init_db(db_path, read_only=False)

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
        raise HTTPException(status_code=400, detail="Bad Request")

    @app.post("/users")
    async def create_user():
        return {"id": 1, "name": "Test User"}

    @app.get("/users/{user_id}/profile")
    async def user_profile(user_id: int):
        return {"user_id": user_id, "profile": "test"}

    yield app

    # Cleanup - close thread-local connections
    try:
        # Clear thread-local connection
        if (
            hasattr(_thread_local, "connection")
            and _thread_local.connection is not None
        ):
            try:
                _thread_local.connection.close()
            except Exception:
                pass
            _thread_local.connection = None

        if os.path.exists(db_path):
            os.unlink(db_path)
    except Exception:
        pass


def test_root_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs(app_with_middleware)

    response = client.get("/")
    assert response.status_code == 200

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 1
    log_entry = logs[0]
    assert log_entry["path"] == "/"
    assert log_entry["method"] == "GET"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert log_entry["status_code"] == 200
    assert isinstance(log_entry["duration_ms"], (int, float))
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_error_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    response = client.get("/error")
    assert response.status_code == 400

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 1
    log_entry = logs[0]
    assert log_entry["status_code"] == 400
    assert log_entry["path"] == "/error"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert isinstance(log_entry["duration_ms"], (int, float))
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_post_request_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    response = client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 1
    log_entry = logs[0]
    assert log_entry["method"] == "POST"
    assert log_entry["path"] == "/users"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert log_entry["status_code"] == 200
    assert isinstance(log_entry["duration_ms"], (int, float))
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_internal_stats_endpoint(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Make multiple requests
    client.get("/")
    client.post("/users", json={"name": "Test User"})
    client.get("/error")

    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert body["total"] == 3
    assert "entries" in body
    assert isinstance(body["entries"], list)
    assert len(body["entries"]) == 3

    # Verify entries contain all required fields
    for entry in body["entries"]:
        assert "path" in entry
        assert "method" in entry
        assert "status_code" in entry
        assert "timestamp" in entry
        assert "duration_ms" in entry
        assert "client_ip" in entry
        assert isinstance(entry["duration_ms"], (int, float))
        assert isinstance(entry["timestamp"], str)
        assert isinstance(entry["client_ip"], str)


def test_excluded_paths_not_logged(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # These paths should be excluded from logging
    client.get("/docs")
    client.get("/redoc")
    client.get("/openapi.json")

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 0

    # Test that a non-excluded path is logged
    client.get("/")
    logs = db.get_all_logs()
    assert len(logs) == 1
    assert logs[0]["path"] == "/"
    assert isinstance(logs[0]["duration_ms"], (int, float))
    assert isinstance(logs[0]["timestamp"], str)
    assert isinstance(logs[0]["client_ip"], str)


def test_path_pattern_normalization(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Test with a path that has parameters
    response = client.get("/users/123/profile")
    assert response.status_code == 200

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 1
    log_entry = logs[0]

    # Check both original path and normalized path pattern
    assert log_entry["path"] == "/users/123/profile"
    assert log_entry["path_pattern"] == "/users/{user_id}/profile"
    assert log_entry["path_params"] == {"user_id": "123"}

    # Test with a simple path
    response = client.get("/")
    assert response.status_code == 200
    logs = db.get_all_logs()
    assert len(logs) == 2
    log_entry = logs[0]  # Most recent log is first in the list

    # Simple paths should have the same path and pattern
    assert log_entry["path"] == "/"
    assert log_entry["path_pattern"] == "/"
    assert log_entry["path_params"] == {}


def test_middleware_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Test successful request
    response = client.get("/")
    assert response.status_code == 200

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 1
    assert logs[0]["status_code"] == 200
    assert logs[0]["method"] == "GET"
    assert logs[0]["path"] == "/"
    assert logs[0]["path_pattern"] == "/"
    assert logs[0]["path_params"] == {}
    assert logs[0]["duration_ms"] > 0
    assert isinstance(logs[0]["timestamp"], str)
    assert isinstance(logs[0]["client_ip"], str)

    # Test error request
    response = client.get("/error")
    assert response.status_code == 400
    logs = db.get_all_logs()
    assert len(logs) == 2
    assert logs[0]["status_code"] == 400  # Most recent first
    assert logs[0]["method"] == "GET"
    assert logs[0]["path"] == "/error"
    assert logs[0]["path_pattern"] == "/error"
    assert logs[0]["path_params"] == {}
    assert logs[0]["duration_ms"] > 0
    assert isinstance(logs[0]["timestamp"], str)
    assert isinstance(logs[0]["client_ip"], str)

    # Test POST request
    response = client.post("/users")
    assert response.status_code == 200
    logs = db.get_all_logs()
    assert len(logs) == 3
    assert logs[0]["status_code"] == 200  # Most recent first
    assert logs[0]["method"] == "POST"
    assert logs[0]["path"] == "/users"
    assert logs[0]["path_pattern"] == "/users"
    assert logs[0]["path_params"] == {}
    assert logs[0]["duration_ms"] > 0
    assert isinstance(logs[0]["timestamp"], str)
    assert isinstance(logs[0]["client_ip"], str)


def test_delete_all_logs(app_with_middleware):
    """Test deleting all logs."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")
    client.post("/users", json={"name": "Test User"})
    client.get("/error")

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 3

    # Delete all logs
    response = client.delete("/__devtrack__/logs?all_logs=true")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 3
    assert "Successfully deleted 3 log entries" in data["message"]

    # Verify logs are deleted
    logs = db.get_all_logs()
    assert len(logs) == 0


def test_delete_logs_by_status_code(app_with_middleware):
    """Test deleting logs by status code."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")  # 200
    client.post("/users", json={"name": "Test User"})  # 200
    client.get("/error")  # 400

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 3

    # Delete only error logs (400)
    response = client.delete("/__devtrack__/logs?status_code=400")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 1

    # Verify only error logs are deleted
    logs = db.get_all_logs()
    assert len(logs) == 2
    for log in logs:
        assert log["status_code"] != 400


def test_delete_logs_by_path_pattern(app_with_middleware):
    """Test deleting logs by path pattern."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")
    client.post("/users", json={"name": "Test User"})
    client.get("/users/123/profile")

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 3

    # Delete logs for user profile pattern
    response = client.delete("/__devtrack__/logs?path_pattern=/users/{user_id}/profile")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 1

    # Verify only user profile logs are deleted
    logs = db.get_all_logs()
    assert len(logs) == 2
    for log in logs:
        assert log["path_pattern"] != "/users/{user_id}/profile"


def test_delete_log_by_id(app_with_middleware):
    """Test deleting a specific log by ID."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")
    client.post("/users", json={"name": "Test User"})

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 2

    # Get the ID of the first log
    log_id = logs[1]["id"]  # Older log (second in list)

    # Delete specific log by ID
    response = client.delete(f"/__devtrack__/logs/{log_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 1
    assert data["log_id"] == log_id

    # Verify only that log is deleted
    logs = db.get_all_logs()
    assert len(logs) == 1
    assert logs[0]["id"] != log_id


def test_delete_logs_by_ids(app_with_middleware):
    """Test deleting multiple logs by IDs."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")
    client.post("/users", json={"name": "Test User"})
    client.get("/error")

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 3

    # Get IDs of first two logs
    log_ids = [logs[2]["id"], logs[1]["id"]]  # Two older logs
    log_ids_str = ",".join(map(str, log_ids))

    # Delete specific logs by IDs
    response = client.delete(f"/__devtrack__/logs?log_ids={log_ids_str}")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 2

    # Verify only those logs are deleted
    logs = db.get_all_logs()
    assert len(logs) == 1
    assert logs[0]["id"] not in log_ids


def test_delete_logs_older_than(app_with_middleware):
    """Test deleting logs older than specified days."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Add some logs
    client.get("/")
    client.post("/users", json={"name": "Test User"})

    # Use the same db instance that middleware uses
    db = app_with_middleware.state.db
    logs = db.get_all_logs()
    assert len(logs) == 2

    # Delete logs older than 365 days (should delete none since logs are fresh)
    response = client.delete("/__devtrack__/logs?older_than_days=365")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 0

    # Verify no logs are deleted
    logs = db.get_all_logs()
    assert len(logs) == 2


def test_delete_log_not_found(app_with_middleware):
    """Test deleting a non-existent log."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Try to delete a non-existent log
    response = client.delete("/__devtrack__/logs/99999")
    assert response.status_code == 200

    data = response.json()
    assert data["deleted_count"] == 0
    assert "No log found with ID 99999" in data["message"]


def test_delete_logs_no_criteria(app_with_middleware):
    """Test deleting logs without providing criteria."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Try to delete without criteria
    response = client.delete("/__devtrack__/logs")
    assert response.status_code == 400

    data = response.json()
    assert "No deletion criteria provided" in data["detail"]


def test_delete_logs_invalid_ids(app_with_middleware):
    """Test deleting logs with invalid ID format."""
    client = TestClient(app_with_middleware)
    clear_db_logs()

    # Try to delete with invalid IDs
    response = client.delete("/__devtrack__/logs?log_ids=invalid,123")
    assert response.status_code == 400

    data = response.json()
    assert "Invalid log IDs format" in data["detail"]
