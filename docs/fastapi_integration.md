# FastAPI Integration Guide

This guide shows you how to integrate DevTrack SDK v0.4.0 with your FastAPI application for comprehensive request tracking and analytics using DuckDB for persistent storage.

## Quick Start

### 1. Installation

```bash
pip install devtrack-sdk
```

### 2. Initialize Database

Initialize the DuckDB database for persistent log storage:

```bash
devtrack init --force
```

### 3. Add Middleware to Your FastAPI App

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()

# Include DevTrack router for stats endpoints
app.include_router(devtrack_router)

# Add DevTrack middleware
app.add_middleware(DevTrackMiddleware)
```

### 4. Test the Integration

Start your FastAPI server:

```bash
uvicorn main:app --reload
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

### Custom Middleware Configuration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()

# Custom middleware with exclude paths
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=[
        "/api/health",
        "/api/metrics",
        "/admin",
        "/static",
        "/media"
    ]
)
```

### Database Configuration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.database import DevTrackDB

app = FastAPI()

# Custom database path
db_path = "/custom/path/devtrack_logs.db"
db = DevTrackDB(db_path)

app.add_middleware(DevTrackMiddleware, db_instance=db)
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

### Sensitive Data Filtering

```python
from devtrack_sdk.middleware import DevTrackMiddleware

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

---

## Performance Optimization

### Exclude High-Traffic Paths

```python
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=[
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    ]
)
```

### Custom Performance Monitoring

```python
import time
from devtrack_sdk.middleware import DevTrackMiddleware

class PerformanceMonitoringMiddleware(DevTrackMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        try:
            response = await super().dispatch(request, call_next)
            
            # Log performance metrics
            duration = time.time() - start_time
            if duration > 1.0:  # Log slow requests
                print(f"Slow request: {request.url.path} took {duration:.2f}s")
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            print(f"Request failed: {request.url.path} after {duration:.2f}s: {e}")
            raise
```

---

## Integration with Monitoring Tools

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, Gauge
from devtrack_sdk.middleware import DevTrackMiddleware
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
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env.production
ENVIRONMENT=production
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
   devtrack init --force
   ```

2. **Import errors**
   ```bash
   pip install devtrack-sdk
   ```

3. **Permission errors**
   ```bash
   chmod +x /path/to/devtrack_logs.db
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Examples

### Basic FastAPI App

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI(title="My API")

# Include DevTrack router
app.include_router(devtrack_router)

# Add DevTrack middleware
app.add_middleware(DevTrackMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/users")
async def get_users():
    return {"users": ["user1", "user2"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Advanced Configuration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router
import os

app = FastAPI(title="My API", version="1.0.0")

# Environment-specific configuration
env = os.getenv('ENVIRONMENT', 'development')
exclude_paths = {
    'development': ['/docs', '/redoc', '/health'],
    'production': ['/health', '/metrics'],
    'staging': ['/health', '/admin']
}

# Include DevTrack router
app.include_router(devtrack_router)

# Add DevTrack middleware with environment-specific exclusions
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=exclude_paths.get(env, [])
)

# Your API endpoints
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/users")
async def get_users():
    return {"users": ["user1", "user2"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Resources

- **GitHub Repository**: [https://github.com/mahesh-solanke/devtrack-sdk](https://github.com/mahesh-solanke/devtrack-sdk)
- **Documentation**: [https://devtrack-sdk.readthedocs.io](https://devtrack-sdk.readthedocs.io)
- **Issues**: [https://github.com/mahesh-solanke/devtrack-sdk/issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [https://github.com/mahesh-solanke/devtrack-sdk/discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)