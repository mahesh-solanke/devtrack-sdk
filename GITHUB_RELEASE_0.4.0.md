# 🚀 DevTrack SDK v0.4.0 - Pulse Release

## 📊 Built-in Real-Time Dashboard

DevTrack SDK v0.4.0 introduces a **beautiful, interactive dashboard** that gives you real-time insights into your API performance - no external tools required!

### ✨ What's New

- **📈 Real-Time Dashboard** at `/__devtrack__/dashboard`
  - Traffic overview with interactive charts
  - Error trends and top failing routes
  - Performance metrics (p50/p95/p99 latency)
  - Consumer segmentation analysis
  - Searchable request logs
  - Auto-refresh with configurable intervals

- **🔌 New Metrics APIs**
  - `GET /__devtrack__/metrics/traffic` - Traffic over time
  - `GET /__devtrack__/metrics/errors` - Error trends
  - `GET /__devtrack__/metrics/perf` - Performance metrics
  - `GET /__devtrack__/consumers` - Consumer segmentation

- **👥 Consumer Segmentation**
  - Automatically identify and analyze API consumers
  - Track patterns, errors, and latency per consumer
  - Privacy-friendly implementation

### 🎯 Quick Start

```bash
pip install devtrack-sdk==0.4.0
```

After integrating the middleware, visit:
```
http://localhost:8000/__devtrack__/dashboard
```

### 🔄 Migration

**No breaking changes!** Simply upgrade:
```bash
pip install --upgrade devtrack-sdk
```

### 📚 Documentation

- [Full Release Notes](docs/release/RELEASE_NOTES%20DevTrack%20SDK%20v0.4.0.md)
- [Integration Guide](docs/fastapi_integration.md)
- [Dashboard Features](docs/release/ROADMAP.md)

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.3.0...v0.4.0

