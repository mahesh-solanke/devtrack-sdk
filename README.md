<h1 align="center">🚀 DevTrack SDK</h1>

<p align="center">
  Plug-and-play request tracking middleware for FastAPI apps. <br>
  <i>Built for devs who care about API usage, performance, and observability.</i>
</p>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/mahesh-solanke/devtrack-sdk.svg)](https://github.com/mahesh-solanke/devtrack-sdk/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/mahesh-solanke/devtrack-sdk.svg)](https://github.com/mahesh-solanke/devtrack-sdk/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

## 🧭 Table of Contents

- [🧐 About](#about)
- [🏁 Getting Started](#getting_started)
- [🔧 Configuration](#configuration)
- [🚀 Deployment](#deployment)
- [🎈 Usage & CLI Tool](#usage)
- [📊 Logged Fields](#logged_fields)
- [🔐 Security](#security)
- [🧪 Testing](#testing)
- [⛏️ Built Using](#built_using)
- [✅ TODO](#todo)
- [🤝 Contributing](#contributing)
- [✍️ Authors](#authors)
- [🎉 Acknowledgements](#acknowledgement)

---

## 🧐 About <a name="about"></a>

**DevTrack SDK** is a powerful and lightweight middleware for FastAPI apps that automatically logs HTTP requests. Track path, method, status, duration, user agent, and more — right from your app with no extra configuration. Perfect for development, testing, and production environments.

Key Features:
- ✨ Zero configuration required
- 🚀 Lightweight and non-blocking
- 📊 Comprehensive request tracking
- 🔒 Security-first design
- 🎯 Easy integration with FastAPI

---

## 🏁 Getting Started <a name="getting_started"></a>

### 🧰 Prerequisites

```bash
python >= 3.8
pip install fastapi httpx starlette
```

### 📥 Installation

```bash
pip install devtrack-sdk
```

### 🧩 Middleware Integration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

That's it! Your app is now tracking requests automatically.

---

## 🔧 Configuration <a name="configuration"></a>

### Basic Configuration

The middleware works out of the box with sensible defaults. You can customize it by passing options:

```python
app.add_middleware(
    DevTrackMiddleware,
    exclude_path=["/endpoint1", "/endpoint2"]  # Paths to exclude from tracking
)
```

### Environment-based Settings

For different environments, you can configure the middleware accordingly:

```python
import os

middleware_config = {
    "development": {
        "skip_paths": ["/docs", "/redoc", "/health"],
    },
    "production": {
        "skip_paths": ["/health", "/metrics"],
    }
}

env = os.getenv("ENV", "development")
app.add_middleware(DevTrackMiddleware, exclude_path=middleware_config[env]["skip_paths"])
```

---

## 🚀 Deployment <a name="deployment"></a>

```bash
uvicorn main:app --reload
```

Test the tracking endpoint:

```bash
curl http://localhost:8000/__devtrack__/stats
```

---

## 🎈 Usage & CLI Tool <a name="usage"></a>

### CLI Tool

DevTrack SDK now comes with a CLI tool (available as the "devtrack" command) to help you manage your project. For example, you can run:

```bash
devtrack -- version
```

to display the current SDK version, or

```bash
devtrack stat
```

to detect and display stats (for example, from your local endpoint).

Below is a demo screenshot of the CLI tool in action:

![CLI Demo](static/CLIDemo.png)

### Accessing Stats

All tracked data is stored in memory and served via:

```
GET /__devtrack__/stats
```

Response format:
```json
{
    "total": 42,
    "entries": [
        {
            "path": "/api/users",
            "method": "GET",
            "status_code": 200,
            "timestamp": "2024-03-20T10:00:00Z",
            "duration_ms": 150.5,
            // ... other fields
        }
    ]
}
```

---

## 📊 Logged Fields <a name="logged_fields"></a>

Each request is logged with these fields:

- `path`: request endpoint
- `method`: HTTP method (GET, POST, etc.)
- `status_code`: HTTP response code
- `timestamp`: ISO timestamp (UTC)
- `client_ip`: origin IP address
- `duration_ms`: time taken for request to complete
- `user_agent`: browser/client making the request
- `referer`: previous page (if any)
- `query_params`: any query string data
- `request_body`: POST/PUT payload (filtered)
- `response_size`: response size in bytes
- `user_id`, `role`: if available from headers
- `trace_id`: unique ID for each request

---

## 🔐 Security <a name="security"></a>

DevTrack SDK is designed with security in mind:

- 🔒 No API keys required for basic usage
- 🛡️ Automatic filtering of sensitive data
- 🔐 Optional authentication for stats endpoint (coming soon)
- 🚫 Configurable path exclusions
- 🔍 Environment-aware configuration

For production deployments, we recommend:
- Using environment variables for configuration
- Implementing proper access control for the stats endpoint
- Excluding sensitive paths from tracking
- Monitoring the stats endpoint for unusual activity

---

## 🧪 Testing <a name="testing"></a>

Run the test suite:

```bash
pytest tests/
```

The SDK includes comprehensive tests for:
- Middleware functionality
- Request tracking
- Path exclusions
- Error handling
- Performance impact

---

## ⛏️ Built Using <a name="built_using"></a>

- 🔹 [FastAPI](https://fastapi.tiangolo.com/) – Modern, fast web framework
- 🔹 [Starlette](https://www.starlette.io/) – ASGI framework/toolkit
- 🔹 [httpx](https://www.python-httpx.org/) – Modern HTTP client

---

## ✅ TODO <a name="todo"></a>

Upcoming features and improvements:

- [x] In-memory logging
- [x] Full request metadata
- [x] Simplified configuration
- [x] 🚫 Path exclusion patterns
- [x] 🧰 CLI tool (with "version" and "stat" commands)
- [ ] ⏱️ Latency percentiles (P50, P95, P99)
- [ ] 🧩 `devtrack.json` configuration
- [ ] 🔐 Token-based authentication
- [ ] 🎯 `@track()` decorator
- [ ] 📈 Dashboard UI
- [ ] 💾 Database support
- [ ] 📦 Log exporters

For more detailed plans and tasks, please refer to the [TODO](./TODO) in the project repository.

---

## 💡 Suggestions Welcome!

Have an idea to improve DevTrack SDK?  
We'd love to hear from you — whether it's a feature request, performance tweak, or integration idea.

👉 [Open an issue](https://github.com/mahesh-solanke/devtrack-sdk/issues/new) to share your thoughts  
or  
💬 Join the discussion in [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions) 

Together we can make DevTrack even better for the FastAPI ecosystem. 🚀

---

## 🤝 Contributing <a name="contributing"></a>

We ❤️ contributions! Please:

1. Fork this repo
2. Create your branch (`git checkout -b feat/awesome-feature`)
3. Commit your changes (`git commit -m '✨ Add awesome feature'`)
4. Push to the branch (`git push origin feat/awesome-feature`)
5. Open a Pull Request

Run `pre-commit run --all-files` before committing 🙏

---

## ✍️ Authors <a name="authors"></a>

- [Mahesh Solanke](https://github.com/mahesh-solanke) – Core Dev & Maintainer

---

## 🎉 Acknowledgements <a name="acknowledgement"></a>

- ✨ Inspired by [FastAPI's](https://github.com/fastapi/fastapi) middleware design
- 💡 Thanks to the open-source community for tooling and inspiration
