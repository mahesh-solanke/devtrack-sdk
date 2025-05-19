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
- [🚀 Deployment](#deployment)
- [🎈 Usage](#usage)
- [📊 Logged Fields](#logged_fields)
- [🧪 Testing](#tests)
- [⛏️ Built Using](#built_using)
- [✅ TODO](#todo)
- [🤝 Contributing](#contributing)
- [✍️ Authors](#authors)
- [🎉 Acknowledgements](#acknowledgement)

---

## 🧐 About <a name="about"></a>

**DevTrack SDK** is a powerful and lightweight middleware for FastAPI apps that automatically logs HTTP requests. Track path, method, status, duration, user agent, and more — right from your app with no extra configuration.

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
app.add_middleware(DevTrackMiddleware, api_key="dummy-key")
```

---

## 🚀 Deployment <a name="deployment"></a>

```bash
uvicorn main:app --reload
```

Then test with:

```bash
curl http://localhost:8000/__devtrack__/stats
```

---

## 🎈 Usage <a name="usage"></a>

All tracked data is stored in memory and served via:

```
GET /__devtrack__/stats
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
- `user_id`, `role`: if available from headers or token
- `trace_id`: unique ID for each request

---

## ⛏️ Built Using <a name="built_using"></a>

- 🔹 [FastAPI](https://fastapi.tiangolo.com/)
- 🔹 [Starlette](https://www.starlette.io/)
- 🔹 [httpx](https://www.python-httpx.org/)

---

## ✅ TODO <a name="todo"></a>
Here are the upcoming features and improvements planned for DevTrack SDK:

- [x] In-memory logging
- [x] Full request metadata (duration, headers, etc.)
- [ ] 🚫 Exclude specific paths from tracking (e.g., `/docs`, `/health`, `/metrics`)
- [ ] ⏱️ Track latency percentiles (P50, P95, P99) and categorize response time (fast / average / slow)
- [ ] 🧩 Support a `devtrack.json` config file for path exclusions and other settings
- [ ] 🔐 Token-based authentication for `/__devtrack__/stats`
- [ ] 🧪 Add more unit tests (e.g., request size, content-type tracking, failure simulation)
- [ ] 🧰 CLI support: `devtrack stats`, `devtrack init`
- [ ] 🎯 `@track()` decorator for selective endpoint tracking
- [ ] 📈 Rich dashboard UI with charts and filters for visualizing real-time stats
- [ ] 💾 Optional database support: SQLite and PostgreSQL
- [ ] 📦 Add plugin system for log exporters (e.g., file, Prometheus, cloud)

---
## 💡 Suggestions Welcome!

Have an idea to improve DevTrack SDK?  
We’d love to hear from you — whether it’s a feature request, performance tweak, or integration idea.

👉 [Open an issue](https://github.com/mahesh-solanke/devtrack-sdk/issues/new) to share your thoughts  
or  
💬 Join the discussion in [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions) *(if enabled)*

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

- [Mahesh Solanke](https://github.com/mahesh-solanke) - Core Dev & Maintainer

---

## 🎉 Acknowledgements <a name="acknowledgement"></a>

- ✨ Inspired by [Fast API's](https://github.com/fastapi/fastapi) middleware design
- 💡 Thanks to the open-source community for tooling and inspiration
