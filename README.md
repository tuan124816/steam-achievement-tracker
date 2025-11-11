# 🏆 Steam Achievement Tracker

A Python tool that automatically fetches and compares **Steam game achievements** for you and your friends - supporting both **public** and **private** profiles.

## ✨ Features

- 🧠 **Auto-detect AppID** from Steam game URLs

- 🎯 **Public + Private Profile Support** (via API or Selenium cookies)

- 📊 **Beautiful Excel Export**

   - Alternating colors

   - Frozen top/side headers

   - Wrapped text

   - Achievement checkmarks

⚙️ **Configurable via** `config.json` or **CLI arguments**

🔄 **Automatic cookie setup** if none found

## 🚀 Quick Start
```bash
git clone https://github.com/yourusername/steam-achievement-tracker.git
cd steam-achievement-tracker
pip install -r requirements.txt
python run_tracker.py --game https://store.steampowered.com/app/3527290/PEAK/
```

✅ That’s it - the program auto-detects the game, checks your friends’ progress, and exports everything to Excel.

## 🧩 Project Structure
```
steam-achievement-tracker/
│
├── tracker/
│   ├── __init__.py
│   ├── config.py          # Loads config.json and CLI overrides
│   ├── constants.py       # Global settings (headers, delays, paths)
│   ├── fetchers.py        # Steam API + Selenium scraping
│   ├── excel_utils.py     # Excel export and styling
│   ├── main.py            # Core logic
│   ├── utils.py           # Logging and helpers
│   └── cookie_setup.py    # Interactive Steam login (cookies)
│
├── config.json
├── run_tracker.py
├── requirements.txt
├── README.md
└── setup_instructions.md
```

## ⚙️ Configuration

All settings (API key, AppID, friend list, output path) live in `config.json`.

Example:
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

## 📘 Full Setup Guide

👉 See setup_instructions.md [`setup_instructions.md`](setup_instructions.md)
 for:

- Cookie generation

- Command-line arguments

- Troubleshooting

- Output examples

## 🚧 Roadmap
🎨 **Visual & UX**

 - Embed achievement icons next to names in Excel

 - Add game title, fetch date, and total achievements summary at top of sheet

📊 **Analytics**

 - Add leaderboard: total unlocked, completion %

 - Track unlock timestamps (first to unlock highlight)

⚡ **Performance**

 - Optionally auto-refresh every X hours via --interval

🔔 **Notifications**

 - Send completion summary to Discord

## 🧑‍💻 Author

Tuấn Nguyễn Huy

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## ✨ Acknowledgments

- [Steam API documentation](https://developer.valvesoftware.com/wiki/Steam_Web_API)
- [Steam Web API Documentation](https://steamcommunity.com/dev)
- ChatGPT for debuging

