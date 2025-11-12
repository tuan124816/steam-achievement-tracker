"""
constants.py
-------------
Global constants for the Steam Achievement Tracker.

Contains HTTP headers and polite delays used across the project.
Keep values here for easy tuning without touching business logic.
"""

# ========== Request timing (seconds) ==========
# Short pauses to avoid hammering Steam's API or pages.

API_SLEEP = 1.0       # Delay between API requests
HTML_SLEEP = 1.2      # Delay between HTML/Selenium requests

# ========== HTTP headers ==========
# Use a realistic User-Agent to reduce the chance of being blocked.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )
}