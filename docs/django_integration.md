# Django Integration Guide

This guide shows you how to integrate DevTrack SDK with your Django application for comprehensive request tracking and analytics.

## Quick Start

### 1. Installation

```bash
pip install devtrack-sdk
```

### 2. Add Middleware to Settings

Add the DevTrack middleware to your Django settings:

```python
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
```

### 3. Add URL Patterns

Include DevTrack URL patterns in your main URLs configuration:

```python
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
```

### 4. Test the Integration

Start your Django development server:

```bash
python manage.py runserver
```

Test the tracking endpoints:

```bash
# Get tracking statistics
curl http://localhost:8000/__devtrack__/stats

# Manually add tracking data
curl -X POST http://localhost:8000/__devtrack__/track \
  -H "Content-Type: application/json" \
  -d '{"custom": "data"}'
```

## Advanced Configuration

### Custom Exclude Paths

You can customize which paths to exclude from tracking:

```python
# settings.py

from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class CustomDevTrackMiddleware(DevTrackDjangoMiddleware):
    def __init__(self, get_response=None):
        exclude_paths = [
            "/api/health/",
            "/api/metrics/",
            "/admin/",
            "/static/",
            "/media/",
            "/debug/",
        ]
        super().__init__(get_response, exclude_path=exclude_paths)

# Use the custom middleware
MIDDLEWARE = [
    # ... other middleware
    'your_app.middleware.CustomDevTrackMiddleware',
]
```

### Environment-Specific Configuration

Configure different exclude paths for different environments:

```python
# settings.py

import os

# Environment-specific exclude paths
EXCLUDE_PATHS = {
    'development': [
        "/debug/",
        "/test/",
        "/docs/",
    ],
    'production': [
        "/health/",
        "/metrics/",
        "/admin/",
    ],
    'staging': [
        "/health/",
        "/admin/",
    ]
}

class EnvironmentAwareDevTrackMiddleware(DevTrackDjangoMiddleware):
    def __init__(self, get_response=None):
        env = os.getenv('DJANGO_ENV', 'development')
        exclude_paths = EXCLUDE_PATHS.get(env, [])
        super().__init__(get_response, exclude_path=exclude_paths)
```

### Custom Data Extraction

Extend the middleware to capture additional data:

```python
# middleware.py

from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class EnhancedDevTrackMiddleware(DevTrackDjangoMiddleware):
    def _extract_devtrack_log_data(self, request, response, start_time):
        # Get base data
        log_data = super()._extract_devtrack_log_data(request, response, start_time)
        
        # Add custom fields
        log_data.update({
            "app_version": "1.0.0",
            "environment": os.getenv('DJANGO_ENV', 'development'),
            "user_email": getattr(request.user, 'email', None) if request.user.is_authenticated else None,
            "session_id": request.session.session_key,
            "request_id": request.META.get('HTTP_X_REQUEST_ID'),
        })
        
        return log_data
```

## API Endpoints

### GET /__devtrack__/stats

Returns all tracked request data:

```json
{
    "total": 42,
    "entries": [
        {
            "path": "/api/users/",
            "method": "GET",
            "status_code": 200,
            "timestamp": "2024-03-20T10:00:00Z",
            "client_ip": "127.0.0.1",
            "duration_ms": 150.5,
            "user_agent": "Mozilla/5.0...",
            "referer": "http://localhost:8000/",
            "query_params": {"page": "1"},
            "path_params": {"id": "123"},
            "request_body": {"name": "John"},
            "response_size": 1024,
            "user_id": "1",
            "role": "admin",
            "trace_id": "uuid-here"
        }
    ]
}
```

### POST /__devtrack__/track

Manually add custom tracking data:

```bash
curl -X POST http://localhost:8000/__devtrack__/track \
  -H "Content-Type: application/json" \
  -d '{
    "custom_event": "user_login",
    "user_id": "123",
    "timestamp": "2024-03-20T10:00:00Z"
  }'
```

## Integration with Django REST Framework

