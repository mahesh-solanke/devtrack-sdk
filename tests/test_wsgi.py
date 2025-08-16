"""
Test WSGI application for DevTrack SDK Django tests
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
application = get_wsgi_application()
