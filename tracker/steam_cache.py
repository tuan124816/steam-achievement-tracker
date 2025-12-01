"""
steam_cache.py
--------------
Handles local caching of:
- Steam game schema
- Achievement icon images

This greatly speeds up repeated runs and enables offline operation.
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any, List
from .utils import log, warn, error

ROOT_DIR = Path(__file__).resolve().parents[1]

CACHE_DIR = ROOT_DIR / "steam_cache"
SCHEMA_DIR = CACHE_DIR / "schema"
ICON_DIR = CACHE_DIR / "icons"

# Create directories safely
CACHE_DIR.mkdir(exist_ok=True)
SCHEMA_DIR.mkdir(exist_ok=True)
ICON_DIR.mkdir(exist_ok=True)


# -----------------------------------------------------
# Save / Load Schema
# -----------------------------------------------------

def get_schema_cache_path(app_id: int) -> Path:
    return SCHEMA_DIR / f"schema_{app_id}.json"


def load_schema_from_cache(app_id: int) -> List[Dict[str, Any]] | None:
    path = get_schema_cache_path(app_id)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            warn("⚠️ Schema cache corrupted — ignoring")
    return None


def save_schema_to_cache(app_id: int, schema: List[Dict[str, Any]]) -> None:
    path = get_schema_cache_path(app_id)
    print('path: ', path)
    path.write_text(json.dumps(schema, indent=2), encoding="utf-8")


# -----------------------------------------------------
# Icon Downloading
# -----------------------------------------------------

def icon_local_path(apiname: str) -> Path:
    return ICON_DIR / f"{apiname}.png"


def download_icon(url: str, apiname: str) -> Path | None:
    """
    Download icon file once and store locally.
    Returns Path to local icon, or None on failure.
    """
    if not url:
        return None

    target_path = icon_local_path(apiname)
    if target_path.exists():
        return target_path

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None

        with open(target_path, "wb") as f:
            f.write(r.content)

        return target_path

    except Exception:
        return None
