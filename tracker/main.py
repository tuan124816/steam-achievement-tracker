import time
import pandas as pd
from .utils import log, progress_bar
from .fetchers import (
    fetch_schema, fetch_player_api,
    fetch_player_html_selenium, create_logged_in_driver
)
from .constants import API_SLEEP, HTML_SLEEP
from .cookie_setup import generate_steam_cookies
from .config import COOKIE_FILE

if not COOKIE_FILE.exists():
    generate_steam_cookies(COOKIE_FILE)

def build_tracker(api_key, app_id, friends, cookie_file):
    schema = fetch_schema(api_key, app_id)
    apiname_to_display = {a["apiname"]: a["displayName"] for a in schema}
    df = pd.DataFrame([{
        "Achievement name": a["displayName"],
        "Description": a["description"],
        **{f["name"]: False for f in friends}
    } for a in schema])

    driver = None
    for friend in progress_bar(friends, desc="Friends"):
        fname, fid = friend["name"], friend["steamid"]
        log(f"Processing {fname}...")
        unlocked_display = set()

        try:
            time.sleep(API_SLEEP)
            api_data = fetch_player_api(api_key, app_id, fid)
            if api_data:
                unlocked_display = {
                    apiname_to_display.get(k)
                    for k, v in api_data.items() if v and apiname_to_display.get(k)
                }
            else:
                raise ValueError("No API data, fallback to Selenium")
        except Exception:
            log(f"  ⚠️ API failed for {fname}, trying Selenium")
            if not driver:
                driver = create_logged_in_driver(cookie_file)
            time.sleep(HTML_SLEEP)
            unlocked_display = fetch_player_html_selenium(fid, app_id, driver)

        df[fname] = df["Achievement name"].apply(lambda s: s in unlocked_display)
        log(f"  → {len(unlocked_display)} unlocked")

    if driver:
        driver.quit()
    return df

def run_tracker(cfg):
    from .excel_utils import export_styled_excel
    df = build_tracker(cfg["api_key"], cfg["app_id"], cfg["friends"], cfg["cookie_file"])
    export_styled_excel(df, cfg["friends"], cfg["output_path"])
