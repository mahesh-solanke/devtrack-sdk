# Release Notes - DevTrack SDK v0.3.0

## 🎉 Release Date
**Version**: 0.3.0  
**Release Date**: 2025-11-30

---

## 📋 Overview

DevTrack SDK v0.3.0 is a **major release** that introduces **DuckDB integration** as the primary database backend, replacing in-memory storage with persistent, high-performance database capabilities. This release significantly enhances the SDK's functionality, reliability, and scalability, making it production-ready for real-world deployments.

---

## 🚀 Major Features

### 🗄️ DuckDB Database Integration

**What's New:**
- **Persistent Storage**: Request logs now persist across application restarts
- **High Performance**: DuckDB's columnar storage optimized for analytics workloads
- **SQL Queries**: Full SQL support for complex filtering and aggregation
- **Automatic Schema Management**: Database tables created automatically on first use

**Benefits:**
- No data loss on application restarts
- Better performance for large datasets
- Production-ready storage solution
- Scalable to handle millions of requests

### 🛠️ Comprehensive CLI Toolkit

**New CLI Commands:**

1. **`devtrack init`** - Initialize DuckDB database
   ```bash
   devtrack init --db-path devtrack_logs.db
   ```

2. **`devtrack reset`** - Reset database (delete all logs)
   ```bash
   devtrack reset --db-path devtrack_logs.db --yes
   ```

3. **`devtrack stat`** - Enhanced statistics with DuckDB backend
   ```bash
   devtrack stat --top 10 --sort-by latency
   ```

4. **`devtrack export`** - Export logs to JSON/CSV
   ```bash
   devtrack export --format json --output logs.json
   ```

5. **`devtrack query`** - Advanced querying with filters
   ```bash
   devtrack query --status-code 404 --days 7 --verbose
   ```

6. **`devtrack monitor`** - Real-time monitoring dashboard
   ```bash
   devtrack monitor --interval 5 --top 15
   ```

7. **`devtrack health`** - System health checks
   ```bash
   devtrack health --endpoint
   ```

8. **`devtrack version`** - Version information
   ```bash
   devtrack version
   ```

### 📝 Django Management Commands

**New Django Commands:**

- `python manage.py devtrack_init` - Initialize database
- `python manage.py devtrack_reset` - Reset database
- `python manage.py devtrack_stats` - View statistics

**Usage:**
```bash
python manage.py devtrack_init
python manage.py devtrack_stats
```

### 🔄 Enhanced Middleware

**Django Middleware:**
- Migrated from in-memory stats to DuckDB storage
- Improved error handling and logging
- Database connection management

**FastAPI Routes:**
- DuckDB integration for statistics endpoints
- Enhanced filtering and querying capabilities
- Improved error responses

---

## 📚 Documentation Improvements

- **New comprehensive documentation** at `docs/index.md`
- **Enhanced integration guides** for Django and FastAPI
- **Updated examples** with DuckDB integration

---

## 🧪 Test Improvements

**Fixed Issues:**
- ✅ Fixed 5 CLI test failures (stat command tests)
- ✅ Fixed 3 Django integration test failures
- ✅ Updated middleware tests for DuckDB integration

**Test Results:**
- 38/39 tests passing
- All DuckDB-related tests verified

---

## ⚠️ Breaking Changes

### 1. Database Initialization Recommended

**Before (v0.2.x):**
- Middleware worked out of the box with in-memory storage
- No initialization needed

**After (v0.3.0):**
- **Database tables are auto-created** on first use (no manual initialization required)
- **Recommended**: Run `devtrack init` for explicit setup and verification
- Middleware uses DuckDB database instead of in-memory storage
- Database file and tables are automatically created when middleware first logs a request

**Why `devtrack init` is recommended:**
- Explicitly prepares the database before production use
- Verifies database connectivity and schema
- Provides initial database statistics
- Allows setting custom database path upfront

**Impact:** For existing deployments, the database will be auto-created on first request, but explicit initialization is recommended for production environments.

### 2. Persistent Storage

