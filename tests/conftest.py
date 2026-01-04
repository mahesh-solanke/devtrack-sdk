"""
Pytest configuration for DevTrack SDK tests
"""

# Ignore test_wsgi.py during pytest collection
# It's a WSGI configuration file, not a test file
collect_ignore = ["test_wsgi.py"]
