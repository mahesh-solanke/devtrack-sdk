from unittest.mock import MagicMock, patch

import requests
from typer.testing import CliRunner

from devtrack_sdk.cli import app, detect_devtrack_endpoint

runner = CliRunner()


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
            {"path": "/api/test", "method": "GET", "duration_ms": 100},
            {"path": "/api/test", "method": "GET", "duration_ms": 200},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock(
            status_code=200, json=MagicMock(return_value=mock_stats)
        )
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat"])
        assert result.exit_code == 0, "Stat command failed"
        assert "📊 DevTrack Stats CLI" in result.output, "Stat CLI header missing"
        assert "/api/test" in result.output, "API path missing in output"
        assert "GET" in result.output, "HTTP method missing in output"


def test_stat_command_with_top_option():
    mock_stats = {
        "entries": [
            {"path": "/api/test1", "method": "GET", "duration_ms": 100},
            {"path": "/api/test2", "method": "POST", "duration_ms": 200},
            {"path": "/api/test3", "method": "PUT", "duration_ms": 300},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock(
            status_code=200, json=MagicMock(return_value=mock_stats)
        )
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat", "--top", "2"])
        assert result.exit_code == 0, "Stat command with top option failed"
        assert result.output.count("Path") == 1, "Header appears more than once"
        assert result.output.count("GET") == 1, "GET method count mismatch"
        assert result.output.count("POST") == 1, "POST method count mismatch"
        assert result.output.count("PUT") == 0, "PUT method should not appear"


def test_stat_command_with_sort_by_latency():
    mock_stats = {
        "entries": [
            {"path": "/api/fast", "method": "GET", "duration_ms": 100},
            {"path": "/api/slow", "method": "GET", "duration_ms": 500},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock(
            status_code=200, json=MagicMock(return_value=mock_stats)
        )
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat", "--sort-by", "latency"])
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
            result = runner.invoke(app, ["stat"])
            assert result.exit_code == 1, "Error handling failed"
            assert "Failed to fetch stats" in result.output, "Error message mismatch"


def test_stat_command_empty_stats():
    mock_stats = {"entries": []}

    with patch("requests.get") as mock_get:
        mock_response = MagicMock(
            status_code=200, json=MagicMock(return_value=mock_stats)
        )
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat"])
        assert result.exit_code == 0, "Empty stats command failed"
        assert (
            "No request stats found yet" in result.output
        ), "Empty stats message mismatch"
