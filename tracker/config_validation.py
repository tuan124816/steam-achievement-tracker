from .utils import error, log
from .fetchers import fetch_schema
from .cookie_setup import generate_steam_cookies
from pathlib import Path

def validate_config(cfg):
    if not cfg.get("api_key"):
        error("Missing API key in config.json")
        raise SystemExit

    if not isinstance(cfg.get("friends"), list):
        error("Friends must be a list in config.json")
        raise SystemExit

    cookie = Path(cfg.get("cookie_file", "steam_cookies.pkl"))
    # print('hehehe: ', Path(cfg.get("cookie_file", "steam_cookies.pkl")))
    if not cookie.exists():
        print('helelee 222: ')
        error(f"Cookie file missing: {cookie}")
        generate_steam_cookies(cookie)
        log("✅ Cookie file created.\n")
        # raise SystemExit

    # AppID test
    try:
        schema = fetch_schema(cfg["api_key"], cfg["app_id"])
        if not schema:
            raise RuntimeError
    except Exception:
        error("Invalid AppID or API key — Schema fetch failed.")
        raise SystemExit

    return True
