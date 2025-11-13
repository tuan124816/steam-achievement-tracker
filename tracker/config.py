"""
config.py
----------
Handles configuration loading, command-line argument parsing,
and Steam game auto-detection (via store URLs).

Responsibilities:
- Load settings from config.json or CLI.
- Extract AppID from a provided Steam store URL.
- Fetch game name from Steam API for clearer logging.
- Define key file paths like steam_cookies.pkl and config.json.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any
import requests

# ========== Default Paths ==========
ROOT_DIR: Path = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG: Path = ROOT_DIR / "config.json"
COOKIE_FILE: Path = ROOT_DIR / "steam_cookies.pkl"


# ========== Helper Functions ==========
def extract_appid_from_url(url: str) -> int:
    """Extract numeric AppID from a Steam store/game URL."""
    match = re.search(r"/app/(\d+)", url)
    if not match:
        raise ValueError(f"Could not extract AppID from URL: {url}")
    return int(match.group(1))


def fetch_game_name(appid: int) -> str:
    """Fetch game name from Steam store API for validation/logging."""
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data or not data.get(str(appid), {}).get("success", False):
            return "Unknown Game"
        name = data[str(appid)]["data"].get("name", "Unknown Game")
        return name
    except Exception:
        return "Unknown Game"


def load_config(default_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from a JSON file and optionally override via CLI arguments.

    CLI arguments supported:
      --appid <id>       → manually specify Steam AppID
      --game <url>       → auto-extract AppID from Steam store URL
      --apikey <key>     → override Steam API key
      --output <path>    → change Excel export path
      --config <path>    → specify alternate config.json
    """
    parser = argparse.ArgumentParser(description="Steam Achievement Tracker")
    parser.add_argument("--appid", type=int, help="Steam App ID to track")
    parser.add_argument("--game", type=str, help="Steam store URL to auto-detect AppID and game name")
    parser.add_argument("--apikey", type=str, help="Steam API key override")
    parser.add_argument("--output", type=str, help="Excel output file path")
    parser.add_argument("--config", type=str, default=default_path, help="Path to config.json")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    config: Dict[str, Any] = json.loads(cfg_path.read_text(encoding="utf-8"))

    # Auto-detect AppID and fetch name
    if args.game:
        appid = extract_appid_from_url(args.game)
        game_name = fetch_game_name(appid)
        print(f"[Auto-Detected] AppID = {appid} ({game_name})")
        config["app_id"] = appid
    elif args.appid:
        game_name = fetch_game_name(args.appid)
        print(f"[Using Provided AppID] {args.appid} ({game_name})")
        config["app_id"] = args.appid

    if args.apikey:
        config["api_key"] = args.apikey
    if args.output:
        config["output_path"] = args.output

    return config


# ========== Self-test ==========
if __name__ == "__main__":
    cfg = load_config()
    print(json.dumps(cfg, indent=2))