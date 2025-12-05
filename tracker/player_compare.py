"""
player_compare.py
-----------------
Generate comparison charts for friends' achievement progress.

Functions:
- generate_all_comparison_charts(df, friends, app_id, theme="light", out_dir=None)
    -> Creates bar chart (current unlocked counts) and line chart (history over time).
- pick_font_for_text() - attempts to find a sensible font that supports most Unicode.

Themes supported: "light", "steam" (dark).
"""

from __future__ import annotations
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.font_manager import findSystemFonts, FontProperties
from pathlib import Path
from typing import List, Dict, Any, Optional
import datetime
import os

from .history_utils import load_history
from .utils import log

# ----- Theme palettes ----- #
LIGHT_THEME = {
    "bg": "white",
    "fg": "black",
    "palette": ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974"],
    "grid": True
}

STEAM_THEME = {
    "bg": "#0f1720",
    "fg": "#d7e6f2",
    "palette": ["#66c0f4", "#a1d6ff", "#4da9e6", "#8ec9ff", "#c7d5e0"],
    "grid": False
}


def _ensure_out_dir(app_id: int, out_dir: Optional[Path] = None) -> Path:
    root = Path(out_dir or Path("history") / str(app_id) / "charts")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _pick_font() -> Optional[FontProperties]:
    """
    Try to pick a font that supports wide unicode ranges (CJK).
    Returns a FontProperties or None to use Matplotlib default.
    """
    # Preferred fonts (system-dependent). These are suggestions; if not present
    # matplotlib will fallback.
    candidates = [
        "Noto Sans CJK JP", "Noto Sans CJK SC", "Noto Sans CJK TC",
        "Noto Sans", "Arial Unicode MS", "Microsoft YaHei", "SimHei",
        "DejaVu Sans"
    ]

    sys_fonts = {Path(p).stem.lower(): p for p in findSystemFonts()}
    for cand in candidates:
        key = cand.lower()
        for fname_stem, path in sys_fonts.items():
            if key in fname_stem:
                try:
                    return FontProperties(fname=path)
                except Exception:
                    continue
    # fallback None (matplotlib default)
    return None


def generate_all_comparison_charts(df, friends: List[Dict[str, Any]], app_id: int,
                                   theme: str = "light", out_dir: Optional[str] = None) -> List[Path]:
    """
    Generate charts and save them to disk.

    Produces:
      - bar_current.png : current unlocked counts per friend
      - line_history.png : unlocked progress over time per friend (if history exists)

    Args:
        df (pd.DataFrame): DataFrame with columns including friends' names.
        friends (list[dict]): friends list (dicts must contain 'name')
        app_id (int): AppID (used for save path)
        theme (str): "light" or "steam"
        out_dir (str|Path|None): override output directory (optional)

    Returns:
        list[Path]: saved image paths
    """
    outp = _ensure_out_dir(app_id, Path(out_dir) if out_dir else None)
    chart_paths = []

    th = LIGHT_THEME if theme == "light" else STEAM_THEME
    mpl_font = _pick_font()
    if mpl_font:
        matplotlib.rcParams["font.family"] = mpl_font.get_name()

    # 1) Bar chart — current unlocked counts
    names = []
    counts = []
    for f in friends:
        name = f.get("name")
        names.append(name)
        if name in df.columns:
            counts.append(int(df[name].astype(int).sum()))
        else:
            counts.append(0)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(th["bg"])
    ax.set_facecolor(th["bg"])
    bars = ax.bar(range(len(names)), counts, color=th["palette"] * ((len(names) // len(th["palette"])) + 1))
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", color=th["fg"])
    ax.set_ylabel("Unlocked achievements", color=th["fg"])
    ax.set_title("Current unlocked achievements per friend", color=th["fg"])
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    if th["grid"]:
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    # hide spines with theme-appropriate color
    for spine in ax.spines.values():
        spine.set_color(th["fg"])

    # label bar values
    for rect in bars:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, h + 0.5, str(int(h)),
                ha="center", va="bottom", color=th["fg"], fontsize=9)

    path_bar = outp / "bar_current.png"
    plt.tight_layout()
    plt.savefig(path_bar, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path_bar)
    log(f"Saved chart: {path_bar}")

    # 2) Line chart — load history snapshots and plot per friend over time
    snapshots = load_history(app_id)
    if snapshots and len(snapshots) >= 1:
        # build timeseries per friend
        times = []
        friend_series = {f["name"]: [] for f in friends}
        for snap in snapshots:
            # snapshot timestamp should be ISO or our string; try parse
            ts = snap.get("timestamp")
            try:
                t = datetime.datetime.fromisoformat(ts)
            except Exception:
                # fallback: try parse using common format
                try:
                    t = datetime.datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")
                except Exception:
                    # fallback to file modification time (not ideal)
                    t = None
            times.append(t if t else datetime.datetime.now())

            # each snapshot stores friends as mapping as implemented in build_snapshot
            for f in friends:
                name = f["name"]
                val = 0
                fd = snap.get("friends", {})
                if isinstance(fd, dict):
                    # new format: friends is mapping name -> {unlocked, achievements}
                    ent = fd.get(name, {})
                    if isinstance(ent, dict):
                        val = int(ent.get("unlocked", 0))
                elif isinstance(fd, list):
                    # older format: list of summaries
                    for item in fd:
                        if item.get("name") == name:
                            val = int(item.get("unlocked", 0))
                            break
                friend_series[name].append(val)

        fig2, ax2 = plt.subplots(figsize=(11, 6))
        fig2.patch.set_facecolor(th["bg"])
        ax2.set_facecolor(th["bg"])
        for idx, (name, series) in enumerate(friend_series.items()):
            ax2.plot(times[:len(series)], series, marker="o",
                     label=name, color=th["palette"][idx % len(th["palette"])])
        ax2.set_xlabel("Time", color=th["fg"])
        ax2.set_ylabel("Unlocked achievements", color=th["fg"])
        ax2.set_title("Achievement progress over time", color=th["fg"])
        ax2.legend(loc="upper left", fontsize=8)
        if th["grid"]:
            ax2.grid(linestyle="--", alpha=0.35)
        for spine in ax2.spines.values():
            spine.set_color(th["fg"])
        plt.xticks(rotation=30)
        path_line = outp / "line_history.png"
        plt.tight_layout()
        plt.savefig(path_line, facecolor=fig2.get_facecolor(), bbox_inches="tight")
        plt.close(fig2)
        chart_paths.append(path_line)
        log(f"Saved chart: {path_line}")
    else:
        log("No history snapshots found — skipping history chart.")

    return chart_paths
