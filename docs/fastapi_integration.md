# FastAPI Integration Guide

This guide shows you how to integrate DevTrack SDK with your FastAPI application for comprehensive request tracking and analytics.

## Quick Start

### 1. Installation

```bash
pip install devtrack-sdk
```

### 2. Add Middleware to Your FastAPI App

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

### 3. Test the Integration

Start your FastAPI server:

```bash
uvicorn main:app --reload
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
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()

# Exclude specific paths from tracking
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=[
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
)
```

### Environment-Specific Configuration

Configure different exclude paths for different environments:

```python
import os
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

# Environment-specific exclude paths
EXCLUDE_PATHS = {
    'development': [
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/health",
        "/debug"
    ],
    'production': [
        "/health",
        "/metrics",
        "/admin"
    ],
    'staging': [
        "/health",
        "/admin"
    ]
}

app = FastAPI()

env = os.getenv('ENV', 'development')
exclude_paths = EXCLUDE_PATHS.get(env, [])

app.add_middleware(DevTrackMiddleware, exclude_path=exclude_paths)
```

### Custom Middleware Configuration

For more advanced customization, you can subclass the middleware:

```python
from fastapi import FastAPI
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
                "custom_field": "custom_value",
                "request_id": str(uuid.uuid4()),
            })
            
            DevTrackMiddleware.stats.append(log_data)
        except Exception as e:
            print(f"[CustomDevTrackMiddleware] Logging error: {e}")
        
        return response

app = FastAPI()
app.add_middleware(CustomDevTrackMiddleware)
```

## API Endpoints

### GET /__devtrack__/stats

Returns all tracked request data:

```json
{
    "total": 42,
    "entries": [
        {
            "path": "/api/users",
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

## Integration with FastAPI Features

### Path Parameters and Query Parameters

FastAPI automatically captures path and query parameters:

```python
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(DevTrackMiddleware)

class User(BaseModel):
    name: str
    email: str

@app.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., description="User ID"),
    include_details: bool = Query(False, description="Include user details")
):
    return {"user_id": user_id, "include_details": include_details}

@app.post("/users")
async def create_user(user: User):
    return {"message": "User created", "user": user}
```

The middleware will track:
- Path parameters: `{"user_id": 123}`
- Query parameters: `{"include_details": true}`
- Request body: `{"name": "John", "email": "john@example.com"}`

### Authentication and User Context

If you're using FastAPI's authentication, the middleware can capture user information:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()
app.add_middleware(DevTrackMiddleware)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Your authentication logic here
    token = credentials.credentials
    # Validate token and return user
    return {"user_id": "123", "role": "admin"}

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": "This is protected", "user": current_user}
```

### Background Tasks

FastAPI background tasks are also tracked:

```python
from fastapi import FastAPI, BackgroundTasks
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()
app.add_middleware(DevTrackMiddleware)

def send_notification(email: str, message: str):
    # Background task logic
    pass

@app.post("/notifications")
async def create_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email, message)
    return {"message": "Notification scheduled"}
```

## Security Considerations

### Sensitive Data Filtering

The middleware automatically filters sensitive data:

```python
# Automatically filtered fields
SENSITIVE_FIELDS = ['password', 'token', 'secret', 'key']

# Custom filtering in middleware
class SecureDevTrackMiddleware(DevTrackMiddleware):
    async def dispatch(self, request, call_next):
        # ... existing logic ...
        
        # Additional filtering
        if 'request_body' in log_data:
            body = log_data['request_body']
            for field in ['ssn', 'credit_card', 'api_key']:
                if field in body:
                    body[field] = '***FILTERED***'
        
        return response
```

### Access Control

Consider adding authentication to the stats endpoint in production:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
security = HTTPBearer()

async def verify_admin_token(credentials = Depends(security)):
    # Verify admin token
    if not is_admin_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Admin access required")

