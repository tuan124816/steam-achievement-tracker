"""
cookie_setup.py
----------------
Helpers to create and reuse a logged-in Selenium Chrome session by
saving/loading Steam cookies (steam_cookies.pkl). Intended for users
who need to scrape private Steam profiles.

Usage:
    # Interactive cookie generation (saves to project root)
    python -m tracker.cookie_setup
"""

import pickle, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ========== Defaults ==========
# Default output cookie file location: project root / steam_cookies.pkl
DEFAULT_COOKIE_FILE = Path(__file__).resolve().parent.parent / "steam_cookies.pkl"


# ========== Cookie generation ==========
def generate_steam_cookies(cookie_file: Path | str = DEFAULT_COOKIE_FILE) -> Path:
    """
    Launch a Chrome window for manual Steam login and save cookies to disk.

    Args:
        cookie_file (Path | str): Path where the cookies will be saved.
                                 Defaults to <project_root>/steam_cookies.pkl.

    Returns:
        Path: The path to the saved cookie file.

    Behavior:
    - Opens a Chrome window (non-headless) and waits for the user to log in.
    - After the user confirms (press Enter), cookies are serialized to the file.
    """
    cookie_path = Path(cookie_file).resolve()

    print("\n🌐 No Steam cookie file detected.")
    print("A Chrome window will open — please log into Steam manually.")
    print("After successful login, return here and press Enter to continue.\n")

    opts = Options()
    # Keep the window open so the user can interact
    opts.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("https://steamcommunity.com/login")
        input("✅ Press [Enter] here after you've logged in successfully...")

        cookies = driver.get_cookies()
        # Write cookie file atomically using with-statement
        cookie_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cookie_path, "wb") as fh:
            pickle.dump(cookies, fh)

        print(f"\n💾 Cookies saved successfully to: {cookie_path}")
        return cookie_path

    finally:
        # Make sure to close the driver if possible. If the user closed the window manually,
        # this may raise; ignore such exceptions to avoid noisy stack traces.
        try:
            driver.quit()
        except Exception:
            pass


# ========== Self-test / CLI entrypoint ==========
if __name__ == "__main__":
    # When executed as a module, generate the cookie file in the repository root.
    generate_steam_cookies(cookie_file=DEFAULT_COOKIE_FILE)