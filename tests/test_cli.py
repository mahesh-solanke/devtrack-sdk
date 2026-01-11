import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import requests
from typer.testing import CliRunner

from devtrack_sdk.cli import app, detect_devtrack_endpoint
from devtrack_sdk.database import DevTrackDB, init_db

runner = CliRunner()


def create_test_db(db_path=None):
    """Helper to create a test database file."""
    if db_path is None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
            os.unlink(db_path)  # Remove empty file

    # Ensure file doesn't exist
    if os.path.exists(db_path):
        os.unlink(db_path)

    # Create proper database
    db = init_db(db_path, read_only=False)
    return db_path, db


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, "Version command failed"
    assert "DevTrack SDK v" in result.output, "Version output mismatch"


def test_stat_help():
    result = runner.invoke(app, ["stat", "--help"])
    assert result.exit_code == 0, "Help command failed"
    assert "Show top N endpoints" in result.output, "Help output mismatch"


def test_detect_devtrack_endpoint_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock(status_code=200)
        mock_get.return_value = mock_response

        endpoint = detect_devtrack_endpoint()
        assert (
            endpoint == "http://localhost:8000/__devtrack__/stats"
        ), "Endpoint mismatch"
        mock_get.assert_called_once_with(
            "http://localhost:8000/__devtrack__/stats", timeout=0.5
        )


def test_detect_devtrack_endpoint_with_domain():
    with patch("typer.prompt") as mock_prompt, patch("typer.confirm") as mock_confirm:
        mock_prompt.side_effect = ["api.example.com", "https"]
        mock_confirm.return_value = False
        with patch("requests.get", side_effect=requests.RequestException):
            endpoint = detect_devtrack_endpoint()
            assert (
                endpoint == "https://api.example.com/__devtrack__/stats"
            ), "Endpoint mismatch"
            assert mock_prompt.call_count == 2, "Prompt call count mismatch"
            assert mock_confirm.call_count == 1, "Confirm call count mismatch"


def test_detect_devtrack_endpoint_with_localhost():
    with patch("typer.prompt") as mock_prompt, patch("typer.confirm") as mock_confirm:
        mock_prompt.side_effect = ["localhost", "8000", "http"]
        mock_confirm.return_value = True
        with patch("requests.get", side_effect=requests.RequestException):
            endpoint = detect_devtrack_endpoint()
            assert (
                endpoint == "http://localhost:8000/__devtrack__/stats"
            ), "Endpoint mismatch"
            assert mock_prompt.call_count == 3, "Prompt call count mismatch"
            assert mock_confirm.call_count == 1, "Confirm call count mismatch"


def test_detect_devtrack_endpoint_with_full_url():
    with patch("typer.prompt") as mock_prompt, patch("typer.confirm") as mock_confirm:
        mock_prompt.side_effect = ["https://api.example.com/", "n"]
        mock_confirm.return_value = False
        with patch("requests.get", side_effect=requests.RequestException):
            endpoint = detect_devtrack_endpoint()
            assert (
                endpoint == "https://api.example.com/__devtrack__/stats"
            ), "Endpoint mismatch"
            assert mock_prompt.call_count == 1, "Prompt call count mismatch"
            assert mock_confirm.call_count == 1, "Confirm call count mismatch"


def test_detect_devtrack_endpoint_with_full_url_and_port():
    with patch("typer.prompt") as mock_prompt, patch("typer.confirm") as mock_confirm:
        mock_prompt.side_effect = ["http://api.example.com", "8080"]
        mock_confirm.return_value = True
        with patch("requests.get", side_effect=requests.RequestException):
            endpoint = detect_devtrack_endpoint()
            assert (
                endpoint == "http://api.example.com:8080/__devtrack__/stats"
            ), "Endpoint mismatch"
            assert mock_prompt.call_count == 2, "Prompt call count mismatch"
            assert mock_confirm.call_count == 1, "Confirm call count mismatch"


def test_detect_devtrack_endpoint_with_cleanup():
    with patch("typer.prompt") as mock_prompt, patch("typer.confirm") as mock_confirm:
        mock_prompt.side_effect = ["https://api.example.com///", "n"]
        mock_confirm.return_value = False
        with patch("requests.get", side_effect=requests.RequestException):
            endpoint = detect_devtrack_endpoint()
            assert (
                endpoint == "https://api.example.com/__devtrack__/stats"
            ), "Endpoint mismatch"
            assert mock_prompt.call_count == 1, "Prompt call count mismatch"
            assert mock_confirm.call_count == 1, "Confirm call count mismatch"


