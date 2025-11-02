# DevTrack SDK Examples

This directory contains example applications demonstrating DevTrack SDK v0.3.0 integration with different frameworks.

## Available Examples

### 1. Django Example (`django_example.py`)

A complete Django application with DevTrack SDK DuckDB integration.

#### Features
- ✅ DuckDB persistent storage
- ✅ Real-time monitoring
- ✅ Advanced querying
- ✅ Export capabilities
- ✅ Health checks
- ✅ CLI toolkit (8 commands)

#### API Endpoints
- `GET /` - Home page with feature overview
- `GET /api/users/` - Users list
- `GET /api/posts/` - Posts list
- `GET /api/error/` - Error test endpoint
- `GET /api/slow/` - Slow endpoint test
- `GET /api/health/` - Health check

#### DevTrack Endpoints
- `GET /__devtrack__/stats` - View statistics
- `POST /__devtrack__/track` - Manual tracking
- `DELETE /__devtrack__/logs` - Delete logs

#### Running the Example

```bash
# Run the Django example
python examples/django_example.py

# Or with gunicorn
gunicorn examples.django_example:application
```

#### Testing Endpoints

```bash
# Test home page
curl http://localhost:8000/

# Test users endpoint
curl http://localhost:8000/api/users/

# Test error endpoint
curl http://localhost:8000/api/error/

# View DevTrack statistics
curl http://localhost:8000/__devtrack__/stats

# View limited statistics
curl http://localhost:8000/__devtrack__/stats?limit=5
```

#### Django Management Commands

```bash
# Initialize database
python manage.py devtrack_init --force

# Show statistics
python manage.py devtrack_stats --limit 20

# Reset database
python manage.py devtrack_reset --yes
```

#### CLI Commands

```bash
# Show version info
devtrack version

# Initialize database
devtrack init --force

# Real-time monitoring
devtrack monitor

# Query logs
devtrack query --limit 10

# Export logs
devtrack export --format json

# Show statistics
devtrack stat --endpoint

# Health check
devtrack health --endpoint
```

### 2. FastAPI Example (`fastapi_example.py`)

A FastAPI application with DevTrack SDK integration.

#### Running the Example

```bash
# Run the FastAPI example
python examples/fastapi_example.py

# Or with uvicorn
uvicorn examples.fastapi_example:app --reload
```

## Configuration

### Environment Variables

```bash
# Database path
DEVTRACK_DB_PATH=devtrack_logs.db

# Environment
ENVIRONMENT=development
```

### Django Settings

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

INSTALLED_APPS = [
    # ... other apps
    'devtrack_sdk',
]

# DevTrack configuration
DEVTRACK_DB_PATH = 'devtrack_logs.db'
```

### FastAPI Integration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

## Features Demonstrated

### 1. Request Tracking
- Automatic request logging
- Performance metrics
- Error tracking
- User context

### 2. Database Operations
- DuckDB initialization
- Log insertion
- Query operations
- Statistics generation

### 3. API Endpoints
- Statistics retrieval
- Log deletion
- Manual tracking
- Health checks

### 4. CLI Integration
- Database management
- Real-time monitoring
- Export capabilities
- Health monitoring

## Testing

### Manual Testing

```bash
# Test various endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/users/
curl http://localhost:8000/api/error/
curl http://localhost:8000/__devtrack__/stats
```

### Automated Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=devtrack_sdk tests/
```

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
   chmod +x examples/django_example.py
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Documentation

- [DevTrack SDK Documentation](https://devtrack-sdk.readthedocs.io)
- [GitHub Repository](https://github.com/mahesh-solanke/devtrack-sdk)
- [Django Integration Guide](../docs/django_integration.md)
- [FastAPI Integration Guide](../docs/fastapi_integration.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.
