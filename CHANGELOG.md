# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-11-24
### Added
- Full Steam achievement tracking pipeline.
- Steam Web API integration for player summaries and achievements.
- Selenium-based HTML scraping fallback with cookie-based authentication.
- Auto-detection of expired cookies with HTML diagnostics saving.
- Rich colored logging (success, warnings, errors).
- `debug/` directory with automatic HTML dump for troubleshooting.
- `fetchers.py` API + HTML route handling.
- `main.py` high-level orchestrator logic.
- `config.json` loading and CLI overrides.
- Progress bars and timestamped logs.
- Complete type hints and docstrings across the project.
- Cookie setup and storage flow.
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
