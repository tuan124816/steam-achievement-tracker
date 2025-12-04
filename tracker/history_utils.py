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
import matplotlib.pyplot as plt

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


def save_history(app_id: int, snapshot: dict, history_dir: Optional[Path] = None) -> Path:
    """
    Save a timestamped JSON snapshot and update latest.json.

    Returns:
        Path to the written timestamped snapshot.
    """
    app_dir = _ensure_app_dir(app_id, history_dir)
    # snapshot = _make_snapshot(app_id, df, friends)

    # ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    # filename = f"{ts}.json"
    # target = app_dir / filename
    # latest = app_dir / "latest.json"

    # try:
    #     target.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    #     latest.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    #     log(f"Saved history: {target}")
    # except Exception as e:
    #     log(f"Error saving history: {e}")
    #     raise

    # return target
    """Save a snapshot into history/<app_id>/<timestamp>.json"""

    # app_dir = HISTORY_DIR / str(app_id)
    # app_dir.mkdir(parents=True, exist_ok=True)

    ts = snapshot["timestamp"]
    path = app_dir / f"{ts}.json"
    latest = app_dir / "latest.json"
    print(f'{ts} \n {path}')

    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"📁 Saved snapshot: {path}")


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


def compare_snapshots(prev: dict, curr: dict) -> dict:
    """
    Compare two snapshots of friend achievement progress.

    Returns a diff dict:
    {
        "friendname": {
            "new_count": int,
            "new_achievements": [api_name, ...]
        },
        ...
    }
    """
    if prev is None:
        # No previous history → everything is "new" compared to nothing
        diff = {}
        for friend, curr_list in curr["friends"].items():
            diff[friend] = {
                "new_count": len(curr_list),
                "new_achievements": curr_list
            }
        return diff

    diff = {}

    for friend, curr_data in curr["friends"].items():
        curr_list = curr_data.get("achievements", [])
        curr_set = set(curr_list)

        if friend not in prev["friends"]:
            # Friend did not exist before — treat everything as new
            diff[friend] = {
                "new_count": len(curr_list),
                "new_achievements": curr_list
            }
            continue

        prev_list = prev["friends"][friend].get("achievements", [])
        prev_set = set(prev_list)

        gained = sorted(curr_set - prev_set)

        diff[friend] = {
            "new_count": len(gained),
            "new_achievements": gained
        }
            

    return diff


def build_diff_text(diff: dict) -> str:
    lines = []
    lines.append("Steam Achievement Tracker — Progress Changes")
    lines.append("---------------------------------------------------")

    for friend, d in diff.items():
        if d["new_count"] == 0:
            lines.append(f"{friend}: no new achievements.")
        else:
            lines.append(f"{friend}: +{d['new_count']} new achievement(s):")
            for a in d["new_achievements"]:
                lines.append(f"   • {a}")

    return "\n".join(lines)


def save_diff_text(app_id: int, diff_text: str):
    out = HISTORY_ROOT / str(app_id)
    out.mkdir(parents=True, exist_ok=True)

    fname = out / f"diff_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
    fname.write_text(diff_text, encoding="utf-8")
    return fname


def build_snapshot(app_id: int, df: pd.DataFrame, friends: list, run_timestamp: str) -> dict:
    """
    Convert the achievement DataFrame into a snapshot structure suitable for saving.

    Snapshot format:
    {
        "app_id": 12345,
        "timestamp": "...",
        "total_achievements": 52,
        "friends": {
            "Alice": {
                "unlocked": 30,
                "achievements": ["ACH_A", "ACH_B", ...]
            },
            "Bob": { ... }
        }
    }
    """
    snapshot = {
        "app_id": app_id,
        "timestamp": run_timestamp,
        "total_achievements": len(df),
        "friends": {}
    }

    # For each friend
    for friend in friends:
        name = friend["name"]
        unlocked_list = df[df[name] == True]["Achievement name"].tolist()

        snapshot["friends"][name] = {
            "unlocked": len(unlocked_list),
            "achievements": unlocked_list
        }

    return snapshot


def plot_progress(app_id: int, history_dir: Path | None = None) -> None:
    """
    Generate progress graphs for each friend based on history snapshots.
    Saves PNG graphs into history/<app_id>/graphs/
    """
    app_dir = _ensure_app_dir(app_id, history_dir)
    graph_dir = app_dir / "graphs"
    graph_dir.mkdir(parents=True, exist_ok=True)

    snapshots = load_history(app_id, history_dir)

    if not snapshots:
        print("📭 No history found — nothing to plot.")
        return

    # Collect timeline of achievement counts per friend
    timeline = {}  # { friend_name: [(timestamp, count), ...] }

    for snap in snapshots:
        ts = snap["timestamp"]
        for friend, data in snap["friends"].items():
            unlocked = data.get("unlocked", 0)
            timeline.setdefault(friend, []).append((ts, unlocked))

    # Plot each friend's graph
    for friend, entries in timeline.items():
        # Sort by timestamp
        entries = sorted(entries, key=lambda x: x[0])
        x = [ts for ts, _ in entries]
        y = [count for _, count in entries]

        plt.figure(figsize=(8,4))
        plt.plot(x, y, marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title(f"{friend} — Achievement Progress")
        plt.xlabel("Time")
        plt.ylabel("Unlocked achievements")
        plt.tight_layout()

        out = graph_dir / f"{friend}.png"
        plt.savefig(out)
        plt.close()

        print(f"📈 Saved graph: {out}")