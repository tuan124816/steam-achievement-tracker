"""
excel_utils.py
---------------
Handles exporting styled Excel workbooks for Steam achievements.

Features:
- Alternating light row colors for readability.
- Frozen header and key columns for easy scrolling.
- Auto-adjusted row height based on description length.
- (Optional, commented) Achievement icon insertion beside names.

Usage:
    from tracker.excel_utils import export_styled_excel
    export_styled_excel(df, friends, "output.xlsx")
"""

import math
import xlsxwriter
import requests
from typing import List, Dict, Any
from io import BytesIO
from PIL import Image
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


def download_icon(icon_url):
    """Download an icon and return raw PNG bytes or None."""
    try:
        resp = requests.get(icon_url, timeout=10)
        img = Image.open(BytesIO(resp.content))
        img.thumbnail((32, 32))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return icon_url, buf.getvalue()
    except Exception:
        return icon_url, None


def batch_download_icons(icon_urls):
    """Download icons concurrently for massive speed boost."""
    icon_cache = {}
    icon_urls = list({u for u in icon_urls if u})  # unique, not None

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(download_icon, url) for url in icon_urls]
        for f in as_completed(futures):
            url, img_bytes = f.result()
            icon_cache[url] = img_bytes

    return icon_cache


def export_styled_excel(df: pd.DataFrame, friends: List[Dict[str, Any]], out_path: str) -> None:
    """
    Export a styled Excel workbook containing all achievements and friends' progress.

    Args:
        df (pd.DataFrame): DataFrame containing columns
            ["Icon", "Achievement name", "Description", friend1, friend2, ...]
        friends (list[dict]): List of friends, each with {"name": str}
        out_path (str | Path): Output Excel file path

    Behavior:
        - Creates alternating colored rows.
        - Centers all columns except description (left/top).
        - Dynamically adjusts row height based on text length.
        - Freezes header row and first two columns.
        - Adds ✔ marks where friends have unlocked the achievement.
    """

    # 🎨 Gentle alternating row colors
    colors = ["#F9F9F9", "#EDF4FB", "#F5F7E8", "#F9F0ED", "#F2F2F2", "#EEF7F2"]
    
    # Create workbook and worksheet
    wb = xlsxwriter.Workbook(out_path)
    ws = wb.add_worksheet("Achievements")

    # ====== Define Styles ====== #
    header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 2,
                                "align": "center", "valign": "vcenter"})
    row_fmt = [wb.add_format({"border": 2, "bg_color": c, "align": "center",
                              "valign": "vcenter"}) for c in colors]
    text_fmt = [wb.add_format({"border": 2, "bg_color": c, "align": "left",
                               "valign": "top", "text_wrap": True}) for c in colors]

    # ====== Header ====== #
    cols = ["Icon", "Achievement name", "Description"] + [f["name"] for f in friends]
    for i, name in enumerate(cols):
        ws.write(0, i, name, header_fmt)

    # ====== Column layout ====== #
    ws.set_column(0, 0, 8)      # Icon
    ws.set_column(1, 1, 40)     # Achievement name
    ws.set_column(2, 2, 80)     # Description
    for i in range(3, len(cols)):
        ws.set_column(i, i, 14)
    ws.freeze_panes(1, 3)       # Freeze top row + first three columns

    # --- SPEED BOOST: download all icons in parallel ---
    print("⏳ Downloading icons...")
    all_icon_urls = df["Icon"].tolist()
    icon_cache = batch_download_icons(all_icon_urls)
    print("⚡ Icon download complete.")

    # ====== Data rows ====== #
    for r, row in enumerate(df.itertuples(index=False, name=None), start=1):
        idx = (r - 1) % len(colors)

        icon_url = row[0]
        ach_name = row[1]
        desc = row[2]

        #  ICON INSERTION 
        if icon_url:
            if icon_url not in icon_cache:
                try:
                    resp = requests.get(icon_url, timeout=10)
                    img = Image.open(BytesIO(resp.content))
                    img.thumbnail((32, 32))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    icon_cache[icon_url] = buf.getvalue()
                except Exception:
                    icon_cache[icon_url] = None

            icon_bytes = icon_cache.get(icon_url)

            if icon_bytes:
                ws.insert_image(
                    r, 0, "",
                    {
                        "image_data": BytesIO(icon_bytes),
                        "x_offset": 2,
                        "y_offset": 2,
                    }
                )

        # Write basic text cells
        ws.write(r, 1, ach_name, row_fmt[idx])    # Achievement name
        ws.write(r, 2, desc, text_fmt[idx])   # Description
        
        # Friend columns: ✔ mark if achieved
        for j, f in enumerate(friends):
            ws.write(r, 3 + j, "✔" if bool(row[3 + j]) else "", row_fmt[idx])

        # Adjust row height dynamically
        desc_len = len(row[1] or "")
        lines = max(1, math.ceil(desc_len / 100))
        ws.set_row(r, 18 + lines * 15)

    wb.close()
    print(f"✅ Saved Excel to {out_path}")


# ====== (Planned Feature) Icon Column ====== #
# The following section is commented out but illustrates how to insert
# achievement icons directly in Excel beside their names. Uncomment and
# adapt once the main tracker integrates icon URLs in the schema DataFrame.

"""
    # # 🖼️ Add new column for icons
    # cols = ["Icon", "Achievement name", "Description"] + [f["name"] for f in friends]
    # for i, name in enumerate(cols):
    #     ws.write(0, i, name, header_fmt)

    # ws.set_column(0, 0, 8)    # Icon column (small)
    # ws.set_column(1, 1, 40)   # Achievement name
    # ws.set_column(2, 2, 80)   # Description
    # for i in range(3, len(cols)):
    #     ws.set_column(i, i, 14)
    # ws.freeze_panes(1, 3)

    # # 🎨 Cache downloaded icons
    # icon_cache = {}

    # for r, row in enumerate(df.itertuples(index=False, name=None), start=1):
    #     idx = (r - 1) % len(colors)
    #     icon_url = getattr(row, "Icon", None)
    #     ach_name, desc = row[0], row[1]

    #     # Download & cache icons
    #     if icon_url:
    #         if icon_url not in icon_cache:
    #             try:
    #                 resp = requests.get(icon_url, timeout=10)
    #                 img = Image.open(BytesIO(resp.content))
    #                 img.thumbnail((32, 32))
    #                 buf = BytesIO()
    #                 img.save(buf, format="PNG")
    #                 icon_cache[icon_url] = buf.getvalue()
    #             except Exception:
    #                 icon_cache[icon_url] = None

    #         if icon_cache[icon_url]:
    #             ws.insert_image(r, 0, icon_url, {
    #                 "image_data": BytesIO(icon_cache[icon_url]),
    #                 "x_offset": 3, "y_offset": 3
    #             })

    #     ws.write(r, 1, ach_name, row_fmt[idx])
    #     ws.write(r, 2, desc, text_fmt[idx])

    #     for j, f in enumerate(friends):
    #         ws.write(r, 3 + j, "✔" if bool(row[2 + j]) else "", row_fmt[idx])

    #     desc_len = len(desc or "")
    #     lines = max(1, math.ceil(desc_len / 100))
    #     ws.set_row(r, 30 + lines * 15)
"""


if __name__ == "__main__":
    import pandas as pd
    friends = [{"name": "TestUser"}, {"name": "Another"}]
    df = pd.DataFrame({
        "Achievement name": ["Test A", "Test B"],
        "Description": ["Desc 1", "Desc 2"],
        "TestUser": [True, False],
        "Another": [False, True],
    })
    export_styled_excel(df, friends, "test_output.xlsx")
