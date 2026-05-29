import requests
import re
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
    return None

def main():
    raw_channels = []
    
    print("Scraping 24/7 channels...")
    html_247 = get_html("https://daddylive.sx/24-7-channels.php")
    if html_247:
        soup = BeautifulSoup(html_247, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'id='))
        print(f"Found {len(links)} channels on menu.")
        
        for link in links:
            name = link.text.strip()
            href = link.get('href', '')
            if not name or 'id=' not in href: continue
            ch_id = href.split('id=')[1].split('&')[0]
            
            if name == "Sky Calcio 7 (257) Italy": name = "DAZN"
            if ch_id == "853": name = "Canale 5 Italy"
            
            raw_channels.append((name, ch_id))

    final_channels = []
    
    print("Unwrapping hidden players 1-6 for all channels globally...")
    for name, ch_id in raw_channels:
        for play_num in range(1, 7):
            player_url = f"https://daddylive.sx/embed/stream-{ch_id}.php?p={play_num}"
            final_channels.append((f"{name} ({play_num})", player_url))

    print("Scraping scheduled live events...")
    html_schedule = get_html("https://daddylive.sx/index.php")
    if html_schedule:
        soup = BeautifulSoup(html_schedule, 'html.parser')
        event_links = soup.find_all('a', href=re.compile(r'stream-\d+\.php'))
        for link in event_links:
            name = link.text.strip()
            href = link.get('href', '')
            if not name or not href: continue
            if "Stream" in name:
                name = f"Live Event: {name}"
            stream_url = f"https://daddylive.sx/{href}"
            final_channels.append((name, stream_url))

    with open("dlhd.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for name, url in final_channels:
            f.write(f'#EXTINF:-1 group-title="DLHD Combined",{name}\n{url}\n\n')
    print(f"Successfully compiled master list with {len(final_channels)} total streams!")

if __name__ == "__main__":
    main()
