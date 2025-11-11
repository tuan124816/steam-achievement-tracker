import time
import pickle
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .constants import HEADERS, API_SLEEP, HTML_SLEEP

def fetch_schema(api_key, app_id):
    url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={app_id}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    ach_list = data.get("game", {}).get("availableGameStats", {}).get("achievements", [])
    return [
        {"apiname": a.get("name", "").strip(),
         "displayName": a.get("displayName", a.get("name", "")).strip(),
         "description": a.get("description", "").strip()}   # NOTE: couldn't added Icon column yet
        for a in ach_list
    ]

def fetch_player_api(api_key, app_id, steamid):
    url = (f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
           f"?appid={app_id}&key={api_key}&steamid={steamid}")
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return {}
    data = r.json()
    achs = data.get("playerstats", {}).get("achievements", [])
    return {a.get("apiname"): int(a.get("achieved", 0)) for a in achs}

def create_logged_in_driver(cookie_file):
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    driver.get("https://steamcommunity.com")
    time.sleep(2)
    cookies = pickle.load(open(cookie_file, "rb"))
    for c in cookies:
        if "steamcommunity" in c.get("domain", ""):
            try:
                driver.add_cookie(c)
            except Exception:
                continue
    return driver

def fetch_player_html_selenium(steamid, app_id, driver):
    url = f"https://steamcommunity.com/profiles/{steamid}/stats/{app_id}/achievements/"
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    unlocked = set()
    for row in soup.select(".achieveRow"):
        title = row.select_one("h3.ellipsis")
        unlock = row.select_one(".achieveUnlockTime")
        if title and unlock and "Unlocked" in unlock.get_text():
            unlocked.add(title.get_text(strip=True))
    return unlocked

if __name__ == "__main__":
    from tracker.config import load_config
    from tracker.cookie_setup import generate_steam_cookies
    from pathlib import Path

    cfg = load_config()
    schema = fetch_schema(cfg["api_key"], cfg["app_id"])
    print(f"✅ Schema loaded: {len(schema)} achievements")

    steamid = input("Enter a SteamID to test: ")
    print("Fetching public API achievements...")
    data = fetch_player_api(cfg["api_key"], cfg["app_id"], steamid)
    print(f"→ Got {len(data)} entries")

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

