from tqdm import tqdm
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def progress_bar(iterable, desc="Processing"):
    return tqdm(iterable, desc=desc, ncols=80)