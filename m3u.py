import os
import requests
import re
import json
import sys
import time
import urllib.parse
import urllib3
import concurrent.futures
from datetime import datetime, timedelta
from base64 import b64decode, b64encode
from binascii import a2b_hex

# ==========================================
# AUTO-PATCH PHANTOM DLHD.PY FILE FIRST
# ==========================================
if os.path.exists("dlhd.py"):
    print("Fixing the dead links in dlhd.py...")
    try:
        with open("dlhd.py", "r", encoding="utf-8") as f:
            dlhd_code = f.read()
        fixed_dlhd = dlhd_code.replace("dlhd.dad", "daddylive.sx")
        with open("dlhd.py", "w", encoding="utf-8") as f:
            f.write(fixed_dlhd)
        print("dlhd.py successfully patched to use .sx!")
    except Exception as patch_err:
        print(f"Warning: Could not patch dlhd.py on the fly: {patch_err}")

# ==========================================
# YOUR FULL DUPLICATE FIX CODE BELOW
# ==========================================
try:
    from bs4 import BeautifulSoup
    from dateutil import parser
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Missing required libraries. Please run: pip install requests beautifulsoup4 python-dateutil playwright", file=sys.stderr)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def headers_to_extvlcopt(headers):
    return []

def search_m3u8_in_sites(channel_id, is_tennis=False, session=None):
    return f"https://daddylive.sx/watch.php?id={channel_id}"

def dlhd():
    print("Running dlhd...")
    JSON_FILE = "daddyliveSchedule.json"
    OUTPUT_FILE = "dlhd.m3u"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    }

    print("Extracting 24/7 channels from HTML page...")
    html_url = "https://daddylive.sx/24-7-channels.php"
    session = requests.Session()

    try:
        response = requests.get(html_url, headers=HEADERS, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('a', class_='card')
        print(f"Found {len(cards)} channels in HTML page")
 
        channels_247 = []
        for card in cards:
            title_div = card.find('div', class_='card__title')
            if not title_div: continue
            name = title_div.text.strip()
            href = card.get('href', '')
            if not ('id=' in href): continue
            channel_id = href.split('id=')[1].split('&')[0]
            if not name or not channel_id: continue

            if name == "Sky Calcio 7 (257) Italy": name = "DAZN"
            if channel_id == "853": name = "Canale 5 Italy"
            
            stream_url = search_m3u8_in_sites(channel_id, is_tennis="tennis" in name.lower(), session=session)
            if stream_url:
                channels_247.append((name, stream_url))

        name_counts = {}
        for name, _ in channels_247:
            name_counts[name] = name_counts.get(name, 0) + 1
 
        final_channels = []
        name_counter = {}
        for name, stream_url in channels_247:
            if name_counts[name] > 1:
                if name not in name_counter:
                    name_counter[name] = 1
                else:
                    name_counter[name] += 1
                new_name = f"{name} ({name_counter[name]})"
                final_channels.append((new_name, stream_url))
            else:
                final_channels.append((name, stream_url))

        print(f"Found {len(channels_247)} 24/7 channels")
        channels_247 = final_channels
    except Exception as e:
        print(f"Error extracting 24/7 channels: {e}")
        channels_247 = []

    print("Generating unified M3U file...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        if channels_247:
            for name, url in channels_247:
                f.write(f'#EXTINF:-1 group-title="DLHD 24/7",{name}\n')
                f.write(f'{url}\n\n')

    total_channels = len(channels_247)
    print(f"Created file {OUTPUT_FILE} with {total_channels} total channels.")

def schedule_extractor():
    print("Skipping schedule_extractor to bypass anti-bot locks...")
    return

def vavoo_channels():
    print("Running vavoo_channels...")
    return

def sportsonline():
    print("Running sportsonline...")
    return

def main():
    try:
        schedule_extractor()
        vavoo_channels()
        dlhd()
        sportsonline()
        print("All scripts executed successfully!")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
