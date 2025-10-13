# 🚀 DevTrack SDK v0.3.0

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](/LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/devtrack-sdk)](https://pepy.tech/projects/devtrack-sdk)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://devtrack-sdk.readthedocs.io/)
[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-black.svg)](https://github.com/mahesh-solanke/devtrack-sdk/issues)
[![GitHub Pull Requests](https://img.shields.io/badge/GitHub-PRs-black.svg)](https://github.com/mahesh-solanke/devtrack-sdk/pulls)

**Comprehensive request tracking and analytics toolkit for FastAPI and Django applications**

*Built for developers who care about API usage, performance, and observability*

📖 **[View Documentation](https://devtrack-sdk.readthedocs.io/)** | 🚀 **[Quick Start](#-quick-start)** | 🛠️ **[CLI Toolkit](#️-cli-toolkit)**

</div>

---

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🔧 Framework Integration](#-framework-integration)
- [🛠️ CLI Toolkit](#️-cli-toolkit)
- [🗄️ Database Integration](#️-database-integration)
- [📊 API Endpoints](#-api-endpoints)
- [⚙️ Configuration](#️-configuration)
- [🔍 Advanced Usage](#-advanced-usage)
- [🔐 Security](#-security)
- [🧪 Testing](#-testing)
- [📈 Performance](#-performance)
- [🚀 Deployment](#-deployment)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Features

### ✨ Core Features
- **Zero Configuration**: Works out of the box with sensible defaults
- **Dual Framework Support**: FastAPI and Django middleware
- **Real-time Monitoring**: Live dashboard with customizable refresh intervals
- **Advanced Querying**: Filter and search logs with multiple criteria
- **Export Capabilities**: Export logs to JSON or CSV formats
- **Health Monitoring**: System health checks and component status
- **CLI Toolkit**: 8 powerful commands for managing your DevTrack instance

### 🗄️ Database Features
- **DuckDB Integration**: High-performance embedded database
- **Persistent Storage**: Data survives application restarts
- **Advanced Analytics**: Built-in statistical analysis
- **Data Management**: Reset, export, and query capabilities

### 🎯 Tracking Capabilities
- **Comprehensive Logging**: 15+ fields per request
- **Performance Metrics**: Duration, response size, latency tracking
- **User Context**: User ID, role, and authentication data
- **Request Details**: Path parameters, query params, request body
- **Client Information**: IP address, user agent, referer
- **Trace IDs**: Unique request identification

---

## 🚀 Quick Start

> 📖 **Need more details?** Check out our comprehensive [documentation](https://devtrack-sdk.readthedocs.io/) for detailed guides, API reference, and advanced usage examples.

### 1. Install DevTrack SDK

```bash
pip install devtrack-sdk
```

### 2. Choose Your Framework

#### FastAPI Integration
```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

#### Django Integration
```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

# urls.py
from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    # ... your other URL patterns
    *devtrack_urlpatterns,
]
```

### 3. Initialize Database
```bash
devtrack init --force
```

### 4. Start Monitoring
```bash
devtrack monitor --interval 3
```

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- FastAPI or Django application

### Install from PyPI
```bash
pip install devtrack-sdk
```

### Install from Source
```bash
git clone https://github.com/mahesh-solanke/devtrack-sdk.git
cd devtrack-sdk
pip install -e .
```

### Dependencies
- `fastapi>=0.90` - FastAPI framework support
- `django>=4.0.0` - Django framework support
- `httpx>=0.24` - HTTP client for CLI
- `starlette>=0.22` - ASGI framework
- `rich>=13.3` - Rich CLI interface
- `typer>=0.9` - CLI framework
- `duckdb>=1.1.0` - Embedded database

---

## 🔧 Framework Integration

### FastAPI Integration

#### Basic Setup
```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI(title="My API")
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

#### Advanced Configuration
```python
import os
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()

# Environment-specific configuration
exclude_paths = {
    'development': ['/docs', '/redoc', '/health'],
    'production': ['/health', '/metrics'],
    'staging': ['/health', '/admin']
}

env = os.getenv('ENVIRONMENT', 'development')
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=exclude_paths.get(env, [])
)
```

#### Custom Middleware
```python
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.middleware.extractor import extract_devtrack_log_data
from datetime import datetime, timezone
import uuid

class CustomDevTrackMiddleware(DevTrackMiddleware):
    def __init__(self, app, exclude_path: list[str] = []):
        super().__init__(app, exclude_path)
        self.app_version = "1.0.0"
        self.environment = os.getenv('ENV', 'development')
    
    async def dispatch(self, request, call_next):
        if request.url.path in self.skip_paths:
            return await call_next(request)

        start_time = datetime.now(timezone.utc)
        
        # Read and buffer the body
        body = await request.body()
        
        async def receive():
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }
        
        # Rebuild the request
        request = Request(request.scope, receive)
        response = await call_next(request)
        
        try:
            # Extract base log data
            log_data = await extract_devtrack_log_data(request, response, start_time)
            
            # Add custom fields
            log_data.update({
                "app_version": self.app_version,
                "environment": self.environment,
                "request_id": str(uuid.uuid4()),
            })
            
            # Store in database
            from devtrack_sdk.database import get_db
            db = get_db()
            db.insert_log(log_data)
        except Exception as e:
            print(f"[CustomDevTrackMiddleware] Logging error: {e}")
        
        return response
```

### Django Integration

#### Basic Setup
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

# urls.py
from django.urls import path, include
from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.urls')),
    # Include DevTrack URLs
    *devtrack_urlpatterns,
]
```

#### Advanced Configuration
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

# Use custom middleware
MIDDLEWARE = [
    # ... other middleware
    'your_app.middleware.CustomDevTrackMiddleware',
]
```

---

## 🛠️ CLI Toolkit

DevTrack SDK includes a comprehensive CLI toolkit with 8 powerful commands:

### 📦 Version Information
```bash
devtrack version
```
Shows SDK version, framework support, database type, and CLI features count.

### 🗄️ Database Management

#### Initialize Database
```bash
devtrack init --force
```
Creates a new DuckDB database with progress indicators and shows database information.

#### Reset Database
```bash
devtrack reset --yes
```
Deletes all log entries with confirmation prompt (skip with `--yes` flag).

### 📤 Export Capabilities
```bash
# Export to JSON
devtrack export --format json --limit 1000 --output-file logs.json

# Export to CSV
devtrack export --format csv --limit 500 --output-file logs.csv

# Export with filters
devtrack export --status-code 404 --days 7 --format json
```

### 🔍 Advanced Querying
```bash
# Basic query
devtrack query --limit 50

# Filter by status code
devtrack query --status-code 404 --days 7

# Filter by HTTP method
devtrack query --method POST --verbose

# Filter by path pattern
devtrack query --path-pattern "/api/users" --limit 20
```

### 📊 Real-time Monitoring
```bash
# Start monitoring with 3-second intervals
devtrack monitor --interval 3 --top 15

# Monitor with custom database path
devtrack monitor --db-path /custom/path/db.db --interval 5
```

### 📈 Statistics
```bash
# Show stats from database
devtrack stat

# Show stats from HTTP endpoint
devtrack stat --endpoint

# Show top 10 endpoints sorted by hits
devtrack stat --top 10 --sort-by hits

# Show top 5 endpoints sorted by latency
devtrack stat --top 5 --sort-by latency
```

### 🏥 Health Checks
```bash
# Check database health
devtrack health

# Check database and HTTP endpoint health
devtrack health --endpoint
```

### 📚 Help
```bash
# Show comprehensive help
devtrack help

# Show help for specific command
devtrack init --help
devtrack query --help
```

---

## 🗄️ Database Integration

### DuckDB Features
- **High Performance**: Embedded database with excellent query performance
- **Zero Configuration**: No external database server required
- **ACID Compliance**: Reliable data storage
- **SQL Support**: Full SQL query capabilities
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Automatic Database Setup
DevTrack SDK automatically creates and manages the DuckDB database. No manual setup required - just install and configure the middleware.

**Stored Data Includes:**
- **Request Details**: Path, method, status code, timestamp
- **Performance Metrics**: Duration, response size, latency
- **Client Information**: IP address, user agent, referer
- **User Context**: User ID, role, authentication data
- **Request Data**: Query parameters, path parameters, request body
- **Trace Information**: Unique request identification

### Database Management
DevTrack SDK provides comprehensive database management through:

- **CLI Commands**: `devtrack init`, `devtrack reset`, `devtrack export`
- **API Endpoints**: `/__devtrack__/stats`, `/__devtrack__/logs`
- **Django Management**: `python manage.py devtrack_init`, `devtrack_stats`
- **Python API**: Direct database operations for advanced use cases

For detailed database operations and advanced usage, see our [documentation](https://devtrack-sdk.readthedocs.io/).

---

## 📊 API Endpoints

### GET /__devtrack__/stats
Returns comprehensive statistics and logs from the database.

#### Query Parameters
- `limit` (int, optional): Limit number of entries returned
- `offset` (int, default: 0): Offset for pagination
- `path_pattern` (str, optional): Filter by path pattern
- `status_code` (int, optional): Filter by status code

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

### DELETE /__devtrack__/logs/{log_id}
Delete a specific log by its ID.

#### Response Format
```json
{
    "message": "Successfully deleted log with ID 123",
    "deleted_count": 1,
    "log_id": 123
}
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Database configuration
DEVTRACK_DB_PATH=/custom/path/devtrack_logs.db

# Middleware configuration
DEVTRACK_EXCLUDE_PATHS=/health,/metrics,/admin
DEVTRACK_MAX_ENTRIES=10000

# Environment
ENVIRONMENT=production
```

### Configuration Files
```python
# config.py
import os

DEVTRACK_CONFIG = {
    'database': {
        'path': os.getenv('DEVTRACK_DB_PATH', 'devtrack_logs.db'),
        'max_entries': int(os.getenv('DEVTRACK_MAX_ENTRIES', '10000')),
    },
    'middleware': {
        'exclude_paths': os.getenv('DEVTRACK_EXCLUDE_PATHS', '').split(',') if os.getenv('DEVTRACK_EXCLUDE_PATHS') else [],
    },
    'environment': os.getenv('ENVIRONMENT', 'development'),
}
```

### Custom Configuration
```python
# Custom middleware configuration
class ConfigurableDevTrackMiddleware(DevTrackMiddleware):
    def __init__(self, app, config=None):
        self.config = config or {}
        exclude_paths = self.config.get('exclude_paths', [])
        super().__init__(app, exclude_path=exclude_paths)
    
    async def dispatch(self, request, call_next):
        # Custom logic based on configuration
        if self.config.get('enable_custom_fields', False):
            # Add custom fields
            pass
        return await super().dispatch(request, call_next)
```

---

## 🔍 Advanced Usage

### Custom Data Extraction
DevTrack SDK allows custom data extraction by extending the base extractor. You can add custom fields like request IDs, app versions, and environment information to your logs.

For detailed implementation examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Custom Database Operations
DevTrack SDK provides a flexible database interface that can be extended for custom operations like date range queries, performance metrics, and advanced analytics.

For detailed implementation examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Integration with Monitoring Tools
DevTrack SDK integrates seamlessly with popular monitoring tools like Prometheus, Grafana, and Datadog. You can extend the middleware to export metrics and integrate with your existing monitoring infrastructure.

For detailed integration examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

---

## 🔐 Security

### Security Features
- **No API Keys Required**: Basic usage doesn't require authentication
- **Automatic Data Filtering**: Sensitive data is automatically filtered
- **Configurable Exclusions**: Exclude sensitive paths from tracking
- **Environment Awareness**: Different configurations for different environments

### Sensitive Data Filtering
DevTrack SDK automatically filters sensitive fields like passwords, tokens, and API keys. You can extend the filtering to include additional sensitive fields specific to your application.

For detailed security configuration examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Access Control
DevTrack SDK endpoints can be protected with authentication and authorization. You can require login, admin access, or custom permissions for accessing statistics and log data.

For detailed access control examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Production Security Recommendations
1. **Environment Variables**: Use environment variables for sensitive configuration
2. **Access Control**: Implement proper authentication for stats endpoints
3. **Path Exclusions**: Exclude sensitive paths from tracking
4. **Monitoring**: Monitor the stats endpoint for unusual activity
5. **Data Retention**: Implement data retention policies
6. **Encryption**: Consider encrypting sensitive log data

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_middleware.py

# Run with coverage
pytest --cov=devtrack_sdk tests/

# Run with verbose output
pytest -v tests/
```

### Test Structure
```
tests/
├── __init__.py
├── test_cli.py              # CLI command tests
├── test_django_integration.py  # Django integration tests
├── test_middleware.py       # Middleware functionality tests
├── test_settings.py         # Configuration tests
├── test_urls.py            # URL pattern tests
└── test_wsgi.py           # WSGI integration tests
```

### Writing Tests
DevTrack SDK provides comprehensive testing support for both FastAPI and Django applications. You can test middleware functionality, database operations, and API endpoints using standard testing frameworks.

For detailed testing examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Integration Tests
DevTrack SDK supports integration testing for both FastAPI and Django applications. You can test middleware behavior, request tracking, and endpoint exclusions using standard testing frameworks.

For detailed integration testing examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

---

## 📈 Performance

### Performance Characteristics
- **Low Overhead**: Minimal impact on request processing time
- **Non-blocking**: Asynchronous operations don't block request handling
- **Efficient Storage**: DuckDB provides excellent query performance
- **Memory Efficient**: Configurable limits prevent memory issues

### Performance Monitoring
DevTrack SDK includes built-in performance monitoring capabilities. You can track request duration, identify slow endpoints, and monitor application performance in real-time.

For detailed performance monitoring examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

### Optimization Tips
1. **Exclude High-Traffic Paths**: Exclude health checks and metrics endpoints
2. **Limit Stored Entries**: Set reasonable limits for in-memory storage
3. **Use Database**: Use DuckDB for persistent storage instead of in-memory
4. **Batch Operations**: Batch database operations when possible
5. **Monitor Performance**: Use the built-in performance monitoring

### Memory Management
DevTrack SDK provides configurable memory management options. You can set limits on stored entries, implement custom cleanup strategies, and optimize memory usage for your specific requirements.

For detailed memory management examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

---

## 🚀 Deployment

### Docker Deployment
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
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEVTRACK_DB_PATH=/app/data/devtrack_logs.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devtrack-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: devtrack-app
  template:
    metadata:
      labels:
        app: devtrack-app
    spec:
      containers:
      - name: app
        image: devtrack-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DEVTRACK_DB_PATH
          value: "/app/data/devtrack_logs.db"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: devtrack-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: devtrack-service
spec:
  selector:
    app: devtrack-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Production Environment Variables
```bash
# .env.production
ENVIRONMENT=production
DEVTRACK_DB_PATH=/var/lib/devtrack/logs.db
DEVTRACK_EXCLUDE_PATHS=/health,/metrics,/admin
DEVTRACK_MAX_ENTRIES=10000
LOG_LEVEL=INFO
```

### Health Checks
DevTrack SDK provides built-in health check capabilities. You can monitor database connectivity, system status, and component health for production deployments.

For detailed health check examples, see our [documentation](https://devtrack-sdk.readthedocs.io/).

---

## 📚 Documentation

### Online Documentation
- **Read the Docs**: [https://devtrack-sdk.readthedocs.io](https://devtrack-sdk.readthedocs.io)
- **GitHub Repository**: [https://github.com/mahesh-solanke/devtrack-sdk](https://github.com/mahesh-solanke/devtrack-sdk)

### Local Documentation
```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme myst-parser

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### API Documentation
- **FastAPI Integration**: [docs/fastapi_integration.md](docs/fastapi_integration.md)
- **Django Integration**: [docs/django_integration.md](docs/django_integration.md)

### Examples
- **FastAPI Example**: [examples/fastapi_example.py](examples/fastapi_example.py)
- **Django Example**: [examples/django_example.py](examples/django_example.py)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup
```bash
# Clone the repository
git clone https://github.com/mahesh-solanke/devtrack-sdk.git
cd devtrack-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest flake8 black isort pre-commit

# Install pre-commit hooks
pre-commit install
```

### Code Style
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **Pre-commit**: Automated checks

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=devtrack_sdk

# Run specific test
pytest tests/test_middleware.py::test_root_logging
```

### Submitting Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/awesome-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run pre-commit checks (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m '✨ Add awesome feature'`)
7. Push to the branch (`git push origin feat/awesome-feature`)
8. Open a Pull Request

### Issue Guidelines
- Use the issue template
- Provide clear description
- Include code examples
- Specify environment details

### Pull Request Guidelines
- Use descriptive commit messages
- Include tests for new features
- Update documentation
- Ensure all checks pass

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ No liability
- ❌ No warranty

---

## 🎉 Acknowledgements

- **FastAPI**: Inspired by FastAPI's middleware design
- **Django**: Django's middleware system
- **DuckDB**: High-performance embedded database
- **Rich**: Beautiful CLI interface
- **Typer**: Modern CLI framework
- **Open Source Community**: For tooling and inspiration

---

## 📞 Support

- **GitHub Issues**: [https://github.com/mahesh-solanke/devtrack-sdk/issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **GitHub Discussions**: [https://github.com/mahesh-solanke/devtrack-sdk/discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)
- **Email**: maheshsolanke69@gmail.com

---

<div align="center">

**Made with ❤️ by [Mahesh Solanke](https://github.com/mahesh-solanke)**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mahesh-solanke)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/mahesh-solanke)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/mahesh_solanke)

</div>