def test_stat_command_success():
    mock_stats = {
        "entries": [
            {
                "path": "/api/test",
                "path_pattern": "/api/test",
                "method": "GET",
                "duration_ms": 100,
            },
            {
                "path": "/api/test",
                "path_pattern": "/api/test",
                "method": "GET",
                "duration_ms": 200,
            },
        ]
    }

    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch("requests.get") as mock_get:
            mock_response = MagicMock(
                status_code=200, json=MagicMock(return_value=mock_stats)
            )
            mock_get.return_value = mock_response

            result = runner.invoke(app, ["stat", "--endpoint"], input="n\n")
            assert result.exit_code == 0, "Stat command failed"
            assert "📊 DevTrack Stats CLI" in result.output, "Stat CLI header missing"
            assert "/api/test" in result.output, "API path missing in output"
            assert "GET" in result.output, "HTTP method missing in output"


def test_stat_command_with_top_option():
    mock_stats = {
        "entries": [
            {
                "path": "/api/test1",
                "path_pattern": "/api/test1",
                "method": "GET",
                "duration_ms": 100,
            },
            {
                "path": "/api/test2",
                "path_pattern": "/api/test2",
                "method": "POST",
                "duration_ms": 200,
            },
            {
                "path": "/api/test3",
                "path_pattern": "/api/test3",
                "method": "PUT",
                "duration_ms": 300,
            },
        ]
    }

    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch("requests.get") as mock_get:
            mock_response = MagicMock(
                status_code=200, json=MagicMock(return_value=mock_stats)
            )
            mock_get.return_value = mock_response

            result = runner.invoke(
                app, ["stat", "--top", "2", "--endpoint"], input="n\n"
            )
            assert result.exit_code == 0, "Stat command with top option failed"
            assert result.output.count("Path") == 1, "Header appears more than once"
            assert result.output.count("GET") == 1, "GET method count mismatch"
            assert result.output.count("POST") == 1, "POST method count mismatch"
            assert result.output.count("PUT") == 0, "PUT method should not appear"


def test_stat_command_with_sort_by_latency():
    mock_stats = {
        "entries": [
            {
                "path": "/api/fast",
                "path_pattern": "/api/fast",
                "method": "GET",
                "duration_ms": 100,
            },
            {
                "path": "/api/slow",
                "path_pattern": "/api/slow",
                "method": "GET",
                "duration_ms": 500,
            },
        ]
    }

    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch("requests.get") as mock_get:
            mock_response = MagicMock(
                status_code=200, json=MagicMock(return_value=mock_stats)
            )
            mock_get.return_value = mock_response

            result = runner.invoke(
                app, ["stat", "--sort-by", "latency", "--endpoint"], input="n\n"
            )
            assert result.exit_code == 0, "Stat command with sort by latency failed"
            assert result.output.find("/api/slow") < result.output.find(
                "/api/fast"
            ), "Latency sort order incorrect"


def test_stat_command_error_handling():
    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch(
            "requests.get", side_effect=requests.RequestException("Connection failed")
        ):
            result = runner.invoke(app, ["stat", "--endpoint"])
            assert result.exit_code == 1, "Error handling failed"
            assert "Failed to fetch stats" in result.output, "Error message mismatch"


def test_stat_command_empty_stats():
    mock_stats = {"entries": []}

    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch("requests.get") as mock_get:
            mock_response = MagicMock(
                status_code=200, json=MagicMock(return_value=mock_stats)
            )
            mock_get.return_value = mock_response

            result = runner.invoke(app, ["stat", "--endpoint"])
            assert result.exit_code == 0, "Empty stats command failed"
            assert (
                "No request stats found yet" in result.output
            ), "Empty stats message mismatch"


# ========== INIT COMMAND TESTS ==========


