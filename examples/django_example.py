"""
Django Example - How to integrate DevTrack SDK with a Django project

This example shows how to add request tracking to a Django application.
"""

# Example Django settings.py configuration
DJANGO_SETTINGS_EXAMPLE = """
# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add DevTrack middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

# Optional: Configure DevTrack middleware with custom exclude paths
DEVELOPMENT_EXCLUDE_PATHS = ["/debug/", "/test/"]
PRODUCTION_EXCLUDE_PATHS = ["/health/", "/metrics/"]

# In your main urls.py, include DevTrack URLs:
# from devtrack_sdk.django_urls import devtrack_urlpatterns
# urlpatterns = [
#     # ... your other URL patterns
#     *devtrack_urlpatterns,
# ]
"""

# Example Django urls.py configuration
DJANGO_URLS_EXAMPLE = """
# urls.py

from django.contrib import admin
from django.urls import path, include
from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # Your other URL patterns here
    path('api/', include('your_app.urls')),
    # Include DevTrack URLs
    *devtrack_urlpatterns,
]
"""

# Example Django views.py with custom middleware configuration
DJANGO_VIEWS_EXAMPLE = """
# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

# Example API view
@csrf_exempt
def api_example(request):
    return JsonResponse({"message": "Hello from Django API!"})

# Example class-based view
class ExampleView(View):
    def get(self, request):
        return JsonResponse({"message": "Hello from class-based view!"})
    def post(self, request):
        return JsonResponse({"message": "POST request received!"})
"""

# Example custom middleware configuration
CUSTOM_MIDDLEWARE_EXAMPLE = """
# Custom middleware configuration example

from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class CustomDevTrackMiddleware(DevTrackDjangoMiddleware):
    def __init__(self, get_response=None):
        # Custom exclude paths for your application
        exclude_paths = [
            "/api/health/",
            "/api/metrics/",
            "/admin/",
            "/static/",
            "/media/",
        ]
        super().__init__(get_response, exclude_path=exclude_paths)
    def _extract_devtrack_log_data(self, request, response, start_time):
        # Customize the data extraction if needed
        log_data = super()._extract_devtrack_log_data(request, response, start_time)
        # Add custom fields
        log_data["custom_field"] = "custom_value"
        log_data["app_version"] = "1.0.0"
        return log_data
"""

if __name__ == "__main__":
    print("Django Integration Example")
    print("=" * 50)
    print("\n1. Add middleware to settings.py:")
    print(DJANGO_SETTINGS_EXAMPLE)
    print("\n2. Include URLs in urls.py:")
    print(DJANGO_URLS_EXAMPLE)
    print("\n3. Access tracking data at:")
    print("   GET /__devtrack__/stats")
    print("   POST /__devtrack__/track")
    print("\n4. Custom middleware example:")
    print(CUSTOM_MIDDLEWARE_EXAMPLE)
