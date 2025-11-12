"""
run_tracker.py
---------------
Main entry point for the Steam Achievement Tracker.

Steps:
1. Load configuration settings (from config.json + CLI overrides)
2. Ensure the user’s Steam cookies exist; if not, launch Chrome for login
3. Run the main tracker workflow to fetch and export achievements

Usage:
    python run_tracker.py --appid 3527290
    python run_tracker.py --game https://store.steampowered.com/app/3527290/PEAK/
"""

import sys
from tracker.config import load_config, COOKIE_FILE
from tracker.cookie_setup import generate_steam_cookies
from tracker.main import run_tracker


def main():
    """
    Run the Steam Achievement Tracker:
    - Loads configuration.
    - Ensures Steam cookies are present.
    - Executes the main tracking workflow.
    """
    # Load settings (from config.json + CLI overrides)
    config = load_config()

    # Ensure Steam cookies are available
    if not COOKIE_FILE.exists():
        print("[⚙️] No Steam cookies found — launching login window...")
        generate_steam_cookies(COOKIE_FILE)
        print("[✅] Cookies saved successfully!\n")

    # 3. Run the tracker
    try:
        run_tracker(config)
    except Exception as e:
        print(f"[❌] Tracker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