**Before (v0.2.x):**
- Data stored in memory (lost on restart)

**After (v0.3.0):**
- Data stored in DuckDB database file
- Persists across application restarts

**Impact:** Data structure and storage location changed.

### 3. Dependencies

**New Dependency:**
- `duckdb>=1.1.0` added to requirements

**Impact:** Additional package installation required.

---

## 🔄 Migration Guide

### For Existing Users (v0.2.x → v0.3.0)

#### Step 1: Upgrade Installation
```bash
pip install --upgrade devtrack-sdk
```

#### Step 2: Initialize Database
```bash
devtrack init --db-path devtrack_logs.db
```

Or for Django:
```bash
python manage.py devtrack_init
```

#### Step 3: Update Configuration (Optional)

**Django:**
```python
# settings.py
DEVTRACK_DB_PATH = "devtrack_logs.db"  # Custom path if needed
```

**FastAPI:**
```python
# Configure database path if different from default
DEVTRACK_DB_PATH = "devtrack_logs.db"
```

#### Step 4: Restart Application
Restart your FastAPI or Django application to use the new database backend.

### Data Migration

If you have existing in-memory data:
- Export existing data (if applicable)
- Initialize new database
- Data will start collecting from scratch in the new database

**Note:** In-memory data cannot be automatically migrated. If you have critical data, export it before upgrading.

---

## 📦 Installation

### Install from PyPI
```bash
pip install devtrack-sdk==0.3.0
```

### Install from Source
```bash
git clone https://github.com/mahesh-solanke/devtrack-sdk.git
cd devtrack-sdk
git checkout v0.3.0
pip install -e .
```

### Requirements
- Python >= 3.10
- duckdb >= 1.1.0 (new)
- fastapi >= 0.90
- django >= 4.0.0
- httpx >= 0.24
- starlette >= 0.22
- rich >= 13.3
- typer >= 0.9

---

## 🎯 What's Improved

1. **Reliability**: Persistent storage means no data loss
2. **Performance**: DuckDB's columnar storage optimized for analytics
3. **Scalability**: Handle larger volumes of request logs efficiently
4. **Developer Experience**: Rich CLI toolkit for managing logs
5. **Production Readiness**: Suitable for production deployments
6. **Query Flexibility**: SQL-based queries for advanced analytics

---

## 🐛 Bug Fixes

- Fixed CLI stat command endpoint detection
- Fixed Django views error handling
- Improved test suite stability
- Fixed database connection handling

---

## 📝 Changelog

### Added
- DuckDB database integration
- CLI toolkit (8 commands)
- Django management commands (3 commands)
- Comprehensive documentation
- Export functionality (JSON/CSV)
- Real-time monitoring dashboard
- Health check functionality
- Query functionality with filters

### Changed
- Middleware now uses DuckDB instead of in-memory storage
- CLI expanded significantly
- Documentation structure improved
- Test suite updated for DuckDB

### Fixed
- CLI test failures
- Django integration test failures
- Error handling in views

---

## 🔮 What's Next

Future releases may include:
- Real-time monitoring dashboard (web UI)
- Advanced analytics and reporting
- Integration with monitoring tools
- Custom metrics and alerting

---

## 🙏 Acknowledgments

Thank you to all contributors and users who provided feedback and helped shape this release!

**Special Thanks:**
- [@vivekkeshore](https://github.com/vivekkeshore/) - For valuable feedback and suggestions



---

## 📞 Support

- **Documentation**: https://github.com/mahesh-solanke/devtrack-sdk/blob/main/docs/index.md
- **GitHub Issues**: https://github.com/mahesh-solanke/devtrack-sdk/issues
- **GitHub Discussions**: https://github.com/mahesh-solanke/devtrack-sdk/discussions

---

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/devtrack-sdk/
- **GitHub Repository**: https://github.com/mahesh-solanke/devtrack-sdk
- **Documentation**: https://github.com/mahesh-solanke/devtrack-sdk/blob/main/docs/index.md

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.2.0...v0.3.0

