# Release Notes - DevTrack SDK v0.4.1

## 🎉 Release Date
**Version**: 0.4.1 (Pulse - Bugfix Release)  
**Release Date**: 2025-12-23

---

## 📋 Overview

DevTrack SDK v0.4.1 is a **bugfix release** that addresses critical issues discovered in v0.4.0, particularly around DuckDB compatibility and dashboard functionality. This release ensures the dashboard displays correct statistics and improves the reliability of request detail views across different browser environments.

---

## 🐛 Critical Bug Fixes

### Fixed DuckDB Column Description Issue

**Problem:** The dashboard was displaying incorrect summary statistics (e.g., `{"1": 10}` instead of proper fields like `total_requests`, `unique_endpoints`, etc.).

**Root Cause:** DuckDB's `conn.description` sometimes returns generic column names like `["1"]` or `["NUMBER"]` instead of actual column names from SQL queries.

**Solution:** 
- Added robust fallback mechanism in `get_stats_summary()` to use known column names when DuckDB returns invalid descriptions
- Applied the same fix to `get_logs_by_path()` and `get_logs_by_status_code()` methods
- Ensures consistent behavior across all database query methods

**Impact:** Dashboard KPI cards now display correct metrics including:
- Total requests count
- Unique endpoints
- Average/min/max duration
- Success and error counts

### Fixed Request Detail View in New Window

**Problem:** When clicking on request IDs to view details in a new window, some users saw a plain screen without styling.

**Root Cause:** 
- `document.write()` method can fail in certain browser environments or with Content Security Policies
- HTML escaping issues could break the document structure
- No fallback mechanisms if primary method failed

**Solution:**
- Implemented multiple fallback methods for maximum compatibility:
  1. **Blob URL** (primary) - Works with CSP, no size limits
  2. **Data URL** (fallback) - For older browsers
  3. **document.write()** (final fallback) - Universal support
- Improved HTML escaping with manual escaping function
- Enhanced HTML structure with proper meta tags and viewport settings
- Better error handling with automatic fallback to modal view

**Impact:** Request detail views now display correctly with full styling across all browsers and environments.

---

## 🔄 Improvements

### Enhanced API Logging
- Improved logging in `fetchStats()` function for better debugging
- More concise and informative log messages
- Better error tracking for API requests

### Database Query Robustness
- All database query methods now handle DuckDB column description quirks
- Consistent fallback behavior across all query operations
- Better error handling and recovery

---

## 📦 Installation

```bash
pip install devtrack-sdk==0.4.1
```

---

## 🔄 Migration from v0.4.0

**No breaking changes!** This is a backward-compatible bugfix release.

Simply upgrade:
```bash
pip install --upgrade devtrack-sdk
```

All existing functionality remains the same. The fixes are automatically applied.

---

## 📝 Full Changelog

### Fixed
- **Critical**: DuckDB column description issue causing incorrect summary statistics in dashboard
- **Critical**: Request detail view not displaying styles in new window for some users
- Database query methods now handle DuckDB column name quirks consistently
- HTML escaping in request detail views for better security and compatibility

### Improved
- Enhanced API logging for better debugging
- Multiple fallback methods for opening request details in new window
- Better error handling in database query operations
- Improved HTML structure and escaping in detail views

---

## 🧪 Testing

All fixes have been tested across:
- Different DuckDB versions and configurations
- Multiple browser environments (Chrome, Firefox, Safari, Edge)
- Various Content Security Policy settings
- Different deployment scenarios

---

## 🙏 Thank You

Thank you to all users who reported these issues! Your feedback helps make DevTrack more reliable and robust.

---

## 🔗 Resources

- **Documentation**: [GitHub Docs](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)

---

## 📋 Known Issues

None at this time. If you encounter any issues, please report them on [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues).

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.4.0...v0.4.1

