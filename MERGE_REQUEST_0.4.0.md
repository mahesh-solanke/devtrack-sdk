# 🚀 Release v0.4.0 - Pulse: Dashboard & Real-Time Metrics

## 📋 Overview

This MR introduces **DevTrack SDK v0.4.0 (Pulse)** - a major release that transforms DevTrack from a logging tool into a full observability platform with a built-in real-time dashboard and comprehensive metrics APIs.

## 🎯 Goal

> Provide a real-time, interactive analytics console running alongside your API.

## ✨ Major Features

### 📊 Built-in Real-Time Dashboard

- **Interactive Dashboard** at `/__devtrack__/dashboard`
  - **Traffic Overview** – requests over time with interactive charts
  - **Error Trends** – failure rates & top failing routes
  - **Performance Metrics** – p50/p95/p99 latency charts
  - **Request Logs** – searchable & filterable table
  - **Consumer Segmentation** – identify and analyze API consumers
  - **KPI Cards** – key metrics at a glance

- Auto-refresh (5–30 s) toggle
- Modern UI built with **React + Tailwind CSS**
- Zero configuration - works out of the box

### 🔌 New Metrics API Endpoints

**JSON APIs for Integration:**
- `GET /__devtrack__/metrics/traffic` - Traffic counts over time
- `GET /__devtrack__/metrics/errors` - Error trends and top failing routes
- `GET /__devtrack__/metrics/perf` - Performance metrics (p50/p95/p99)
- `GET /__devtrack__/consumers` - Consumer segmentation data

All endpoints support `hours` query parameter for time range filtering.

### 👥 Consumer Segmentation

- Automatically identify API consumers via headers, JWTs, IPs, or auth context
- Track request patterns per consumer
- Analyze error rates and latency by consumer
- Privacy-friendly hashed identifiers
- No API key required

### 🛠️ Technical Implementation

- Dashboard built with **React + Tailwind**, bundled with FastAPI static files
- Async batching writer for minimal overhead
- Enhanced database queries for metrics aggregation
- Optimized SQL queries for time-series data
- Efficient percentile calculations

## 📦 Changes

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
- Database connection handling in tests

## ✅ Testing

**Status**: ✅ **ALL TESTS PASSING**

- **Django Integration**: 10/10 tests passing
- **CLI Commands**: 13/13 tests passing
- **v0.4.0 Metrics Endpoints**: 9/9 tests passing
- **FastAPI Middleware**: 16/16 tests passing

**Total**: 48+ tests passing

For detailed test results, see: [Final Test Summary](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/FINAL_TEST_SUMMARY.md)

## 🔄 Migration

**No breaking changes!** This is a backward-compatible release.

Simply upgrade:
```bash
pip install --upgrade devtrack-sdk
```

The dashboard will be automatically available at `/__devtrack__/dashboard` after upgrade.

## 📚 Documentation

- [Release Notes](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/docs/release/RELEASE_NOTES%20DevTrack%20SDK%20v0.4.0.md)
- [Test Summary](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/FINAL_TEST_SUMMARY.md)
- [GitHub Release Notes](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/GITHUB_RELEASE_0.4.0.md)
- [Roadmap Update](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/docs/release/ROADMAP.md#-v04--dashboard--real-time-metrics)

## 🎯 Version Update

All version numbers updated from `0.3.0` to `0.4.0`:
- `devtrack_sdk/__version__.py`
- `setup.py`
- `pyproject.toml`
- `README.md`
- Documentation files
- Example files

## 📝 Checklist

- [x] All features implemented
- [x] All tests passing
- [x] Version numbers updated
- [x] Documentation updated
- [x] Release notes created
- [x] Examples updated
- [x] No breaking changes
- [x] Backward compatible
- [x] Database connection issues fixed

## 🔗 Related

- Related to: v0.4.0 Pulse Release
- Roadmap: [v0.4.0 Section](https://github.com/mahesh-solanke/devtrack-sdk/blob/devtrack/pulse-q4-dashboard/docs/release/ROADMAP.md#-v04--dashboard--real-time-metrics)
- [View All Changes](https://github.com/mahesh-solanke/devtrack-sdk/compare/main...devtrack/pulse-q4-dashboard)

---

**Ready for Review & Merge** ✅