If you're using Django REST Framework, the middleware works seamlessly:

```python
# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def api_example(request):
    if request.method == 'GET':
        return Response({"message": "Hello from DRF!"})
    elif request.method == 'POST':
        return Response(request.data, status=status.HTTP_201_CREATED)
```

The middleware will automatically track:
- Request method and path
- Status codes
- Request/response bodies
- Duration
- User authentication info

## Security Considerations

### Sensitive Data Filtering

The middleware automatically filters sensitive data:

```python
# Automatically filtered fields
SENSITIVE_FIELDS = ['password', 'token', 'secret', 'key']

# Custom filtering
class SecureDevTrackMiddleware(DevTrackDjangoMiddleware):
    def _extract_devtrack_log_data(self, request, response, start_time):
        log_data = super()._extract_devtrack_log_data(request, response, start_time)
        
        # Additional filtering
        if 'request_body' in log_data:
            body = log_data['request_body']
            for field in ['ssn', 'credit_card', 'api_key']:
                if field in body:
                    body[field] = '***FILTERED***'
        
        return log_data
```

### Access Control

Consider adding authentication to the stats endpoint in production:

```python
# views.py

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from devtrack_sdk.django_views import stats_view

# Require login for stats
@login_required
def secure_stats_view(request):
    return stats_view(request)

# Require staff access
@staff_member_required
def admin_stats_view(request):
    return stats_view(request)
```

## Performance Considerations

### Memory Management

The middleware stores data in memory. For production applications:

```python
# settings.py

# Limit the number of stored entries
class LimitedDevTrackMiddleware(DevTrackDjangoMiddleware):
    MAX_ENTRIES = 1000
    
    def _extract_devtrack_log_data(self, request, response, start_time):
        log_data = super()._extract_devtrack_log_data(request, response, start_time)
        
        # Limit stored entries
        if len(self.stats) >= self.MAX_ENTRIES:
            self.stats.pop(0)  # Remove oldest entry
        
        return log_data
```

### Async Support

For Django 3.1+ with async views:

```python
# views.py

from django.http import JsonResponse
import asyncio

async def async_api_view(request):
    await asyncio.sleep(0.1)  # Simulate async work
    return JsonResponse({"message": "Async response"})
```

The middleware works with both sync and async views.

## Testing

### Unit Tests

```python
# tests.py

from django.test import TestCase, RequestFactory
from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class DevTrackTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DevTrackDjangoMiddleware()
    
    def test_request_tracking(self):
        request = self.factory.get('/api/test/')
        response = self.middleware(request)
        
        # Check that stats were recorded
        self.assertTrue(len(DevTrackDjangoMiddleware.stats) > 0)
```

### Integration Tests

```python
# test_integration.py

from django.test import TestCase
from django.urls import reverse

class DevTrackIntegrationTest(TestCase):
    def test_stats_endpoint(self):
        response = self.client.get('/__devtrack__/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('entries', data)
```

## Troubleshooting

### Common Issues

1. **Middleware not tracking requests**
   - Check that middleware is in the correct order
   - Verify paths are not in exclude list

2. **Import errors**
   - Ensure Django is installed: `pip install django>=4.0.0`
   - Check Python version compatibility

3. **Performance issues**
   - Consider limiting stored entries
   - Exclude high-traffic paths

### Debug Mode

Enable debug logging:

```python
# settings.py

import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'devtrack_sdk': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Best Practices

1. **Environment Configuration**: Use different exclude paths for different environments
2. **Security**: Always filter sensitive data and consider access control
3. **Performance**: Monitor memory usage and limit stored entries
4. **Testing**: Include DevTrack in your test suite
5. **Documentation**: Document your custom configurations

## Migration from FastAPI

If you're migrating from FastAPI to Django:

1. Replace `DevTrackMiddleware` with `DevTrackDjangoMiddleware`
2. Update middleware configuration in Django settings
3. Include Django URL patterns instead of FastAPI router
4. Update any custom data extraction logic

The API endpoints and data format remain the same, ensuring a smooth transition. 