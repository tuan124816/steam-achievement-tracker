# run_tracker.py
import sys
from tracker.config import load_config, COOKIE_FILE
from tracker.cookie_setup import generate_steam_cookies
from tracker.main import run_tracker

def main():
    # ✅ 1. Load settings (from config.json + CLI overrides)
    config = load_config()

    # ✅ 2. Ensure Steam cookies are available
    if not COOKIE_FILE.exists():
        print("[⚙️] No Steam cookies found — launching login window...")
        generate_steam_cookies(COOKIE_FILE)
        print("[✅] Cookies saved successfully!\n")

    # ✅ 3. Run the tracker
    try:
        run_tracker(config)
    except Exception as e:
        print(f"[❌] Tracker failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
