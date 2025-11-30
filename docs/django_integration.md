# Django Integration Guide

This guide shows you how to integrate DevTrack SDK v0.4.0 with your Django application for comprehensive request tracking and analytics using DuckDB for persistent storage.

## Quick Start

### 1. Installation

```bash
pip install devtrack-sdk
```

### 2. Initialize Database

Initialize the DuckDB database for persistent log storage:

```bash
# Using CLI
devtrack init --force

# Or using Django management command
python manage.py devtrack_init --force
```

### 3. Add Middleware to Settings

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

# DevTrack configuration
DEVTRACK_DB_PATH = 'devtrack_logs.db'  # Path to DuckDB file
```

### 4. Add URL Patterns

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

### 5. Django Management Commands

DevTrack SDK provides Django management commands for database operations:

```bash
# Initialize database
python manage.py devtrack_init --force

# Show statistics
python manage.py devtrack_stats --limit 20

# Reset database (delete all logs)
python manage.py devtrack_reset --yes
```

### 6. Test the Integration

Start your Django development server:

```bash
python manage.py runserver
```

Test the tracking endpoints:

```bash
# Get tracking statistics
curl http://localhost:8000/__devtrack__/stats

# View limited statistics
curl http://localhost:8000/__devtrack__/stats?limit=5
```

---

## Advanced Configuration

### Environment-specific Configuration

```python
# settings.py
import os

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

# Environment-specific configuration
env = os.getenv('ENVIRONMENT', 'development')
if env == 'production':
    DEVTRACK_DB_PATH = '/var/lib/devtrack/logs.db'
    DEVTRACK_EXCLUDE_PATHS = ['/health', '/metrics', '/admin']
else:
    DEVTRACK_DB_PATH = 'devtrack_logs.db'
    DEVTRACK_EXCLUDE_PATHS = ['/docs', '/redoc', '/health']
```

### Custom Middleware Configuration

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
        ]
        super().__init__(get_response, exclude_path=exclude_paths)

# Use custom middleware in MIDDLEWARE setting
MIDDLEWARE = [
    # ... other middleware
    'your_app.middleware.CustomDevTrackMiddleware',
]
```

### Database Configuration

```python
# settings.py

# Custom database path
DEVTRACK_DB_PATH = '/custom/path/devtrack_logs.db'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## API Endpoints

### GET /__devtrack__/stats

Returns comprehensive statistics and logs from the database.

#### Query Parameters
- `limit` (int, optional): Limit number of entries returned
- `offset` (int, default: 0): Offset for pagination
- `path_pattern` (str, optional): Filter by path pattern
- `status_code` (int, optional): Filter by status code

#### Example Usage
```bash
# Get all statistics
curl http://localhost:8000/__devtrack__/stats

# Get limited results
curl http://localhost:8000/__devtrack__/stats?limit=10

# Filter by status code
curl http://localhost:8000/__devtrack__/stats?status_code=404

