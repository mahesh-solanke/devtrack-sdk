# DevTrack SDK Documentation

Welcome to the DevTrack SDK documentation!

## Overview

DevTrack SDK is a comprehensive request tracking and analytics toolkit for FastAPI and Django applications. It provides real-time monitoring, detailed logging, and powerful CLI tools for API observability.

## Features

- 🚀 **Zero Configuration**: Works out of the box with sensible defaults
- 📊 **Real-time Monitoring**: Live dashboard with customizable refresh intervals
- 🗄️ **DuckDB Integration**: High-performance embedded database for log storage
- 🔍 **Advanced Querying**: Filter and search logs with multiple criteria
- 📤 **Export Capabilities**: Export logs to JSON or CSV formats
- 🏥 **Health Checks**: Monitor system health and component status
- ⚙️ **CLI Toolkit**: 8 powerful commands for managing your DevTrack instance

## Quick Start

### Installation

```bash
pip install devtrack-sdk
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

### Django Integration

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

## CLI Commands

The DevTrack CLI provides 8 powerful commands:

- `devtrack version` - Show SDK version and build information
- `devtrack init` - Initialize a new DevTrack database
- `devtrack reset` - Reset the DevTrack database
- `devtrack export` - Export logs to JSON or CSV
- `devtrack query` - Query logs with advanced filtering
- `devtrack monitor` - Real-time monitoring dashboard
- `devtrack stat` - Display comprehensive API statistics
- `devtrack health` - Check system health and status

## Documentation Sections

- [FastAPI Integration](fastapi_integration.md) - Complete FastAPI setup guide
- [Django Integration](django_integration.md) - Complete Django setup guide

## Getting Help

- **GitHub**: [https://github.com/mahesh-solanke/devtrack-sdk](https://github.com/mahesh-solanke/devtrack-sdk)
- **Issues**: [https://github.com/mahesh-solanke/devtrack-sdk/issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [https://github.com/mahesh-solanke/devtrack-sdk/discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)

## Version

Current version: **0.3.0**

## License

MIT License - see [LICENSE](../LICENSE) for details.
