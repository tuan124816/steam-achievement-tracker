import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from pathlib import Path

def setup_unicode_font():
    """
    Force matplotlib to use a font that supports all CJK and Unicode characters.
    """

    # Priority 1 — Noto Sans CJK (best choice)
    noto_candidates = [
        "Noto Sans CJK JP",
        "Noto Sans CJK SC",
        "Noto Sans CJK TC",
        "Noto Sans CJK KR",
        "Noto Sans SC",
        "Noto Sans"
    ]

    # Priority 2 — Windows built-in font
    windows_candidates = [
        "Microsoft YaHei",
        "MS Gothic",
        "SimHei",
        "SimSun"
    ]

    # Combined list
    candidates = noto_candidates + windows_candidates

    for font in candidates:
        try:
            fm.findfont(font, fallback_to_default=False)
            matplotlib.rcParams["font.family"] = font
            matplotlib.rcParams["axes.unicode_minus"] = False
            print(f"[Font] Using: {font}")
            return font
        except Exception:
            pass

    print("[Font] WARNING: No CJK font found — Unicode may break.")
    return None


def detect_unsupported_glyphs(strings, font_name=None):
    """
    Detect characters not supported by the current matplotlib font.

    Args:
        strings (list[str]): List of text fields to scan.
        font_name (str|None): If None, use matplotlib's current font.

    Returns:
        dict: { "char": ["string where found", ...], ... }
    """
    # Pick active font
    if font_name is None:
        try:
            font_name = matplotlib.rcParams["font.family"][0]
        except:
            font_name = matplotlib.rcParams["font.family"]

    try:
        font_path = fm.findfont(font_name)
    except:
        print(f"[GlyphCheck] ERROR: Could not locate font '{font_name}'")
        return {}

    font = fm.FontProperties(fname=font_path)
    ftfont = fm.get_font(font_path)

    unsupported = {}

    for s in strings:
        for ch in s:
            if ord(ch) < 128:
                continue  # ASCII always supported

            try:
                glyph_idx = ftfont.get_char_index(ord(ch))
            except Exception:
                glyph_idx = 0

            if glyph_idx == 0:
                unsupported.setdefault(ch, []).append(s)

    return unsupported


def print_unsupported_report(unsupported_map):
    """
    Pretty print unsupported characters found.
    """
    if not unsupported_map:
        print("🎉 All characters are supported by your current font!")
        return

    print("\n=== Unsupported Glyph Report ===")
    for ch, sources in unsupported_map.items():
        hex_code = f"U+{ord(ch):04X}"
        print(f"'{ch}' ({hex_code})")
        for s in set(sources):
            print(f"   • Found in: {s}")
    print("=== End Report ===\n")