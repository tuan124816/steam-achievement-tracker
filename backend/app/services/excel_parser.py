import pandas as pd
from pathlib import Path

def parse_achievement_excel(path: Path):
    """
    Expected columns (adjust if needed):
    - player
    - total_achievements
    - unlocked
    - percentage
    """
    df = pd.read_excel(path)

    results = {}
    for _, row in df.iterrows():
        player = str(row["player"])
        results[player] = {
            "total": int(row["total_achievements"]),
            "unlocked": int(row["unlocked"]),
            "percent": float(row["percentage"]),
        }

    return results
