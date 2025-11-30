"""
Django example with DevTrack SDK v0.4.0 DuckDB integration
"""

import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.urls import path

# import from devtrack_sdk
from devtrack_sdk.database import init_db

# Import DevTrack components
from devtrack_sdk.django_urls import devtrack_urlpatterns

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_settings")


# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="dev-track-example-secret-key",
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            # Add DevTrack middleware
            "devtrack_sdk.django_middleware.DevTrackDjangoMiddleware",
        ],
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        # DevTrack configuration
        DEVTRACK_DB_PATH="django_devtrack_logs.db",
        USE_TZ=True,
    )

django.setup()


# Initialize DevTrack database
print("🗄️ Initializing DevTrack database...")
db = init_db("django_devtrack_logs.db")
print("✅ DevTrack database initialized!")


def home_view(request):
    """Home page view"""
    return JsonResponse(
        {
            "message": "Welcome to Django DevTrack SDK v0.4.0 Example!",
            "version": "0.4.0",
            "features": [
                "DuckDB persistent storage",
                "Real-time monitoring",
                "Advanced querying",
                "Export capabilities",
                "Health checks",
                "CLI toolkit",
            ],
            "endpoints": [
                "/",
                "/api/users",
                "/api/posts",
                "/api/error",
                "/__devtrack__/stats",
                "/__devtrack__/logs",
                "/__devtrack__/track",
            ],
            "cli_commands": [
                "devtrack version",
                "devtrack init",
                "devtrack reset",
                "devtrack export",
                "devtrack query",
                "devtrack monitor",
                "devtrack stat",
                "devtrack health",
            ],
        }
    )


def users_view(request):
    """Users API view"""
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "user"},
        {
            "id": 3,
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "role": "moderator",
        },
        {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "role": "user"},
    ]
    return JsonResponse(
        {"users": users, "total": len(users), "message": "Users retrieved successfully"}
    )


def posts_view(request):
    """Posts API view"""
    posts = [
        {
            "id": 1,
            "title": "Hello World",
            "content": "This is my first post",
            "author": "John Doe",
        },
        {
            "id": 2,
            "title": "Django DevTrack v0.4.0",
            "content": "Using DevTrack with Django and DuckDB",
            "author": "Jane Smith",
        },
        {
            "id": 3,
            "title": "DuckDB Integration",
            "content": "Persistent logging with DuckDB database",
            "author": "Bob Johnson",
        },
        {
            "id": 4,
            "title": "CLI Toolkit",
            "content": "8 powerful CLI commands for DevTrack management",
            "author": "Alice Brown",
        },
    ]
    return JsonResponse(
        {"posts": posts, "total": len(posts), "message": "Posts retrieved successfully"}
    )


def error_view(request):
    """Error view for testing error tracking"""
    return JsonResponse(
        {
            "error": "This is a test error for DevTrack v0.4.0",
            "status": "error",
            "code": "TEST_ERROR",
            "message": "This endpoint intentionally returns an error\
                for testing purposes",
        },
        status=500,
    )


def slow_view(request):
    """Slow view for testing performance tracking"""
    import time

    time.sleep(0.5)  # Simulate slow response
    return JsonResponse(
        {
            "message": "This is a slow endpoint",
            "duration": "500ms",
            "purpose": "Testing performance tracking",
        }
    )


def health_view(request):
    """Health check view"""
    return JsonResponse(
        {
            "status": "healthy",
            "version": "0.4.0",
            "database": "DuckDB",
            "middleware": "DevTrackDjangoMiddleware",
            "timestamp": "2024-01-01T00:00:00Z",
        }
    )


# URL patterns
urlpatterns = [
    path("", home_view, name="home"),
    path("api/users/", users_view, name="users"),
    path("api/posts/", posts_view, name="posts"),
    path("api/error/", error_view, name="error"),
    path("api/slow/", slow_view, name="slow"),
    path("api/health/", health_view, name="health"),
    # Include DevTrack URLs
    *devtrack_urlpatterns,
]

# WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    print("🚀 Starting Django DevTrack SDK v0.4.0 Example...")
    print("=" * 60)
    print("📊 DevTrack v0.4.0 Features:")
    print("   ✅ DuckDB persistent storage")
    print("   ✅ Real-time monitoring")
    print("   ✅ Advanced querying")
    print("   ✅ Export capabilities")
    print("   ✅ Health checks")
    print("   ✅ CLI toolkit (8 commands)")
    print()
    print("📊 DevTrack API endpoints:")
    print("   GET    /__devtrack__/stats  - View statistics")
    print("   POST   /__devtrack__/track  - Manual tracking")
    print("   DELETE /__devtrack__/logs   - Delete logs")
    print()
    print("🌐 Example API endpoints:")
    print("   GET  /                     - Home page")
    print("   GET  /api/users/           - Users list")
    print("   GET  /api/posts/           - Posts list")
    print("   GET  /api/error/           - Error test")
    print("   GET  /api/slow/            - Slow endpoint test")
    print("   GET  /api/health/          - Health check")
    print()
    print("🔧 Django management commands:")
    print("   python manage.py devtrack_init   - Initialize database")
    print("   python manage.py devtrack_stats  - Show statistics")
    print("   python manage.py devtrack_reset  - Reset database")
    print()
    print("🛠️ CLI commands:")
    print("   devtrack version           - Show version info")
    print("   devtrack init --force      - Initialize database")
    print("   devtrack monitor           - Real-time monitoring")
    print("   devtrack query --limit 10  - Query logs")
    print("   devtrack export --format json - Export logs")
    print("   devtrack stat --endpoint   - Show statistics")
    print("   devtrack health --endpoint - Health check")
    print()
    print("💡 Test the endpoints:")
    print("   curl http://localhost:8000/")
    print("   curl http://localhost:8000/api/users/")
    print("   curl http://localhost:8000/api/error/")
    print("   curl http://localhost:8000/__devtrack__/stats")
    print("   curl http://localhost:8000/__devtrack__/stats?limit=5")
    print()
    print("🎯 Start the server:")
    print("   python examples/django_example.py")
    print("   # or")
    print("   gunicorn examples.django_example:application")
    print()
    print("📚 Documentation:")
    print("   https://devtrack-sdk.readthedocs.io")
    print("   https://github.com/mahesh-solanke/devtrack-sdk")
    print("=" * 60)
