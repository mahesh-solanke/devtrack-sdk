from unittest.mock import MagicMock, patch

import requests
from typer.testing import CliRunner

from devtrack_sdk.cli import app, detect_devtrack_endpoint

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DevTrack SDK v" in result.output


def test_stat_help():
    result = runner.invoke(app, ["stat", "--help"])
    assert result.exit_code == 0
    assert "Show top N endpoints" in result.output


def test_detect_devtrack_endpoint_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        endpoint = detect_devtrack_endpoint()
        assert endpoint == "http://localhost:8000/__devtrack__/stats"
        mock_get.assert_called_with(
            "http://localhost:8000/__devtrack__/stats", timeout=0.5
        )


def test_detect_devtrack_endpoint_with_domain():
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = ["api.example.com", "https"]
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException()

            endpoint = detect_devtrack_endpoint()
            assert endpoint == "https://api.example.com/__devtrack__/stats"
            assert mock_prompt.call_count == 2


def test_detect_devtrack_endpoint_with_localhost():
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = ["localhost", "8000", "http"]
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException()

            endpoint = detect_devtrack_endpoint()
            assert endpoint == "http://localhost:8000/__devtrack__/stats"
            assert mock_prompt.call_count == 3


def test_detect_devtrack_endpoint_with_full_url():
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = ["https://api.example.com/", "n"]  # n for no port
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException()

            endpoint = detect_devtrack_endpoint()
            assert endpoint == "https://api.example.com/__devtrack__/stats"
            assert mock_prompt.call_count == 1  # Only asked for host, not protocol


def test_detect_devtrack_endpoint_with_full_url_and_port():
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = [
            "http://api.example.com",
            "y",
            "8080",
        ]  # y for yes port
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException()

            endpoint = detect_devtrack_endpoint()
            assert endpoint == "http://api.example.com:8080/__devtrack__/stats"
            assert mock_prompt.call_count == 2  # Asked for host and port, not protocol


def test_detect_devtrack_endpoint_with_cleanup():
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = [
            "https://api.example.com///",
            "n",
        ]  # Test cleanup of extra slashes
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException()

            endpoint = detect_devtrack_endpoint()
            assert endpoint == "https://api.example.com/__devtrack__/stats"
            assert mock_prompt.call_count == 1


def test_stat_command_success():
    mock_stats = {
        "entries": [
            {"path": "/api/test", "method": "GET", "duration_ms": 100},
            {"path": "/api/test", "method": "GET", "duration_ms": 200},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_stats
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat"])
        assert result.exit_code == 0
        assert "📊 DevTrack Stats CLI" in result.output
        assert "/api/test" in result.output
        assert "GET" in result.output


def test_stat_command_with_top_option():
    mock_stats = {
        "entries": [
            {"path": "/api/test1", "method": "GET", "duration_ms": 100},
            {"path": "/api/test2", "method": "POST", "duration_ms": 200},
            {"path": "/api/test3", "method": "PUT", "duration_ms": 300},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_stats
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat", "--top", "2"])
        assert result.exit_code == 0
        assert result.output.count("Path") == 1  # Header appears once
        assert result.output.count("GET") == 1
        assert result.output.count("POST") == 1
        assert result.output.count("PUT") == 0  # Third entry should be cut off


def test_stat_command_with_sort_by_latency():
    mock_stats = {
        "entries": [
            {"path": "/api/fast", "method": "GET", "duration_ms": 100},
            {"path": "/api/slow", "method": "GET", "duration_ms": 500},
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_stats
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat", "--sort-by", "latency"])
        assert result.exit_code == 0
        # The slow endpoint should appear first
        assert result.output.find("/api/slow") < result.output.find("/api/fast")


def test_stat_command_error_handling():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Connection failed")

        result = runner.invoke(app, ["stat"])
        assert result.exit_code == 1
        assert "Failed to fetch stats" in result.output


def test_stat_command_empty_stats():
    mock_stats = {"entries": []}

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_stats
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["stat"])
        assert result.exit_code == 0
        assert "No request stats found yet" in result.output
