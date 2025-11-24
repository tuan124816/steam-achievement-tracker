# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
