# Release Notes - DevTrack SDK v0.4.3

## 🎉 Release Date
**Version**: 0.4.3 (Packaging & Compatibility Release)  
**Release Date**: 2026-06-18

---

## 📋 Overview

DevTrack SDK v0.4.3 improves how the package is installed, tested, and released. The main change is that FastAPI and Django are now optional integration dependencies instead of being installed for every user by default. This keeps the core SDK lighter while still making framework-specific installation straightforward.

This release also expands Django compatibility validation, adds packaging guardrails, and introduces one-command version bumping for future releases.

---

## ✨ What's New

### Optional Framework Dependencies

FastAPI and Django integrations are now installed through package extras:

```bash
# FastAPI integration
pip install "devtrack-sdk[fastapi]"

# Django integration
pip install "devtrack-sdk[django]"

# Both integrations
pip install "devtrack-sdk[all]"
```

Core installs remain available for CLI/database usage:

```bash
pip install devtrack-sdk
```

**Impact:**
- Users no longer install FastAPI or Django unless they need those integrations
- Core installs are smaller and less likely to affect existing application dependency trees
- Framework-specific setup is clearer in README and integration docs

### Lazy Framework Imports

Top-level imports now avoid importing optional frameworks immediately. DevTrack SDK lazily loads FastAPI and Django integration exports only when those attributes are accessed.

**Impact:**
- `import devtrack_sdk` works without FastAPI or Django installed
- Optional framework dependencies behave like true extras
- Applications can depend on the core SDK without pulling framework packages

---

## 🔄 Improvements

### Django Compatibility Coverage

GitHub Actions now tests against a Django matrix:

- Django `4.2`
- Django `5.2`

The runtime compatibility test now checks the supported Django range instead of hard-coding only exact CI versions, making local development less brittle while preserving CI coverage for declared support.

### Packaging Metadata

Package metadata now better reflects optional framework support:

- Core dependencies contain only runtime CLI/database requirements
- FastAPI and Django are declared under optional extras
- Django `4.2` and `5.2` classifiers were added
- Development dependencies include framework/test tooling separately

### Release Automation

DevTrack SDK now uses `bump-my-version` for coordinated version updates.

Maintainers can bump all tracked version references with:

```bash
bump-my-version bump patch
```

This updates:
- `pyproject.toml`
- `setup.py`
- `devtrack_sdk/__version__.py`
- README version badge

Commit and tag creation are disabled by default so maintainers stay in control of the release flow.

---

## 🔧 Technical Changes

### Added

- Optional dependency groups: `fastapi`, `django`, `all`, and `dev`
- Django compatibility tests for middleware, URL patterns, request extraction, and runtime support range
- Packaging tests to ensure frameworks remain optional
- Version synchronization test across package metadata and README badge
- `bump-my-version` configuration in `pyproject.toml`
- Release checklist instructions for automated version bumps

### Changed

- Moved FastAPI and Django from core dependencies into optional extras
- Updated README and framework docs to use extras-based installation commands
- Updated CI to install package in editable mode with dev extras
- Added CI matrix coverage for Django 4.2 and 5.2
- Updated package version from `0.4.2` to `0.4.3`

---

## 📦 Installation

Core install:

```bash
pip install devtrack-sdk==0.4.3
```

Framework integrations:

```bash
pip install "devtrack-sdk[fastapi]==0.4.3"
pip install "devtrack-sdk[django]==0.4.3"
pip install "devtrack-sdk[all]==0.4.3"
```

Or upgrade from a previous version:

```bash
pip install --upgrade devtrack-sdk
```

---

## 🔄 Migration from v0.4.2

This release is backward-compatible for users who already have their framework installed in their application environment.

### What Changed

FastAPI and Django are no longer installed by the core package. If your app relies on DevTrack to bring in the framework dependency, install the matching extra:

```bash
pip install "devtrack-sdk[fastapi]"
pip install "devtrack-sdk[django]"
```

### What Stays the Same

- Existing middleware APIs remain unchanged
- CLI behavior remains unchanged
- Database behavior remains unchanged
- Existing FastAPI and Django integrations continue to work when the relevant framework is installed

---

## 📝 Full Changelog

### Added
- Optional package extras for FastAPI and Django integrations
- Django 4.2 and 5.2 CI matrix coverage
- Django compatibility tests
- Packaging tests for optional dependency behavior
- Version consistency test for release metadata
- One-command release version bumping with `bump-my-version`

### Changed
- Core package dependencies are now limited to non-framework runtime requirements
- Top-level package exports now use lazy imports for framework integrations
- README and integration docs now recommend extras-based installation
- Release checklist now documents automated version bumping

### Technical
- Added `[project.optional-dependencies]` in `pyproject.toml`
- Added `extras_require` in `setup.py`
- Added `[tool.bumpversion]` configuration in `pyproject.toml`
- Updated GitHub Actions dependency installation flow

---

## 🧪 Testing

Validation added or updated for:

- ✅ Top-level `devtrack_sdk` import without framework packages
- ✅ Optional FastAPI and Django dependency metadata
- ✅ Django middleware and URL loading
- ✅ Django request metadata extraction
- ✅ Django runtime compatibility range
- ✅ Version references staying in sync across release files
- ✅ CI coverage for Django 4.2 and 5.2

---

## 🔗 Resources

- **Documentation**: [GitHub Docs](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahesh-solanke/devtrack-sdk/discussions)

---

## 📋 Known Issues

None at this time. If you encounter any issues, please report them on [GitHub Issues](https://github.com/mahesh-solanke/devtrack-sdk/issues).

---

**Full Changelog**: https://github.com/mahesh-solanke/devtrack-sdk/compare/v0.4.2...v0.4.3
