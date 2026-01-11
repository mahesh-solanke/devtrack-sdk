"""
Pytest configuration for DevTrack SDK tests
"""

from unittest.mock import patch

import pytest
import requests

# Ignore test_wsgi.py during pytest collection
# It's a WSGI configuration file, not a test file
collect_ignore = ["test_wsgi.py"]


@pytest.fixture(autouse=True)
def mock_network_requests():
    """
    Automatically mock network requests to prevent hanging in CI.
    This ensures detect_devtrack_endpoint() doesn't make real network calls.
    Tests that need specific network behavior should override these mocks.
    """
    # Mock requests.get/delete to raise RequestException by default
    # This makes detect_devtrack_endpoint() try all URLs (fast with 0.5s timeout)
    # and then prompt. We mock typer.prompt/confirm to avoid hanging on user input.
    # Tests that need specific behavior will override these mocks.
    with patch(
        "requests.get", side_effect=requests.RequestException("Mocked network error")
    ):
        with patch(
            "requests.delete",
            side_effect=requests.RequestException("Mocked network error"),
        ):
            # Mock typer prompts with sensible defaults to avoid hanging
            # Tests that test prompt behavior will override these
            with patch("typer.prompt", return_value="localhost"):
                with patch("typer.confirm", return_value=False):
                    with patch("typer.echo"):  # Suppress echo output in tests
                        yield
