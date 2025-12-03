"""
history_utils.py
----------------
Save and load historical snapshots of achievement progress.

Functions:
- save_history(app_id, df, friends, history_dir=None)
- load_latest_history(app_id, history_dir=None)
- load_history(app_id, history_dir=None)

History layout:
history/<appid>/YYYY-MM-DD_HH-MM.json
history/<appid>/latest.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .utils import log

HISTORY_ROOT = Path("history")


def _ensure_app_dir(app_id: int, history_dir: Optional[Path] = None) -> Path:
    root = history_dir or HISTORY_ROOT
    app_dir = Path(root) / str(app_id)
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def _make_snapshot(app_id: int, df: pd.DataFrame, friends: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build the snapshot dict from DataFrame and friends list.
    Snapshot format matches history_format.md spec.
    """
    total = int(len(df))
    friends_summary: List[Dict[str, Any]] = []
    for f in friends:
        name = f.get("name")
        steamid = f.get("steamid")
        # If column missing, treat as 0
        if name in df.columns:
            unlocked = int(df[name].astype(int).sum())
        else:
            unlocked = 0
        friends_summary.append({
            "name": name,
            "steamid": steamid,
            "unlocked": unlocked,
            "total": total
        })

    snapshot = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "app_id": int(app_id),
        "friends": friends_summary
    }
    return snapshot


def save_history(app_id: int, df: pd.DataFrame, friends: List[Dict[str, Any]], history_dir: Optional[Path] = None) -> Path:
    """
    Save a timestamped JSON snapshot and update latest.json.

    Returns:
        Path to the written timestamped snapshot.
    """
    app_dir = _ensure_app_dir(app_id, history_dir)
    snapshot = _make_snapshot(app_id, df, friends)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{ts}.json"
    target = app_dir / filename
    latest = app_dir / "latest.json"

    try:
        target.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        latest.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"Saved history: {target}")
    except Exception as e:
        log(f"Error saving history: {e}")
        raise

    return target


def load_latest_history(app_id: int, history_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Load latest.json for an app if exists.
    """
    app_dir = _ensure_app_dir(app_id, history_dir)
    latest = app_dir / "latest.json"
    if not latest.exists():
        return None
    try:
        return json.loads(latest.read_text(encoding="utf-8"))
    except Exception:
        log("Failed to read latest history (corrupted?).")
        return None


def load_history(app_id: int, history_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load all snapshots for an app, sorted oldest -> newest.
    """
    app_dir = _ensure_app_dir(app_id, history_dir)
    snapshots: List[Dict[str, Any]] = []
    for p in sorted(app_dir.glob("*.json")):
        try:
            snapshots.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            # skip corrupted entries
            log(f"Skipping corrupted history file: {p}")
            continue
    return snapshots