# Protect DevTrack endpoints
app.include_router(
    devtrack_router,
    dependencies=[Depends(verify_admin_token)]
)
```

## Performance Considerations

### Memory Management

The middleware stores data in memory. For production applications:

```python
from collections import deque
from devtrack_sdk.middleware import DevTrackMiddleware

class LimitedDevTrackMiddleware(DevTrackMiddleware):
    MAX_ENTRIES = 1000
    
    async def dispatch(self, request, call_next):
        # ... existing logic ...
        
        # Limit stored entries
        if len(DevTrackMiddleware.stats) >= self.MAX_ENTRIES:
            DevTrackMiddleware.stats.pop(0)  # Remove oldest entry
        
        return response
```

### Async Support

FastAPI is built on async/await, and the middleware fully supports it:

```python
import asyncio
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()
app.add_middleware(DevTrackMiddleware)

@app.get("/async-example")
async def async_endpoint():
    await asyncio.sleep(0.1)  # Simulate async work
    return {"message": "Async response"}
```

## Testing

### Unit Tests

```python
from fastapi.testclient import TestClient
from devtrack_sdk.middleware import DevTrackMiddleware

def test_middleware_tracking():
    from fastapi import FastAPI
    
    app = FastAPI()
    app.add_middleware(DevTrackMiddleware)
    
    client = TestClient(app)
    
    # Make a request
    response = client.get("/test")
    
    # Check that stats were recorded
    stats_response = client.get("/__devtrack__/stats")
    stats = stats_response.json()
    
    assert stats["total"] > 0
    assert len(stats["entries"]) > 0
```

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from devtrack_sdk.middleware import DevTrackMiddleware

@pytest.fixture
def client():
    from fastapi import FastAPI
    
    app = FastAPI()
    app.add_middleware(DevTrackMiddleware)
    
    return TestClient(app)

def test_stats_endpoint(client):
    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "entries" in data

def test_track_endpoint(client):
    test_data = {"test": "data"}
    response = client.post("/__devtrack__/track", json=test_data)
    assert response.status_code == 200
    assert response.json()["ok"] == True
```

## Deployment

### Production Configuration

```python
import os
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()

# Production middleware configuration
if os.getenv('ENVIRONMENT') == 'production':
    app.add_middleware(
        DevTrackMiddleware,
        exclude_path=[
            "/health",
            "/metrics",
            "/admin"
        ]
    )
else:
    # Development configuration
    app.add_middleware(DevTrackMiddleware)
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env
ENVIRONMENT=production
DEVTRACK_MAX_ENTRIES=1000
DEVTRACK_EXCLUDE_PATHS=/health,/metrics
```

## Troubleshooting

### Common Issues

1. **Middleware not tracking requests**
   - Check that middleware is added before other middleware
   - Verify paths are not in exclude list

2. **Import errors**
   - Ensure all dependencies are installed: `pip install fastapi httpx starlette`
   - Check Python version compatibility

3. **Performance issues**
   - Consider limiting stored entries
   - Exclude high-traffic paths

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('devtrack_sdk')
```

## Best Practices

1. **Environment Configuration**: Use different exclude paths for different environments
2. **Security**: Always filter sensitive data and consider access control
3. **Performance**: Monitor memory usage and limit stored entries
4. **Testing**: Include DevTrack in your test suite
5. **Documentation**: Document your custom configurations

## Migration from Django

If you're migrating from Django to FastAPI:

1. Replace `DevTrackDjangoMiddleware` with `DevTrackMiddleware`
2. Update middleware configuration in FastAPI app
3. Include FastAPI router instead of Django URL patterns
4. Update any custom data extraction logic

The API endpoints and data format remain the same, ensuring a smooth transition.

## CLI Tool Integration

DevTrack SDK includes a CLI tool for managing your project:

```bash
# Display version
devtrack --version

# Get stats from local endpoint
devtrack stat

# Get stats from remote endpoint
devtrack stat --url http://api.example.com/__devtrack__/stats
```

The CLI tool works with both FastAPI and Django integrations! 