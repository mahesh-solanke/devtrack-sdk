# Release Notes - DevTrack SDK v0.4.0

## 🎉 Release Date
**Version**: 0.4.0 (Pulse)  
**Release Date**: 2025-11-30

---

## 📋 Overview

DevTrack SDK v0.4.0 **Pulse** introduces a **built-in real-time dashboard** and comprehensive metrics APIs, transforming DevTrack from a logging tool into a full observability platform. This release brings you a beautiful, interactive dashboard with zero external dependencies - everything runs locally with your API.

---

## 🚀 Major Features

### 📊 Built-in Real-Time Dashboard

**What's New:**
- **Interactive Dashboard** at `/__devtrack__/dashboard`
- **Auto-refresh** with configurable intervals (5-30 seconds)
- **Modern UI** built with React + Tailwind CSS
- **Zero Configuration** - works out of the box

**Dashboard Components:**
- 📈 **Traffic Overview** - Request volume over time with interactive charts
- ⚠️ **Error Trends** - Failure rates and top failing routes
- ⚡ **Performance Metrics** - p50, p95, p99 latency visualizations
- 👥 **Consumer Segmentation** - Identify and analyze API consumers
- 📋 **Request Logs** - Searchable, filterable request log table
- 📊 **KPI Cards** - Key metrics at a glance

### 🔌 New Metrics API Endpoints

**JSON APIs for Integration:**
- `GET /__devtrack__/metrics/traffic` - Traffic counts over time
- `GET /__devtrack__/metrics/errors` - Error trends and top failing routes
- `GET /__devtrack__/metrics/perf` - Performance metrics (p50/p95/p99)
- `GET /__devtrack__/consumers` - Consumer segmentation data

All endpoints support `hours` query parameter for time range filtering.

### 👥 Consumer Segmentation

**New Capability:**
- Automatically identify API consumers via headers, JWTs, IPs, or auth context
- Track request patterns per consumer
- Analyze error rates and latency by consumer
- Privacy-friendly hashed identifiers

---

## 📦 Installation

```bash
pip install devtrack-sdk==0.4.0
```

---

## 🚀 Quick Start

### FastAPI
```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.controller import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware)
```

### Django
```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'devtrack_sdk.django_middleware.DevTrackDjangoMiddleware',
]

# urls.py
from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    # ... your URLs
    *devtrack_urlpatterns,
]
```

### Access Dashboard
Once your app is running, visit:
```
http://localhost:8000/__devtrack__/dashboard
```

---

## 🎯 What's Changed

### ✨ New Features
- Built-in React dashboard with real-time updates
- Traffic, error, and performance metrics APIs
- Consumer segmentation and analysis
- Auto-refresh dashboard with configurable intervals
- Interactive charts and visualizations

### 🔄 Improvements
- Enhanced database queries for metrics aggregation
- Better error handling in dashboard routes
- Improved dashboard UI/UX
- Optimized performance metric calculations

### 📚 Documentation
- Updated integration guides
- Dashboard usage documentation
- API endpoint documentation

---

## 🔄 Migration from v0.3.0

**No breaking changes!** This is a backward-compatible release.

Simply upgrade:
```bash
pip install --upgrade devtrack-sdk
```

The dashboard will be automatically available at `/__devtrack__/dashboard` after upgrade.

---

## 📊 Example Dashboard Features

### Traffic Overview
- Real-time request volume charts
- Time-based filtering (last 1h, 6h, 24h)
- Interactive hover details

### Error Trends
- Error rate over time
- Top 10 failing routes
- Error count breakdowns

### Performance Metrics
- p50, p95, p99 latency percentiles
- Average latency tracking
- Performance trends over time

### Consumer Segmentation
- Top 50 consumers by request volume
- Average latency per consumer
- Error rates per consumer
- Unique endpoints accessed

---

## 🛠️ Technical Details

### Dashboard Technology
- **Frontend**: React 18 + Tailwind CSS
- **Charts**: Chart.js with react-chartjs-2
- **Build**: Vite
- **Bundling**: Included in Python package

### API Enhancements
- New metrics aggregation methods in database layer
- Optimized SQL queries for time-series data
- Efficient percentile calculations

---

## 📝 Full Changelog

### Added
- Built-in dashboard at `/__devtrack__/dashboard`
- Traffic metrics API endpoint
- Error trends API endpoint
- Performance metrics API endpoint
- Consumer segmentation API endpoint
- Auto-refresh functionality in dashboard
- KPI cards component
- Interactive charts for all metrics

### Improved
- Database query performance for metrics
- Error handling in API routes
- Dashboard asset serving
- Consumer identification logic

### Fixed
- Dashboard API URL injection
- Asset path resolution
- Time bucket calculations

---

## ✅ Testing & Quality Assurance

For detailed test results and verification, see: [Final Test Summary](../../FINAL_TEST_SUMMARY.md)

---

## 🙏 Thank You

Thank you to all contributors and users who provided feedback! This release represents a significant step forward in making DevTrack a complete observability solution.

---

## 🔗 Resources

- **Documentation**: [GitHub Docs](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.3.0...v0.4.0

