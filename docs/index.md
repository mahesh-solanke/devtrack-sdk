<div align="center">

![DevTrack SDK Logo](../static/devtrack-logo.png)

</div>
<div align="center">

**Comprehensive request tracking and analytics toolkit for FastAPI and Django applications**

*Built for developers who care about API usage, performance, and observability*

[![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)](https://github.com/mahesh-solanke/devtrack-sdk)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/mahesh-solanke/devtrack-sdk/blob/main/LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/devtrack-sdk)](https://pepy.tech/projects/devtrack-sdk)

</div>

---

## 🌟 Features

### ✨ Core Features
- **Zero Configuration**: Works out of the box with sensible defaults
- **Dual Framework Support**: FastAPI and Django middleware
- **Real-Time Dashboard**: Interactive dashboard at `/__devtrack__/dashboard` with live metrics
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

### 4. Access Dashboard
Once your app is running, visit:
```
http://localhost:8000/__devtrack__/dashboard
```

The dashboard provides real-time insights into your API performance with interactive charts and metrics.

### 5. Start Monitoring (Optional)
```bash
devtrack monitor --interval 3
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

## 📊 API Endpoints

### GET /__devtrack__/dashboard
Serves the built-in real-time dashboard with interactive charts and metrics.

**Features:**
- Traffic overview with time-series charts
- Error trends and top failing routes
- Performance metrics (p50/p95/p99 latency)
- Consumer segmentation analysis
- Searchable request logs table
- Auto-refresh functionality

**Access:** Visit `http://localhost:8000/__devtrack__/dashboard` after starting your application.

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
            "method": "GET",
            "status_code": 200,
            "timestamp": "2024-01-01T10:00:00Z",
            "duration_ms": 150.5
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

### GET /__devtrack__/metrics/traffic
Get traffic metrics over time.

**Query Parameters:**
- `hours` (int, default: 24): Number of hours to look back

**Response:** Returns traffic counts grouped by time intervals.

### GET /__devtrack__/metrics/errors
Get error trends and top failing routes.

**Query Parameters:**
- `hours` (int, default: 24): Number of hours to look back

**Response:** Returns error trends over time and top failing routes.

### GET /__devtrack__/metrics/perf
Get performance metrics (p50/p95/p99 latency).

**Query Parameters:**
- `hours` (int, default: 24): Number of hours to look back

**Response:** Returns latency percentiles over time and overall statistics.

### GET /__devtrack__/consumers
Get consumer segmentation data.

**Query Parameters:**
- `hours` (int, default: 24): Number of hours to look back

**Response:** Returns consumer segments with request counts, error rates, and latency metrics.

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

### FastAPI Configuration
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

### Django Configuration
```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

# DevTrack configuration
DEVTRACK_DB_PATH = 'devtrack_logs.db'
```

---

## 🔍 Advanced Usage

### Custom Data Extraction
```python
from devtrack_sdk.middleware.extractor import extract_devtrack_log_data
from datetime import datetime, timezone
import uuid

async def custom_extract_log_data(request, response, start_time):
    # Get base data
    log_data = await extract_devtrack_log_data(request, response, start_time)
    
    # Add custom fields
    log_data.update({
        "custom_field": "custom_value",
        "request_id": str(uuid.uuid4()),
        "app_version": "1.0.0",
        "environment": "production",
    })
    
    return log_data
```

### Integration with Monitoring Tools
```python
# Prometheus integration
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
request_count = Counter('devtrack_requests_total', 'Total requests', ['method', 'path', 'status'])
request_duration = Histogram('devtrack_request_duration_seconds', 'Request duration')
active_requests = Gauge('devtrack_active_requests', 'Active requests')

class PrometheusDevTrackMiddleware(DevTrackMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        active_requests.inc()
        
        try:
            response = await super().dispatch(request, call_next)
            
            # Record metrics
            request_count.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code
            ).inc()
            
            request_duration.observe(time.time() - start_time)
            
            return response
        finally:
            active_requests.dec()
```

---

## 🔐 Security

### Security Features
- **No API Keys Required**: Basic usage doesn't require authentication
- **Automatic Data Filtering**: Sensitive data is automatically filtered
- **Configurable Exclusions**: Exclude sensitive paths from tracking
- **Environment Awareness**: Different configurations for different environments

### Sensitive Data Filtering
```python
# Automatically filtered fields
SENSITIVE_FIELDS = ['password', 'token', 'secret', 'key', 'api_key']

# Custom filtering
class SecureDevTrackMiddleware(DevTrackMiddleware):
    async def dispatch(self, request, call_next):
        response = await super().dispatch(request, call_next)
        
        # Additional filtering
        if hasattr(response, 'log_data') and 'request_body' in response.log_data:
            body = response.log_data['request_body']
            for field in ['ssn', 'credit_card', 'api_key']:
                if field in body:
                    body[field] = '***FILTERED***'
        
        return response
```

### Access Control
```python
# FastAPI - Protect DevTrack endpoints
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_admin_token(credentials = Depends(security)):
    if not is_admin_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Admin access required")

# Protect DevTrack endpoints
app.include_router(
    devtrack_router,
    dependencies=[Depends(verify_admin_token)]
)
```

---

## 📈 Performance

### Performance Characteristics
- **Low Overhead**: Minimal impact on request processing time
- **Non-blocking**: Asynchronous operations don't block request handling
- **Efficient Storage**: DuckDB provides excellent query performance
- **Memory Efficient**: Configurable limits prevent memory issues

### Optimization Tips
1. **Exclude High-Traffic Paths**: Exclude health checks and metrics endpoints
2. **Limit Stored Entries**: Set reasonable limits for in-memory storage
3. **Use Database**: Use DuckDB for persistent storage instead of in-memory
4. **Batch Operations**: Batch database operations when possible
5. **Monitor Performance**: Use the built-in performance monitoring

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

### Production Environment Variables
```bash
# .env.production
ENVIRONMENT=production
DEVTRACK_DB_PATH=/var/lib/devtrack/logs.db
DEVTRACK_EXCLUDE_PATHS=/health,/metrics,/admin
DEVTRACK_MAX_ENTRIES=10000
LOG_LEVEL=INFO
```

---

## 📚 Documentation Sections

```{toctree}
:maxdepth: 2
:caption: Integration Guides

fastapi_integration
django_integration
```

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

### Submitting Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/awesome-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run pre-commit checks (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m '✨ Add awesome feature'`)
7. Push to the branch (`git push origin feat/awesome-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mahesh-solanke/devtrack-sdk/blob/main/LICENSE) file for details.

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