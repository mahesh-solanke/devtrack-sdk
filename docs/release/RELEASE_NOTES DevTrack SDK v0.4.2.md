# Release Notes - DevTrack SDK v0.4.2

## 🎉 Release Date
**Version**: 0.4.2 (Stability - Bugfix Release)  
**Release Date**: 2026-01-11

---

## 📋 Overview

DevTrack SDK v0.4.2 is a **stability and bugfix release** that resolves critical database lock conflicts between CLI commands and running applications. This release significantly improves the developer experience by adding intelligent fallback mechanisms and better error handling when the database is locked by an active application instance.

---

## 🐛 Critical Bug Fixes

### Fixed DuckDB Lock Conflicts in CLI Commands

**Problem:** CLI commands (`stat`, `query`, `init`) would fail with lock errors when the database was already in use by a running application. DuckDB uses file-level locking, meaning a single write connection blocks all other connections (including read-only ones) from accessing the database file.

**Root Cause:** 
- DuckDB's file-level locking mechanism prevents concurrent access
- CLI commands attempted direct database access without checking if the application was running
- No fallback mechanism when database was locked
- Poor error messages that didn't guide users to solutions

**Solution:**
- **HTTP API Fallback**: Added intelligent fallback to HTTP API endpoints when database lock is detected
  - `stat` command now fetches stats from `/__devtrack__/stats` endpoint if database is locked
  - `query` command fetches logs from API when direct database access fails
  - `init` command checks database status via API before prompting for overwrite
- **Lock Detection**: Enhanced error parsing to detect lock conflicts and extract process information (PID)
- **Graceful Degradation**: Commands now provide clear guidance when database is locked
- **Improved User Experience**: Better error messages with actionable suggestions

**Impact:**
- CLI commands now work seamlessly even when application is running
- No more confusing lock errors - users get clear guidance
- Developers can use CLI tools without stopping their applications
- Better error messages help users understand and resolve issues quickly

### Fixed `init` Command Unnecessary Prompts

**Problem:** The `init` command would prompt users to overwrite an existing database even when the database was already initialized and accessible via the running application's API.

**Solution:**
- Added `check_db_initialized_via_api()` helper function
- `init` command now checks database status via HTTP API before prompting
- If database is initialized and accessible via API, shows information and exits gracefully
- Prevents unnecessary overwrite prompts when application is running

---

## 🔄 Improvements

### Enhanced Database Connection Management

- **Read/Write Mode Handling**: Improved `DevTrackDB` class to better handle read-only and write mode transitions
- **Connection Reuse**: Optimized connection reuse to minimize lock contention
- **Better Lock Handling**: Enhanced lock conflict detection and error reporting

### Improved Error Messages

- **Lock Information**: Error messages now include process PID when available
- **Actionable Guidance**: Clear suggestions on how to resolve lock conflicts
- **API Status**: Better feedback when API fallback is used

### Test Infrastructure

- **Network Request Mocking**: Added global pytest fixture to prevent hanging in CI
- **Comprehensive Test Coverage**: Added extensive tests for lock conflict scenarios
- **CI Stability**: Fixed GitHub Actions timeouts by mocking network requests

---

## 🔧 Technical Changes

### New Functions

- `parse_lock_error()`: Extracts PID and process info from DuckDB lock errors
- `check_db_initialized_via_api()`: Checks database initialization status via HTTP API
- Enhanced `detect_devtrack_endpoint()`: Better endpoint detection with improved error handling

### Modified Components

- **`cli.py`**: Major refactoring to add API fallback mechanisms
  - `stat` command: HTTP API fallback on lock
  - `query` command: HTTP API fallback on lock
  - `init` command: API check before overwrite prompt
- **`database.py`**: Improved connection handling for read/write mode transitions
- **`tests/conftest.py`**: Added global network request mocking fixture

### Test Coverage

- Added 46 comprehensive CLI tests
- Tests for lock conflict scenarios
- Tests for API fallback mechanisms
- Tests for error handling and user messaging

---

## 📦 Installation

```bash
pip install devtrack-sdk==0.4.2
```

Or upgrade from previous version:
```bash
pip install --upgrade devtrack-sdk
```

---

## 🔄 Migration from v0.4.1

**No breaking changes!** This is a backward-compatible bugfix release.

Simply upgrade:
```bash
pip install --upgrade devtrack-sdk
```

All existing functionality remains the same. The improvements are automatically applied.

### What to Expect

- **Better CLI Experience**: CLI commands now work even when your application is running
- **Clearer Error Messages**: More helpful error messages when issues occur
- **No Behavior Changes**: All existing functionality works exactly as before

---

## 📝 Full Changelog

### Fixed
- **Critical**: DuckDB lock conflicts causing CLI commands to fail when application is running
- **Critical**: `init` command prompting unnecessarily when database is already initialized
- Database connection handling for read/write mode transitions
- Error messages for locked databases now include process information

### Improved
- Added HTTP API fallback for `stat`, `query`, and `init` commands
- Enhanced error handling with lock detection and process information
- Better user guidance when database is locked
- Improved test infrastructure to prevent CI timeouts
- More robust database initialization checks

### Technical
- Added `parse_lock_error()` function for better error parsing
- Added `check_db_initialized_via_api()` helper function
- Enhanced `detect_devtrack_endpoint()` with better error handling
- Improved `DevTrackDB` connection management
- Added global pytest fixture for network request mocking

---

## 🧪 Testing

All fixes have been tested across:
- Different database lock scenarios
- Running application with CLI commands
- API fallback mechanisms
- Error handling and user messaging
- CI/CD pipeline (GitHub Actions)

**Test Results:**
- ✅ All 46 CLI tests passing
- ✅ All integration tests passing
- ✅ CI pipeline stable (no timeouts)

---

## 🙏 Thank You

Thank you to all users who reported database lock issues! Your feedback helped us create a much better developer experience.

---

## 🔗 Resources

- **Documentation**: [GitHub Docs](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)

---

## 📋 Known Issues

None at this time. If you encounter any issues, please report them on [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues).

---

## 🎯 What's Next

We're continuously improving DevTrack SDK based on user feedback. Upcoming releases will focus on:
- Performance optimizations
- Additional CLI features
- Enhanced dashboard capabilities
- Better documentation and examples

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.4.1...v0.4.2

