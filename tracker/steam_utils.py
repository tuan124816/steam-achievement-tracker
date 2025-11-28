import os
import re
import time
import requests
from typing import Optional


STEAM_RESOLVE_URL = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"


def _normalize_input(value: str) -> str:
    v = (value or "").strip()
    v = re.sub(r"^https?://", "", v, flags=re.IGNORECASE)
    v = re.sub(r"^www\.", "", v, flags=re.IGNORECASE)

    if "/" in v:
        parts = [p for p in v.split("/") if p]
        if "profiles" in parts:
            i = parts.index("profiles")
            if i + 1 < len(parts):
                return parts[i + 1]
        if "id" in parts:
            i = parts.index("id")
            if i + 1 < len(parts):
                return parts[i + 1]
        return parts[-1]

    return v


def is_probable_steamid64(candidate: str) -> bool:
    return bool(re.fullmatch(r"7\d{16}", candidate))


def resolve_vanity_url(
    vanity_or_id: str,
    api_key: Optional[str] = None,
    timeout: float = 8.0,
    retries: int = 2,
    backoff: float = 1.0,
) -> Optional[str]:

    if api_key is None:
        api_key = os.getenv("STEAM_API_KEY")
    if not api_key:
        raise ValueError("Steam API key required.")

    candidate = _normalize_input(vanity_or_id)
    if not candidate:
        return None

    if is_probable_steamid64(candidate):
        return candidate

    params = {"key": api_key, "vanityurl": candidate}

    attempt = 0
    while attempt <= retries:
        try:
            r = requests.get(STEAM_RESOLVE_URL, params=params, timeout=timeout)
            if r.status_code != 200:
                attempt += 1
                time.sleep(backoff * (2 ** (attempt - 1)))
                continue

            data = r.json()
            resp = data.get("response", {})
            if int(resp.get("success", 0)) == 1:
                return resp.get("steamid")
            return None

        except requests.RequestException:
            attempt += 1
            if attempt > retries:
                return None
            time.sleep(backoff * (2 ** (attempt - 1)))

    return None


if __name__ == "__main__":
    import getpass

    print("Vanity -> SteamID64 resolver test")
    print("---------------------------------")
    api_key_env = os.getenv("STEAM_API_KEY")
    if api_key_env:
        print("Using STEAM_API_KEY from environment.")
        use_env = True
    else:
        use_env = False

    if not use_env:
        # Prompt for API key (hidden)
        api_key_input = getpass.getpass("Enter Steam API key (or press Enter to abort): ").strip()
        if not api_key_input:
            print("No API key provided; aborting.")
            raise SystemExit(1)
        api_key = api_key_input
    else:
        api_key = api_key_env

    samples = [
        "https://steamcommunity.com/id/gaben/",
        "gaben",
        "https://steamcommunity.com/profiles/76561197960287930/",
        "76561197960287930",
        "thisuserdoesnotexistprobably"
    ]

    print("\nTesting sample inputs:")
    for s in samples:
        sid = resolve_vanity_url(s, api_key)
        print(f"  {s!r:50} -> {sid}")

    # Interactive single test
    while True:
        val = input("\nEnter vanity/URL/steamid (or blank to exit): ").strip()
        if not val:
            break
        sid = resolve_vanity_url(val, api_key)
        print("Result:", sid)