# Filter by path pattern
curl http://localhost:8000/__devtrack__/stats?path_pattern=/api/users
```

#### Response Format
```json
{
    "summary": {
        "total_requests": 1500,
        "unique_endpoints": 25,
        "avg_duration_ms": 125.5,
        "min_duration_ms": 10.2,
        "max_duration_ms": 2500.0,
        "success_count": 1400,
        "error_count": 100
    },
    "total": 1500,
    "entries": [
        {
            "id": 1,
            "path": "/api/users",
            "path_pattern": "/api/users",
            "method": "GET",
            "status_code": 200,
            "timestamp": "2024-01-01T10:00:00Z",
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
            "trace_id": "uuid-here",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "filters": {
        "limit": 50,
        "offset": 0,
        "path_pattern": null,
        "status_code": null
    }
}
```

### DELETE /__devtrack__/logs

Delete logs from the database with various filtering options.

#### Query Parameters
- `all_logs` (bool, default: false): Delete all logs
- `path_pattern` (str, optional): Delete logs by path pattern
- `status_code` (int, optional): Delete logs by status code
- `older_than_days` (int, optional): Delete logs older than N days
- `log_ids` (str, optional): Comma-separated list of log IDs to delete

#### Example Usage
```bash
# Delete all logs
curl -X DELETE http://localhost:8000/__devtrack__/logs?all_logs=true

# Delete logs by path pattern
curl -X DELETE http://localhost:8000/__devtrack__/logs?path_pattern=/api/users

# Delete logs by status code
curl -X DELETE http://localhost:8000/__devtrack__/logs?status_code=404

# Delete old logs
curl -X DELETE http://localhost:8000/__devtrack__/logs?older_than_days=30
```

#### Response Format
```json
{
    "message": "Successfully deleted 150 log entries",
    "deleted_count": 150,
    "criteria": {
        "all_logs": false,
        "path_pattern": "/api/users",
        "status_code": null,
        "older_than_days": null,
        "log_ids": null
    }
}
```

---

## Django Management Commands

### devtrack_init

Initialize the DuckDB database for DevTrack.

```bash
# Initialize with default settings
python manage.py devtrack_init

# Force initialization (overwrite existing)
python manage.py devtrack_init --force

# Custom database path
python manage.py devtrack_init --db-path /custom/path/db.db
```

### devtrack_stats

Display statistics from the DuckDB database.

```bash
# Show basic statistics
python manage.py devtrack_stats

# Show limited results
python manage.py devtrack_stats --limit 20

# Show in JSON format
python manage.py devtrack_stats --format json

# Custom database path
python manage.py devtrack_stats --db-path /custom/path/db.db
```

### devtrack_reset

Reset the DuckDB database (delete all logs).

```bash
# Reset with confirmation
python manage.py devtrack_reset

# Skip confirmation
python manage.py devtrack_reset --yes

# Custom database path
python manage.py devtrack_reset --db-path /custom/path/db.db
```

---

## CLI Integration

### Database Management

```bash
# Initialize database
devtrack init --force

# Reset database
devtrack reset --yes

# Show statistics
devtrack stat
```

### Real-time Monitoring

```bash
# Start monitoring
devtrack monitor --interval 3

# Monitor with custom settings
devtrack monitor --interval 5 --top 20
```

### Export and Query

```bash
# Export logs
devtrack export --format json --limit 1000

# Query logs
devtrack query --status-code 404 --days 7

# Health check
devtrack health
```

---

## Security Considerations

### Access Control

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

### Sensitive Data Filtering

```python
# settings.py
from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class SecureDevTrackMiddleware(DevTrackDjangoMiddleware):
    def _extract_devtrack_log_data(self, request, response, start_time):
        # Get base data
        log_data = super()._extract_devtrack_log_data(request, response, start_time)
        
        # Additional filtering
        if 'request_body' in log_data:
            body = log_data['request_body']
            for field in ['ssn', 'credit_card', 'api_key']:
                if field in body:
                    body[field] = '***FILTERED***'
        
        return log_data
```

---

## Performance Optimization

### Exclude High-Traffic Paths

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

# Exclude paths from tracking
DEVTRACK_EXCLUDE_PATHS = [
    '/health',
    '/metrics',
    '/admin',
    '/static',
    '/media',
    '/favicon.ico'
]
```

### Custom Performance Monitoring

```python
# middleware.py
import time
from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware

class PerformanceMonitoringMiddleware(DevTrackDjangoMiddleware):
    def __call__(self, request):
        start_time = time.time()
        
        try:
            response = super().__call__(request)
            
            # Log performance metrics
            duration = time.time() - start_time
            if duration > 1.0:  # Log slow requests
                print(f"Slow request: {request.path} took {duration:.2f}s")
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            print(f"Request failed: {request.path} after {duration:.2f}s: {e}")
            raise
```

---

## Integration with Monitoring Tools

### Prometheus Integration

```python
# middleware.py
from prometheus_client import Counter, Histogram, Gauge
from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware
import time

# Metrics
request_count = Counter('devtrack_requests_total', 'Total requests', ['method', 'path', 'status'])
request_duration = Histogram('devtrack_request_duration_seconds', 'Request duration')
active_requests = Gauge('devtrack_active_requests', 'Active requests')

class PrometheusDevTrackMiddleware(DevTrackDjangoMiddleware):
    def __call__(self, request):
        start_time = time.time()
        active_requests.inc()
        
        try:
            response = super().__call__(request)
            
            # Record metrics
            request_count.labels(
                method=request.method,
                path=request.path,
                status=response.status_code
            ).inc()
            
            request_duration.observe(time.time() - start_time)
            
            return response
        finally:
            active_requests.dec()
```

---

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for DevTrack database
RUN mkdir -p /app/data

# Set environment variables
ENV DEVTRACK_DB_PATH=/app/data/devtrack_logs.db
ENV DJANGO_ENV=production

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment Variables

```bash
# .env.production
DJANGO_ENV=production
DEVTRACK_DB_PATH=/var/lib/devtrack/logs.db
DEVTRACK_EXCLUDE_PATHS=/health,/metrics,/admin
DEVTRACK_MAX_ENTRIES=10000
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Common Issues

1. **Database not initialized**
   ```bash
   python manage.py devtrack_init --force
   ```

2. **Import errors**
   ```bash
   pip install devtrack-sdk
   ```

3. **Permission errors**
   ```bash
   chmod +x /path/to/devtrack_logs.db
   ```

4. **Middleware not working**
   - Check MIDDLEWARE order in settings.py
   - Ensure DevTrack middleware is added
   - Verify URL patterns are included

### Debug Mode

```python
# settings.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode
DEBUG = True
```

---

## Examples

### Basic Django App

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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

# DevTrack configuration
DEVTRACK_DB_PATH = 'devtrack_logs.db'
```

```python
# urls.py
from django.contrib import admin
from django.urls import path, include
from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    # Include DevTrack URLs
    *devtrack_urlpatterns,
]
```

### Advanced Configuration

```python
# settings.py
import os

# Environment-specific configuration
env = os.getenv('DJANGO_ENV', 'development')

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

# Environment-specific DevTrack configuration
if env == 'production':
    DEVTRACK_DB_PATH = '/var/lib/devtrack/logs.db'
    DEVTRACK_EXCLUDE_PATHS = ['/health', '/metrics', '/admin']
else:
    DEVTRACK_DB_PATH = 'devtrack_logs.db'
    DEVTRACK_EXCLUDE_PATHS = ['/docs', '/redoc', '/health']
```

---

## Resources

- **GitHub Repository**: [https://github.com/mahesh-solanke/devtrack-sdk](https://github.com/mahesh-solanke/devtrack-sdk)
- **Documentation**: [https://devtrack-sdk.readthedocs.io](https://devtrack-sdk.readthedocs.io)
- **Issues**: [https://github.com/mahesh-solanke/devtrack-sdk/issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [https://github.com/mahesh-solanke/devtrack-sdk/discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)