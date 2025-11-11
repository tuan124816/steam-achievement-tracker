import math
import xlsxwriter
# This is for the image
import requests
from io import BytesIO
from PIL import Image

def export_styled_excel(df, friends, out_path):
    colors = ["#F9F9F9", "#EDF4FB", "#F5F7E8", "#F9F0ED", "#F2F2F2", "#EEF7F2"]
    wb = xlsxwriter.Workbook(out_path)
    ws = wb.add_worksheet("Achievements")

    header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 2,
                                "align": "center", "valign": "vcenter"})
    row_fmt = [wb.add_format({"border": 2, "bg_color": c, "align": "center",
                              "valign": "vcenter"}) for c in colors]
    text_fmt = [wb.add_format({"border": 2, "bg_color": c, "align": "left",
                               "valign": "top", "text_wrap": True}) for c in colors]

    cols = ["Achievement name", "Description"] + [f["name"] for f in friends]
    for i, name in enumerate(cols):
        ws.write(0, i, name, header_fmt)

    ws.set_column(0, 0, 40)
    ws.set_column(1, 1, 80)
    for i in range(2, len(cols)):
        ws.set_column(i, i, 14)
    ws.freeze_panes(1, 2)

    for r, row in enumerate(df.itertuples(index=False, name=None), start=1):
        idx = (r - 1) % len(colors)
        ws.write(r, 0, row[0], row_fmt[idx])
        ws.write(r, 1, row[1], text_fmt[idx])
        for j, f in enumerate(friends):
            ws.write(r, 2 + j, "✔" if bool(row[2 + j]) else "", row_fmt[idx])

        desc_len = len(row[1] or "")
        lines = max(1, math.ceil(desc_len / 100))
        ws.set_row(r, 18 + lines * 15)

    wb.close()
    print(f"✅ Saved Excel to {out_path}")




    # NEED TO REWORK ALL THE CODE FOR THE ICON COLUMN

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

    # # 🎨 Cache for downloaded icons to avoid duplicates
    # icon_cache = {}

    # for r, row in enumerate(df.itertuples(index=False, name=None), start=1):
    #     idx = (r - 1) % len(colors)

    #     # Unpack row fields
    #     # df must include an 'Icon' column before export (icon URL from schema)
    #     icon_url = getattr(row, "Icon", None) if hasattr(row, "Icon") else None
    #     ach_name = row[0]
    #     desc = row[1]

    #     # 🖼️ Insert icon
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
    #             ws.insert_image(r, 0, icon_url, {"image_data": BytesIO(icon_cache[icon_url]), "x_offset": 3, "y_offset": 3})

    #     # Write text data
    #     ws.write(r, 1, ach_name, row_fmt[idx])
    #     ws.write(r, 2, desc, text_fmt[idx])

    #     # Write checkmarks for friends
    #     for j, f in enumerate(friends):
    #         ws.write(r, 3 + j, "✔" if bool(row[2 + j]) else "", row_fmt[idx])

    #     # Adjust height for text
    #     desc_len = len(desc or "")
    #     lines = max(1, math.ceil(desc_len / 100))
    #     ws.set_row(r, 30 + lines * 15)

    # wb.close()
    # print(f"✅ Saved Excel with icons to {out_path}")

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
