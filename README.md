<div align="center">

![DevTrack SDK Logo](https://raw.githubusercontent.com/mahesh-solanke/devtrack-sdk/main/static/devtrack-logo.png)

</div>
<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Version](https://img.shields.io/badge/version-0.4.2-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](/LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/devtrack-sdk)](https://pepy.tech/projects/devtrack-sdk)
[![Documentation](https://img.shields.io/badge/docs-github-blue.svg)](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-black.svg)](https://github.com/mahesh-solanke/devtrack-sdk/issues)
[![GitHub Pull Requests](https://img.shields.io/badge/GitHub-PRs-black.svg)](https://github.com/mahesh-solanke/devtrack-sdk/pulls)

**Comprehensive request tracking and analytics toolkit for FastAPI and Django applications**

*Built for developers who care about API usage, performance, and observability*

📖 **[View Documentation](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)** | 🚀 **[Quick Start](#-quick-start)** | 🛠️ **[CLI Toolkit](#️-cli-toolkit)**

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
- [📈 Performance](#-performance)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Features

### ✨ Core Features
- **Zero Configuration**: Works out of the box with sensible defaults
- **Dual Framework Support**: FastAPI and Django middleware
- **Real-Time Dashboard**: Interactive dashboard at `/__devtrack__/dashboard` with live metrics
- **Advanced Querying**: Filter and search logs with multiple criteria
- **Export Capabilities**: Export logs to JSON or CSV formats
- **Health Monitoring**: System health checks and component status
- **CLI Toolkit**: 8 powerful commands for managing your DevTrack instance

### 🗄️ Database Features
- **DuckDB Integration**: High-performance embedded database
- **Persistent Storage**: Data survives application restarts
- **Advanced Analytics**: Built-in statistical analysis

### 🎯 Tracking Capabilities
- **Comprehensive Logging**: 15+ fields per request
- **Performance Metrics**: Duration, response size, latency tracking
- **User Context**: User ID, role, and authentication data
- **Request Details**: Path parameters, query params, request body
- **Client Information**: IP address, user agent, referer

---

## 🚀 Quick Start

### 1. Install DevTrack SDK
```bash
pip install devtrack-sdk
```

### 2. Choose Your Framework

#### FastAPI
```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

#### Django
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
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=['/docs', '/redoc', '/health']
)
```

### Django Integration

#### Basic Setup
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

For custom middleware and advanced configurations, see the [documentation](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs).

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

**Query Parameters:**
- `limit` (int, optional): Limit number of entries returned
- `offset` (int, default: 0): Offset for pagination
- `path_pattern` (str, optional): Filter by path pattern
- `status_code` (int, optional): Filter by status code

**Response:** Returns summary statistics and log entries array.

### DELETE /__devtrack__/logs
Delete logs from the database with various filtering options.

**Query Parameters:**
- `all_logs` (bool, default: false): Delete all logs
- `path_pattern` (str, optional): Delete logs by path pattern
- `status_code` (int, optional): Delete logs by status code
- `older_than_days` (int, optional): Delete logs older than N days
- `log_ids` (str, optional): Comma-separated list of log IDs to delete

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

For detailed API documentation, see the [documentation](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs).

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

### Exclude Paths
You can exclude specific paths from tracking:

```python
# FastAPI
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=['/docs', '/redoc', '/health']
)

# Django
class CustomDevTrackMiddleware(DevTrackDjangoMiddleware):
    def __init__(self, get_response=None):
        exclude_paths = ['/health', '/metrics', '/admin']
        super().__init__(get_response, exclude_path=exclude_paths)
```

### Custom Configuration
```python
# Custom middleware configuration
class ConfigurableDevTrackMiddleware(DevTrackMiddleware):
    def __init__(self, app, config=None):
        self.config = config or {}
        exclude_paths = self.config.get('exclude_paths', [])
        super().__init__(app, exclude_path=exclude_paths)
```

---

## 🔍 Advanced Usage

### Custom Data Extraction
DevTrack SDK allows custom data extraction by extending the base extractor. You can add custom fields like request IDs, app versions, and environment information to your logs.

### Custom Database Operations
DevTrack SDK provides a flexible database interface that can be extended for custom operations like date range queries, performance metrics, and advanced analytics.

### Integration with Monitoring Tools
DevTrack SDK integrates seamlessly with popular monitoring tools like Prometheus, Grafana, and Datadog. You can extend the middleware to export metrics and integrate with your existing monitoring infrastructure.

---

## 🔐 Security

### Security Features
- **No API Keys Required**: Basic usage doesn't require authentication
- **Automatic Data Filtering**: Sensitive data is automatically filtered
- **Configurable Exclusions**: Exclude sensitive paths from tracking
- **Environment Awareness**: Different configurations for different environments

### Sensitive Data Filtering
DevTrack SDK automatically filters sensitive fields like passwords, tokens, and API keys. You can extend the filtering to include additional sensitive fields specific to your application.

### Access Control
DevTrack SDK endpoints can be protected with authentication and authorization. You can require login, admin access, or custom permissions for accessing statistics and log data.

### Production Security Recommendations
1. **Environment Variables**: Use environment variables for sensitive configuration
2. **Access Control**: Implement proper authentication for stats endpoints
3. **Path Exclusions**: Exclude sensitive paths from tracking
4. **Monitoring**: Monitor the stats endpoint for unusual activity
5. **Data Retention**: Implement data retention policies
6. **Encryption**: Consider encrypting sensitive log data

---

## 📈 Performance

### Performance Characteristics
- **Low Overhead**: Minimal impact on request processing time
- **Non-blocking**: Asynchronous operations don't block request handling
- **Efficient Storage**: DuckDB provides excellent query performance
- **Memory Efficient**: Configurable limits prevent memory issues

### Performance Monitoring
DevTrack SDK includes built-in performance monitoring capabilities. You can track request duration, identify slow endpoints, and monitor application performance in real-time.

### Optimization Tips
1. **Exclude High-Traffic Paths**: Exclude health checks and metrics endpoints
2. **Limit Stored Entries**: Set reasonable limits for in-memory storage
3. **Use Database**: Use DuckDB for persistent storage instead of in-memory
4. **Batch Operations**: Batch database operations when possible
5. **Monitor Performance**: Use the built-in performance monitoring

### Memory Management
DevTrack SDK provides configurable memory management options. You can set limits on stored entries, implement custom cleanup strategies, and optimize memory usage for your specific requirements.

### Production Environment Variables
```bash
ENVIRONMENT=production
DEVTRACK_DB_PATH=/var/lib/devtrack/logs.db
DEVTRACK_EXCLUDE_PATHS=/health,/metrics,/admin
DEVTRACK_MAX_ENTRIES=10000
LOG_LEVEL=INFO
```

---

## 📚 Documentation

- **GitHub Repository**: [https://github.com/mahesh-solanke/devtrack-sdk](https://github.com/mahesh-solanke/devtrack-sdk)
- **Documentation Files**: [https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
- **FastAPI Integration**: [docs/fastapi_integration.md](docs/fastapi_integration.md)
- **Django Integration**: [docs/django_integration.md](docs/django_integration.md)
- **Examples**: [examples/](examples/)



---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup
```bash
git clone https://github.com/mahesh-solanke/devtrack-sdk.git
cd devtrack-sdk
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pip install pytest flake8 black isort pre-commit
pre-commit install
```

### Running Tests
```bash
pytest
pytest --cov=devtrack_sdk
```

### Submitting Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/awesome-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m '✨ Add awesome feature'`)
6. Push to the branch (`git push origin feat/awesome-feature`)
7. Open a Pull Request

For detailed contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📅 Release Timeline

- See the full roadmap and release plan in **[RoadMap](./docs/release/ROADMAP.md)**

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
- **LinkedIn Company**: [DevTrackHQ](https://www.linkedin.com/company/devtrackhq/)
- **Email**: [Contact me](https://linkedin.com/in/mahesh-solanke-200697)

---

<div align="center">

**Made with ❤️ by [Mahesh Solanke](https://github.com/mahesh-solanke)**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mahesh-solanke)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/mahesh-solanke-200697)
[![DevTrackHQ](https://img.shields.io/badge/DevTrackHQ-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/devtrackhq/)

</div>