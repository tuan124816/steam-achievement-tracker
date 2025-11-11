import pickle, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def generate_steam_cookies(cookie_file="steam_cookies.pkl"):
    """Launches a Chrome window for manual login, saves cookies once logged in."""
    print("\n🌐 No Steam cookie file detected.")
    print("A Chrome window will open — please log into Steam manually.")
    print("After successful login, close the window to continue.\n")

    opts = Options()
    opts.add_experimental_option("detach", True)  # keeps window open
    driver = webdriver.Chrome(options=opts)
    driver.get("https://steamcommunity.com/login")
    input("✅ Press [Enter] here after you've logged in successfully...")

    cookies = driver.get_cookies()
    pickle.dump(cookies, open(cookie_file, "wb"))
    driver.quit()

    print(f"\n💾 Cookies saved successfully to: {cookie_file}")

if __name__ == "__main__":
    generate_steam_cookies(cookie_file=Path(__file__).resolve().parent.parent / "steam_cookies.pkl")