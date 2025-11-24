import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRY = ROOT / "run_tracker.py"

def run(cmd):
    print(f"\n>>> {cmd}\n")
    subprocess.run(cmd, shell=True, check=True)

def build_windows():
    run(f"pyinstaller --onefile --noconsole --name steam_tracker_win {ENTRY}")

def build_linux():
    run(f"pyinstaller --onedir --noconsole --name steam_tracker_linux {ENTRY}")

def build_macos():
    run(f"pyinstaller --onedir --windowed --name steam_tracker_mac {ENTRY}")

if __name__ == "__main__":
    os.chdir(ROOT)

    system = platform.system()

    if system == "Windows":
        build_windows()

    elif system == "Linux":
        build_linux()

    elif system == "Darwin": 
        build_macos()

    print("\nBuild complete!\n")
