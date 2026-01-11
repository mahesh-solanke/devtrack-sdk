# DevTrack SDK Release Checklist

Use this checklist for every release to ensure consistency and completeness.

## 📋 Pre-Release Preparation

### Code Quality & Testing
- [ ] **All tests pass locally**
  ```bash
   pytest tests/ -v
   ```
- [ ] **CI/CD pipeline passes** (GitHub Actions)
- [ ] **No linting errors**
  ```bash
   flake8 devtrack_sdk/ tests/
   ```
- [ ] **Code review completed** (if applicable)
- [ ] **All merge conflicts resolved**
- [ ] **Branch is up-to-date with main**

### Version Management
- [ ] **Determine version number** (following [SemVer](https://semver.org/))
  - `MAJOR.MINOR.PATCH` (e.g., 0.4.1 → 0.4.2)
  - Breaking changes → MAJOR
  - New features → MINOR
  - Bug fixes → PATCH
- [ ] **Update version in `devtrack_sdk/__version__.py`**
- [ ] **Update version in `pyproject.toml`**
- [ ] **Update version badge in `README.md`** (if applicable)

### Documentation
- [ ] **Create/update CHANGELOG.md** (or release notes)
  - List all changes (features, fixes, improvements)
  - Group by type: Added, Changed, Fixed, Deprecated, Removed
  - Include migration notes if breaking changes
- [ ] **Update `docs/release/RELEASE_NOTES DevTrack SDK vX.Y.Z.md`**
- [ ] **Review and update README.md** if needed
- [ ] **Update API documentation** (if applicable)
- [ ] **Check example code** in `examples/` directory

### Git Operations
- [ ] **Commit all changes** with clear commit message
  ```bash
   git add .
   git commit -m "chore: prepare release v0.4.2"
   ```
- [ ] **Push branch to remote**
  ```bash
   git push origin fix/db-lock-issue-conflicting-api-call-and-cli-command
   ```
- [ ] **Create Pull Request** (if not merging directly)
- [ ] **Merge to main branch**
  ```bash
   git checkout main
   git pull origin main
   git merge fix/db-lock-issue-conflicting-api-call-and-cli-command
   git push origin main
   ```

## 🏷️ Release Tagging

- [ ] **Create annotated git tag**
  ```bash
   git tag -a v0.4.2 -m "Release v0.4.2: Fix database lock conflicts"
   git push origin v0.4.2
   ```
- [ ] **Verify tag was created**
  ```bash
   git tag -l
   git show v0.4.2
   ```

## 📦 Package Building

- [ ] **Clean previous builds**
  ```bash
   rm -rf dist/ build/ *.egg-info/
   ```
- [ ] **Install/upgrade build tools**
  ```bash
   pip install --upgrade build twine
   ```
- [ ] **Build source distribution and wheel**
  ```bash
   python -m build
   ```
- [ ] **Verify build artifacts**
  ```bash
   ls -lh dist/
   # Should see: devtrack-sdk-0.4.2-py3-none-any.whl
   #            devtrack-sdk-0.4.2.tar.gz
   ```
- [ ] **Test installation from wheel** (optional but recommended)
  ```bash
   pip install dist/devtrack_sdk-0.4.2-py3-none-any.whl --force-reinstall
   devtrack version  # Verify it works
   ```

## 🚀 Publishing to PyPI

### Test PyPI (Recommended First)
- [ ] **Upload to Test PyPI**
  ```bash
   python -m twine upload --repository testpypi dist/*
   ```
- [ ] **Test installation from Test PyPI**
  ```bash
   pip install --index-url https://test.pypi.org/simple/ devtrack-sdk==0.4.2
   devtrack version  # Verify
   ```

### Production PyPI
- [ ] **Upload to Production PyPI**
  ```bash
   python -m twine upload dist/*
   ```
- [ ] **Verify package on PyPI**
  - Visit: https://pypi.org/project/devtrack-sdk/
  - Check version, description, files
- [ ] **Test installation from PyPI**
  ```bash
   pip install --upgrade devtrack-sdk
   devtrack version  # Verify version matches
   ```

## 📢 Post-Release Tasks

### GitHub
- [ ] **Create GitHub Release**
  - Go to: https://github.com/mahesh-solanke/devtrack-sdk/releases/new
  - Tag: `v0.4.2`
  - Title: `DevTrack SDK v0.4.2`
  - Description: Copy from release notes
  - Attach release notes file
- [ ] **Update release notes** on GitHub with changelog
- [ ] **Close related issues/PRs** (if applicable)
- [ ] **Update project milestones** (if using)

### Documentation
- [ ] **Update main documentation** (if hosted separately)
- [ ] **Update any external references** to version number
- [ ] **Announce release** (if applicable)
  - Blog post
  - Social media
  - Community forums

### Verification
- [ ] **Verify installation works** on clean environment
  ```bash
   python -m venv test_env
   source test_env/bin/activate  # or `test_env\Scripts\activate` on Windows
   pip install devtrack-sdk
   devtrack version
   ```
- [ ] **Test key functionality** after installation
  ```bash
   devtrack init
   devtrack stat
   devtrack help
   ```
- [ ] **Check PyPI download stats** (after 24 hours)

## 🔄 Post-Release Cleanup

- [ ] **Delete release branch** (if applicable)
  ```bash
   git branch -d fix/db-lock-issue-conflicting-api-call-and-cli-command
   git push origin --delete fix/db-lock-issue-conflicting-api-call-and-cli-command
   ```
- [ ] **Update local main branch**
  ```bash
   git checkout main
   git pull origin main
   ```
- [ ] **Clean up local tags** (optional)
- [ ] **Archive release notes** in `docs/release/`

## 📝 Release Notes Template

When creating release notes, use this structure:

```markdown
# DevTrack SDK v0.4.2 Release Notes

**Release Date:** YYYY-MM-DD

## 🎉 What's New

### Features
- Feature 1 description
- Feature 2 description

### Improvements
- Improvement 1
- Improvement 2

### Bug Fixes
- Fixed database lock conflicts in CLI commands
- Fixed issue with `devtrack init` prompting unnecessarily

### Technical Changes
- Added HTTP API fallback for CLI commands
- Enhanced error handling for locked databases
- Improved test coverage

## 🔧 Migration Guide

(If breaking changes exist)

## 📚 Documentation

- Updated CLI documentation
- Added examples for new features

## 🙏 Contributors

- @username1
- @username2

## 📦 Installation

```bash
pip install --upgrade devtrack-sdk
```

## 🔗 Links

- [GitHub Release](https://github.com/mahesh-solanke/devtrack-sdk/releases/tag/v0.4.2)
- [PyPI Package](https://pypi.org/project/devtrack-sdk/0.4.2/)
- [Documentation](https://github.com/mahesh-solanke/devtrack-sdk/tree/main/docs)
```

## ⚠️ Emergency Rollback (If Needed)

If critical issues are found after release:

- [ ] **Create hotfix branch** from main
- [ ] **Fix critical issue**
- [ ] **Bump patch version** (e.g., 0.4.2 → 0.4.3)
- [ ] **Follow release checklist** for hotfix
- [ ] **Document issue and fix** in release notes
- [ ] **Consider yanking problematic version** on PyPI if severe
  ```bash
   twine yank --version 0.4.2 devtrack-sdk
   ```

## 📊 Release Metrics (Optional)

Track these for future reference:
- Time to complete release: _____
- Number of commits in release: _____
- Number of files changed: _____
- Test coverage: _____
- PyPI downloads (first week): _____

---

**Last Updated:** 2024-12-19
**Maintainer:** DevTrack SDK Team