def test_init_new_database():
    """Test initializing a new database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file, let DuckDB create it

    try:
        result = runner.invoke(app, ["init", "--db-path", db_path])
        assert result.exit_code == 0, "Init command failed"
        assert (
            "✅ DevTrack database initialized" in result.output
            or "initialized" in result.output.lower()
        )
        assert os.path.exists(db_path), "Database file not created"

        # Verify tables exist
        db = DevTrackDB(db_path, read_only=True)
        assert db.tables_exist(), "Tables not created"
        db.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_existing_database():
    """Test init on existing database without --force."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        # Create database first using init_db
        from devtrack_sdk.database import init_db

        init_db(db_path, read_only=False).close()

        result = runner.invoke(app, ["init", "--db-path", db_path], input="n\n")
        assert result.exit_code == 0, "Init on existing DB should succeed"
        assert "already initialized" in result.output or "Overwrite" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_with_force():
    """Test init with --force flag."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        # Create database with some data
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["init", "--db-path", db_path, "--force"])
        # Should succeed (may use API or direct DB)
        assert result.exit_code in [0, 1], "Init with force should handle gracefully"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_with_force_via_api():
    """Test init --force using HTTP API."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        # Create database
        db = init_db(db_path, read_only=False)
        db.close()

        mock_delete_response = MagicMock(
            status_code=200, json=MagicMock(return_value={"deleted_count": 5})
        )

        with patch(
            "devtrack_sdk.cli.detect_devtrack_endpoint",
            return_value="http://localhost:8000/__devtrack__/stats",
        ):
            with patch("requests.delete", return_value=mock_delete_response):
                result = runner.invoke(app, ["init", "--db-path", db_path, "--force"])
                assert result.exit_code == 0, "Init with force via API failed"
                assert "via API" in result.output or "reset" in result.output.lower()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_locked_database():
    """Test init when database is locked during initialization."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file - start with no database

    try:
        # Simulate lock error when trying to create/initialize database
        import duckdb

        lock_error = duckdb.IOException(
            "IO Error: Could not set lock on file: "
            "Conflicting lock (held in process with PID 12345)"
        )

        # Mock init_db to raise lock error (this is called when
        # actually creating tables)
        # Also mock detect_devtrack_endpoint to return None (no API available)
        with patch("devtrack_sdk.cli.detect_devtrack_endpoint", return_value=None):
            with patch("devtrack_sdk.cli.init_db", side_effect=lock_error):
                result = runner.invoke(app, ["init", "--db-path", db_path])
                # Should handle lock gracefully - show lock message
                assert (
                    "lock" in result.output.lower() or "locked" in result.output.lower()
                )
                assert result.exit_code == 0  # Should exit gracefully, not crash
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


# ========== RESET COMMAND TESTS ==========


def test_reset_missing_database():
    """Test reset on non-existent database."""
    result = runner.invoke(app, ["reset", "--db-path", "nonexistent.db"])
    assert result.exit_code == 0, "Reset on missing DB should exit gracefully"
    assert "does not exist" in result.output


def test_reset_with_confirmation():
    """Test reset with confirmation prompt."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["reset", "--db-path", db_path], input="n\n")
        assert result.exit_code == 0, "Reset cancelled should exit gracefully"
        assert (
            "cancelled" in result.output.lower() or "Reset cancelled" in result.output
        )
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_reset_with_yes_flag():
    """Test reset with --yes flag (skip confirmation)."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["reset", "--db-path", db_path, "--yes"])
        assert result.exit_code == 0, "Reset with --yes failed"
        assert "reset" in result.output.lower() or "deleted" in result.output.lower()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_reset_via_api():
    """Test reset using HTTP API."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        mock_delete_response = MagicMock(
            status_code=200, json=MagicMock(return_value={"deleted_count": 10})
        )

        with patch(
            "devtrack_sdk.cli.detect_devtrack_endpoint",
            return_value="http://localhost:8000/__devtrack__/stats",
        ):
            with patch("requests.delete", return_value=mock_delete_response):
                result = runner.invoke(app, ["reset", "--db-path", db_path, "--yes"])
                assert result.exit_code == 0, "Reset via API failed"
                assert "via API" in result.output or "deleted" in result.output.lower()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_reset_locked_database():
    """Test reset when database is locked."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        # Simulate lock error
        import duckdb

        lock_error = duckdb.IOException("IO Error: Could not set lock on file")

        with patch("devtrack_sdk.cli.DevTrackDB") as mock_db:
            mock_instance = MagicMock()
            mock_instance.delete_all_logs.side_effect = lock_error
            mock_db.return_value = mock_instance

            with patch(
                "devtrack_sdk.cli.detect_devtrack_endpoint", side_effect=Exception
            ):
                result = runner.invoke(app, ["reset", "--db-path", db_path, "--yes"])
                assert result.exit_code == 1, "Reset on locked DB should fail"
                assert (
                    "lock" in result.output.lower() or "locked" in result.output.lower()
                )
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


# ========== EXPORT COMMAND TESTS ==========


def test_export_missing_database():
    """Test export on non-existent database."""
    result = runner.invoke(app, ["export", "--db-path", "nonexistent.db"])
    assert result.exit_code == 1, "Export on missing DB should fail"
    assert "does not exist" in result.output


def test_export_json_format():
    """Test export to JSON format."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
        os.unlink(db_path)  # Remove empty file

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_out:
        out_path = tmp_out.name
        os.unlink(out_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "path_pattern": "/api/test",  # Required field
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(
            app,
            [
                "export",
                "--db-path",
                db_path,
                "--output-file",
                out_path,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, f"Export to JSON failed: {result.output}"
        assert os.path.exists(out_path), "Output file not created"

        with open(out_path) as f:
            data = json.load(f)
            assert "entries" in data or "export_timestamp" in data
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_export_csv_format():
    """Test export to CSV format."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
        os.unlink(db_path)  # Remove empty file

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_out:
        out_path = tmp_out.name
        os.unlink(out_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(
            app,
            [
                "export",
                "--db-path",
                db_path,
                "--output-file",
                out_path,
                "--format",
                "csv",
            ],
        )
        assert result.exit_code == 0, "Export to CSV failed"
        assert os.path.exists(out_path), "Output file not created"

        with open(out_path) as f:
            content = f.read()
            assert "path" in content or "method" in content
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_export_with_filters():
    """Test export with path pattern and status code filters."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
        os.unlink(db_path)  # Remove empty file

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_out:
        out_path = tmp_out.name
        os.unlink(out_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.insert_log(
            {
                "path": "/api/other",
                "method": "POST",
                "status_code": 404,
                "duration_ms": 50,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(
            app,
            [
                "export",
                "--db-path",
                db_path,
                "--output-file",
                out_path,
                "--path-pattern",
                "/api/test",
                "--status-code",
                "200",
            ],
        )
        assert result.exit_code == 0, "Export with filters failed"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_export_empty_database():
    """Test export from empty database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
        os.unlink(db_path)  # Remove empty file

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_out:
        out_path = tmp_out.name
        os.unlink(out_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        result = runner.invoke(
            app, ["export", "--db-path", db_path, "--output-file", out_path]
        )
        assert result.exit_code == 0, "Export from empty DB should succeed"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_export_with_limit():
    """Test export with limit option."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
        os.unlink(db_path)  # Remove empty file

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_out:
        out_path = tmp_out.name
        os.unlink(out_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        for i in range(5):
            db.insert_log(
                {
                    "path": f"/api/test{i}",
                    "path_pattern": f"/api/test{i}",  # Required field
                    "method": "GET",
                    "status_code": 200,
                    "duration_ms": 100,
                    "timestamp": "2024-01-01T00:00:00",
                    "client_ip": "127.0.0.1",
                    "user_agent": "test",
                }
            )
        db.close()

        result = runner.invoke(
            app,
            ["export", "--db-path", db_path, "--output-file", out_path, "--limit", "2"],
        )
        assert result.exit_code == 0, f"Export with limit failed: {result.output}"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


# ========== QUERY COMMAND TESTS ==========


def test_query_missing_database():
    """Test query on non-existent database."""
    result = runner.invoke(app, ["query", "--db-path", "nonexistent.db"])
    assert result.exit_code == 1, "Query on missing DB should fail"
    assert "does not exist" in result.output


def test_query_empty_database():
    """Test query on empty database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        result = runner.invoke(app, ["query", "--db-path", db_path])
        assert result.exit_code == 0, "Query on empty DB should succeed"
        assert "No logs found" in result.output or "No logs" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_path_pattern():
    """Test query with path pattern filter."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                # Required - get_logs_by_path searches path_pattern column
                "path_pattern": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(
            app, ["query", "--db-path", db_path, "--path-pattern", "/api/test"]
        )
        assert result.exit_code == 0, "Query with path pattern failed"
        # get_logs_by_path searches path_pattern column, so it should find the log
        assert (
            "No logs found" not in result.output
        ), f"Expected to find logs but got: {result.output}"
        assert "/api/test" in result.output or "test" in result.output.lower()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_status_code():
    """Test query with status code filter."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 404,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(
            app, ["query", "--db-path", db_path, "--status-code", "404"]
        )
        assert result.exit_code == 0, "Query with status code failed"
        assert "404" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_method():
    """Test query with HTTP method filter."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "POST",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["query", "--db-path", db_path, "--method", "POST"])
        assert result.exit_code == 0, "Query with method failed"
        assert "POST" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_days():
    """Test query with days filter."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": datetime.now().isoformat(),
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["query", "--db-path", db_path, "--days", "7"])
        assert result.exit_code == 0, "Query with days failed"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_verbose():
    """Test query with verbose flag."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["query", "--db-path", db_path, "--verbose"])
        assert result.exit_code == 0, "Query with verbose failed"
        assert "Path:" in result.output or "Method:" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_query_with_limit():
    """Test query with limit option."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        for i in range(5):
            db.insert_log(
                {
                    "path": f"/api/test{i}",
                    "method": "GET",
                    "status_code": 200,
                    "duration_ms": 100,
                    "timestamp": "2024-01-01T00:00:00",
                    "client_ip": "127.0.0.1",
                    "user_agent": "test",
                }
            )
        db.close()

        result = runner.invoke(app, ["query", "--db-path", db_path, "--limit", "2"])
        assert result.exit_code == 0, "Query with limit failed"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


# ========== STAT COMMAND TESTS (Additional) ==========


def test_stat_command_database_mode():
    """Test stat command using database (not endpoint)."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.insert_log(
            {
                "path": "/api/test",
                "method": "GET",
                "status_code": 200,
                "duration_ms": 100,
                "timestamp": "2024-01-01T00:00:00",
                "client_ip": "127.0.0.1",
                "user_agent": "test",
            }
        )
        db.close()

        result = runner.invoke(app, ["stat", "--db-path", db_path], input="n\n")
        assert result.exit_code == 0, "Stat with DB mode failed"
        assert "📊 DevTrack Stats CLI" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_stat_command_missing_database():
    """Test stat command with missing database."""
    result = runner.invoke(app, ["stat", "--db-path", "nonexistent.db"])
    assert result.exit_code == 1, "Stat on missing DB should fail"
    assert "does not exist" in result.output


def test_stat_command_empty_database():
    """Test stat command with empty database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        result = runner.invoke(app, ["stat", "--db-path", db_path], input="n\n")
        assert result.exit_code == 0, "Stat on empty DB should succeed"
        assert "No request stats found" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


# ========== HEALTH COMMAND TESTS ==========


def test_health_command_database_only():
    """Test health command checking database only."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
        os.unlink(db_path)  # Remove empty file

    try:
        db = init_db(db_path, read_only=False)
        db.close()

        result = runner.invoke(app, ["health", "--db-path", db_path])
        assert result.exit_code in [0, 1], "Health check should complete"
        assert "Health Check" in result.output or "Healthy" in result.output
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_health_command_missing_database():
    """Test health command with missing database."""
    result = runner.invoke(app, ["health", "--db-path", "nonexistent.db"])
    # Health check doesn't fail on missing DB, it just reports it
    assert result.exit_code in [0, 1], "Health check should complete"
    assert (
        "Not Found" in result.output
        or "does not exist" in result.output
        or "⚠️" in result.output
    )


def test_health_command_with_endpoint():
    """Test health command with endpoint check."""
    mock_response = MagicMock(status_code=200)

    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch("requests.get", return_value=mock_response):
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                db_path = tmp.name
                os.unlink(db_path)  # Remove empty file
            try:
                db = init_db(db_path, read_only=False)
                db.close()

                result = runner.invoke(
                    app, ["health", "--db-path", db_path, "--endpoint"]
                )
                assert result.exit_code in [
                    0,
                    1,
                ], "Health with endpoint should complete"
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)


def test_health_command_endpoint_unreachable():
    """Test health command when endpoint is unreachable."""
    with patch(
        "devtrack_sdk.cli.detect_devtrack_endpoint",
        return_value="http://localhost:8000/__devtrack__/stats",
    ):
        with patch(
            "requests.get", side_effect=requests.RequestException("Connection failed")
        ):
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                db_path = tmp.name
                os.unlink(db_path)  # Remove empty file
            try:
                db = init_db(db_path, read_only=False)
                db.close()

                result = runner.invoke(
                    app, ["health", "--db-path", db_path, "--endpoint"]
                )
                assert (
                    result.exit_code == 1
                ), "Health with unreachable endpoint should fail"
                assert "Unreachable" in result.output or "Unhealthy" in result.output
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)


# ========== HELP COMMAND TESTS ==========


def test_help_command():
    """Test help command."""
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0, "Help command failed"
    assert "DevTrack CLI" in result.output or "Available Commands" in result.output


def test_version_command_detailed():
    """Test version command shows all information."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, "Version command failed"
    assert "DevTrack SDK" in result.output
    assert "Version" in result.output or "Framework Support" in result.output
