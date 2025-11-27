"""
fetchers.py
------------
Handles all data-fetching operations for the Steam Achievement Tracker project.

Includes:
- Steam Web API calls for game schemas and player achievement data.
- Selenium + BeautifulSoup scraping for locked/private profiles.
- Automatic cookie-based login for Selenium sessions.
- Privacy detection (API-private vs Steam-private vs cookie-expired).
"""

import time
import pickle
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from typing import Dict, Any, List, Set

from .constants import HEADERS, API_SLEEP, HTML_SLEEP
from .utils import log, warn, error, debug_save_html


def fetch_schema(api_key: str, app_id: int) -> List[Dict[str, str]]:
    """
    Fetch the achievement schema for a game from Steam Web API.

    Args:
        api_key (str): Steam Web API key.
        app_id (int): Steam App ID.

    Returns:
        list[dict]: Each dict contains:
            {
                "apiname": internal API name,
                "displayName": player-visible name,
                "description": achievement description,
                "icon": str | None,
                "icongray": str | None
            }
    """
    url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={app_id}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Extract the list of achievements from the schema
    ach_list = data.get("game", {}).get("availableGameStats", {}).get("achievements", [])

    return [
        {"apiname": a.get("name", "").strip(),
         "displayName": a.get("displayName", a.get("name", "")).strip(),
         "description": a.get("description", "").strip(),
         "icon": a.get("icon", None),
         "icongray": a.get("icongray", None),
         }  
        for a in ach_list
    ]


def fetch_player_api(api_key: str, app_id: int, steamid: str) -> Dict[str, int]:
    """
    Fetch a user's achievement data for a given game using the Steam API.

    Args:
        api_key (str): Steam Web API key.
        app_id (int): Steam App ID.
        steamid (str): Steam user ID (64-bit numeric).

    Returns:
        dict: {apiname: achieved_flag}, where achieved_flag ∈ {0, 1}.
    """
    url = (f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
           f"?appid={app_id}&key={api_key}&steamid={steamid}"
           )
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return {}
    data = r.json()
    achs = data.get("playerstats", {}).get("achievements", [])
    return {a.get("apiname"): int(a.get("achieved", 0)) for a in achs}


def create_logged_in_driver(cookie_file: str | Path) -> webdriver.Chrome:
    """
    Create a headless Selenium Chrome driver and load stored Steam cookies.

    Args:
        cookie_file (str | Path): Path to a .pkl file containing saved cookies.

    Returns:
        selenium.webdriver.Chrome: A Chrome driver logged into Steam.
    """
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    driver.get("https://steamcommunity.com")

    time.sleep(2)
    cookies = pickle.load(open(cookie_file, "rb"))
    # Inject cookies into session
    for c in cookies:
        if "steamcommunity" in c.get("domain", ""):
            try:
                driver.add_cookie(c)
            except Exception:
                continue
    return driver


def fetch_player_html_selenium(steamid: str, app_id: int, driver: webdriver.Chrome, debug: bool = False) -> Set[str]:
    """
    Fetch achievement unlocks from a user's Steam profile using Selenium.

    Used when the Steam Web API fails (e.g., profile privacy issues).

    Args:
        steamid (str): Steam user ID.
        app_id (int): Steam App ID.
        driver (webdriver.Chrome): Logged-in Selenium driver.
        debug (bool): If True, save raw HTML for debugging.

    Returns:
        set[str]: Names of unlocked achievements (as displayed on page).
        empty set: fully private (LEGIT).

    Raises:
        ValueError: If cookies are expired or invalid (LOGIN NEEDED).
    """
    url = f"https://steamcommunity.com/profiles/{steamid}/stats/{app_id}/achievements/"
    driver.get(url)
    time.sleep(3)

    html = driver.page_source

    # Debug mode: save HTML for inspection
    if debug:
        debug_save_html(f"{steamid}.html", html)

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ").lower()

    # if "you do not have permission to view these game stats" in text:
    #     raise ValueError("Expired Steam cookies detected")

    # if "this profile is private" in text or "private profile" in text:
    #     return set()
    
    # unlocked = set()

    # for row in soup.select(".achieveRow"):
    #     title = row.select_one("h3.ellipsis")
    #     unlock = row.select_one(".achieveUnlockTime")

    #     # If the element contains an unlock time, then achievement is earned
    #     if title and unlock and "Unlocked" in unlock.get_text():
    #         unlocked.add(title.get_text(strip=True))
    # return unlocked


    # # Case 1 — Fully private profile = LEGIT private
    # if "this profile is private" in text:
    #     return set()

    # # Case 2 — Cookie expired OR fully-private returns denial
    # if "you do not have permission to view these game stats" in text:
    #     # Check if we *can* view the profile itself
    #     profile_private = (
    #         soup.select_one(".profile_private_info") or
    #         "this profile is private" in text
    #     )

    #     if profile_private:
    #         # Fully private → LEGIT privacy
    #         return set()

    #     # Otherwise: expired cookie → REQUIRES RELOGIN
    #     raise ValueError("Expired Steam cookies detected")

    logged = {c["name"]: c["value"] for c in driver.get_cookies()}

    if "you do not have permission to view these game stats" in text:
        if not logged:
            ValueError("Expired Steam cookies detected")
        else:
            warn("This profile is private. Skipping ...")
            return set()

    if "this profile is private" in text:
        warn("This profile is private. Skipping ...")
        return set()

    # Case 3 — Normal achievement parsing
    unlocked = set()
    for row in soup.select(".achieveRow"):
        title = row.select_one("h3.ellipsis")
        unlock = row.select_one(".achieveUnlockTime")
        if title and unlock and "unlocked" in unlock.get_text().lower():
            unlocked.add(title.get_text(strip=True))

    return unlocked


if __name__ == "__main__":
    """
    Test mode: Run standalone from terminal to verify functionality.

    Usage:
        python -m tracker.fetchers

    Behavior:
        - Loads config (API key, AppID).
        - Fetches schema & player data from API.
        - Optionally tests Selenium with cookie-based login.
    """
    from tracker.config import load_config
    from tracker.cookie_setup import generate_steam_cookies
    from pathlib import Path

    cfg = load_config()
    schema = fetch_schema(cfg["api_key"], cfg["app_id"])
    print(f"✅ Schema loaded: {len(schema)} achievements")

    steamid = input("Enter a SteamID to test: ")
    
    print("\nFetching API data...")
    data = fetch_player_api(cfg["api_key"], cfg["app_id"], steamid)
    print(f"→ API returned: {len(data)} entries")

    # --- Optional Selenium test with interactive cookie setup ---
    cookie_path = Path("steam_cookies.pkl")

    try:
        if not cookie_path.exists():
            print(f"\n⚠️  No cookie file found at {cookie_path}")
            choice = input("Would you like to create it now? [y/N]: ").strip().lower()
            if choice == "y":
                generate_steam_cookies(cookie_file=str(cookie_path))
                print("✅ Cookie file created successfully!\n")
            else:
                print("❌ Skipping Selenium test (no cookie file).")
                raise SystemExit(0)

        print("Launching Selenium driver...")
        driver = create_logged_in_driver(cookie_path)
        print("Fetching HTML via Selenium...")
        unlocked = fetch_player_html_selenium(steamid, cfg["app_id"], driver)
        print(f"→ {len(unlocked)} unlocked achievements")
        driver.quit()

    except FileNotFoundError:
        print(f"\n❌ Cookie file not found: {cookie_path}")
        print("Please run: python -m tracker.cookie_setup\n")
    except Exception as e:
        print(f"\n⚠️ Selenium test failed: {e}")

