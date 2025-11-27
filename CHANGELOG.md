# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [1.1.0] – 2025-11-27
### Added
- **Icon support to Excel** (#3)
- **Private profile detection** (#4)
  - Detect API-private, Selenium-private, and fully-inaccessible profiles.
  - Avoid infinite loops when cookies are valid but user is private.
  - Clean classification of Type A, B, C, and D users.
- **Improved Selenium error handling**
  - Properly identifies expired cookies.
  - Prevents false positives due to identical HTML structures.
- **Icon support in Excel exports**
  - Adds `icon` and `icongray` URL fields.
  - Schema now contains full image metadata for achievements.
- **Stronger logging system**
  - Colored terminal logs (green/yellow/red).
  - Colorless logs in `logs/tracker.log` for debugging.
- **Config validation**
  - Verifies API key
  - Verifies AppID (schema fetch test)
  - Verifies cookie file existence
  - Verifies friends list format

### Changed
- Updated Selenium HTML parsing with a more robust classifier.
- Cleaned and reorganized `fetchers.py`.

### Fixed
- Prevented incorrect detection of cookie expiration when the profile is truly private.
- Fixed rare case where Selenium HTML failed to detect unlocked achievements.

---


## [1.0.0] - 2025-11-24
### Added
- Full Steam API + Selenium achievement parser
- Robust cookie management & expired-cookie detection
- Colored logging (success/warn/error)
- Auto HTML snapshot saving (`/debug/html_*.html`)
- Excel export with styling
- Configurable via JSON or CLI flags
- Cross-platform executable support (Win/Linux/Mac)
- Initial packaging support (`pyproject.toml`).

### Changed
- Improved resilience against rate limits and failed HTML loads.
- Cleaner error messages and structured logging.

### Fixed
- Infinite cookie regeneration loop.
- Silent Selenium failures not detected before.

## [Unreleased]
- Further UI improvements.
- Possible SQLite achievement history database.
