# 🧩 Setup Instructions

This guide will help you install and run the **Steam Achievement Tracker** from scratch.


## ⚙️ 1. Prerequisites

Make sure you have the following installed:

- **Python 3.10+**

- **Google Chrome** (latest version)

- **ChromeDriver** (auto-installed via Selenium if not found)

- A **Steam API** key
→ Get it here: https://steamcommunity.com/dev/apikey

## 📦 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/steam-achievement-tracker.git
cd steam-achievement-tracker
pip install -r requirements.txt
```

## 🔑 3. Configuration
Step 1 — Edit `config.json`
```json
{
  "api_key": "YOUR_STEAM_API_KEY",
  "app_id": 3527290,
  "output_path": "achievements.xlsx",
  "friends": [
    { "name": "YourSteamName", "steamid": "76561198000000000" },
    { "name": "AnotherFriend", "steamid": "76561198011111111" }
  ]
}
```

You can find a user’s SteamID using tools like https://steamid.io


## 🍪 4. Steam Cookies Setup (for private profiles)

Some friends may have **private Steam profiles** - in that case, the API can’t access their achievements.
To handle this, we log in via Selenium using your Steam cookies.

**Run cookie generator**:
```bash
python -m tracker.cookie_setup
```

This will:

- Open Chrome and ask you to log into Steam.

- Save your cookies automatically as steam_cookies.pkl in the project root.

✅ Once done, your cookies will automatically be reused for scraping private profiles.

## 🚀 5. Running the Tracker
Option 1 - Use `config.json`
```bash
python run_tracker.py
```

Option 2 - Pass arguments manually
```bash
python run_tracker.py --appid 3527290 --apikey YOUR_KEY
```

Option 3 - Auto-detect game from URL
```bash
python run_tracker.py --game https://store.steampowered.com/app/3527290/PEAK/
```


The tracker will:

- Auto-fetch the game’s achievements

- Retrieve progress for all your listed friends

- Export everything to a styled Excel file in the output/ folder

## 📊 6. Excel Output Preview

- ✅ **Top row + first two columns are frozen** for easy scrolling

- 🎨 Alternating row colors

- 💬 Wrapped text for long descriptions

- ✔️ Checkmarks for unlocked achievements

Example:

| Achievement Name | Description | You | Friend 1 | Friend 2 |
|--------|-----------|:------:|:------:|:------:|
| Peak Badge | Reach the PEAK. | ✔ |  | ✔ |

## 🧰 7. Troubleshooting

| Issue | Possible Fix |
|:------|:------|
| `steam_cookies.pkl not found` | Run `python -m tracker.cookie_setup` again |
| `selenium.common.exceptions` | Chrome/ChromeDriver version mismatch - update Chrome |
| Excel file empty | Check that `app_id` is valid and you own the game |


## 🧠 8. Tips

- You can mix **public** and **private** friends - the tracker automatically detects which method to use.

- To add more friends, just edit `config.json` and re-run.

- Output files can be renamed freely (they’re never overwritten without confirmation).

## 🏁 Done!

Once everything runs, you’ll get your achievement progress saved beautifully in Excel.
Share it with your friends or track your 100% runs easily!