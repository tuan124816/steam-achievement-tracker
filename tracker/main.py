"""
main.py
--------
Core logic for building and running the Steam Achievement Tracker.

Handles:
- Retrieving game schema (achievement list)
- Fetching each friend’s unlocked achievements
- Automatic fallback from API → Selenium when private profiles are detected
- Combining data into a single Pandas DataFrame
- Exporting to formatted Excel report
"""

import time
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from .utils import log, warn, error, progress_bar
from .fetchers import (
    fetch_schema, fetch_player_api,
    fetch_player_html_selenium, create_logged_in_driver
)
from .constants import API_SLEEP, HTML_SLEEP
from .cookie_setup import generate_steam_cookies
from .config import COOKIE_FILE


# # Ensure cookies exist before starting
# def ensure_valid_cookies() -> None:
#     """Check whether cookies exist; if missing, generate them."""
#     if not COOKIE_FILE.exists():
#         log("⚠️  No steam_cookies.pkl found — generating new cookies.")
#         generate_steam_cookies(COOKIE_FILE)
#         log("✅ Cookie file created.\n")


def build_tracker(api_key: str, app_id: int, friends: List[Dict[str, Any]], cookie_file: Path, debug=False) -> pd.DataFrame:
    """
    Build the main achievement tracking DataFrame.

    Steps:
    1. Load the game schema (list of all achievements).
    2. For each friend:
        - Try Steam API first.
        - If API fails (private profile or missing data), use Selenium fallback.
    3. Populate the DataFrame with True/False for each user's unlocked achievements.

    Args:
        api_key (str): Steam Web API key.
        app_id (int): Steam game AppID.
        friends (list[dict]): List of friends ({"name": str, "steamid": str}).
        cookie_file (Path): Path to saved Steam cookies.
        debug (bool): If True, save raw HTML for debugging.

    Returns:
        pandas.DataFrame: Achievement tracker with friends' progress.
    """
    # Fetch schema and build DataFrame structure
    schema = fetch_schema(api_key, app_id)
    apiname_to_display = {a["apiname"]: a["displayName"] for a in schema}

    df = pd.DataFrame([{
        "Icon": a["icon"],      # NEW
        "Achievement name": a["displayName"],
        "Description": a["description"],
        **{f["name"]: False for f in friends}
    } for a in schema])

    driver = None   # Selenium driver (lazy-loaded only if needed)

    # Loop through friends with progress bar
    for friend in progress_bar(friends, desc="Friends"):
        fname, fid = friend["name"], friend["steamid"]
        log(f"Processing {fname}...")
        unlocked_display = set()

        try:
            # Try API first
            time.sleep(API_SLEEP)
            api_data = fetch_player_api(api_key, app_id, fid)
            if api_data:
                unlocked_display = {
                    apiname_to_display.get(k)
                    for k, v in api_data.items() if v and apiname_to_display.get(k)
                }
            else:
                # API returned no data, then likely private
                raise ValueError("No API data, fallback to Selenium")
            
        except Exception:
            # Selenium fallback (for private profiles)
            warn(f"  ⚠️ API failed for {fname}, trying Selenium") if debug else None
            if not driver:
                driver = create_logged_in_driver(cookie_file)
            time.sleep(HTML_SLEEP)
            try:
                unlocked_display = fetch_player_html_selenium(fid, app_id, driver, debug=debug)
            except ValueError as e:
                if "expired" not in str(e).lower():
                    raise

                error("⚠️  Selenium cookie error detected.")
                error("Cookie file exists but is expired or invalid.")
                log("🔄 Regenerating cookies…")

                generate_steam_cookies(COOKIE_FILE)

                driver = create_logged_in_driver(cookie_file)
                unlocked_display = fetch_player_html_selenium(fid, app_id, driver, debug=debug)


        # Mark unlocked achievements in DataFrame
        df[fname] = df["Achievement name"].apply(lambda s: s in unlocked_display)
        log(f"  → {len(unlocked_display)} unlocked")

    if driver:
        driver.quit()

    return df


def run_tracker(cfg: Dict[str, Any]) -> None:
    """
    Main entrypoint for running the full achievement tracker.

    Loads configuration, runs the tracker, and exports the final Excel file.

    Args:
        cfg (dict): Config dictionary containing:
            - api_key
            - app_id
            - friends
            - cookie_file
            - output_path
    """
    from .excel_utils import export_styled_excel
    from .steam_utils import resolve_vanity_url

    for friend in cfg["friends"]:
        raw = friend["steamid"]
        steamid = resolve_vanity_url(raw, api_key=cfg["api_key"])

        if steamid:
            friend["steamid"] = steamid
        else:
            warn(f"⚠️ Could not resolve vanity URL '{raw}'.  Skipping ...")

    df = build_tracker(cfg["api_key"], 
                       cfg["app_id"], 
                       cfg["friends"], 
                       cfg["cookie_file"],
                       cfg["debug"])
    export_styled_excel(df, cfg["friends"], cfg["output_path"], cfg["app_id"])
