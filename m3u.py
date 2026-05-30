import requests
import re
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_html(url):
    # Hardened headers to mimic a clean mobile device connection
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    try:
        res = requests.get(url, headers=headers, timeout=25, verify=False)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

def main():
    channels = []
    
    # Using the primary web mirror to fetch the layout safely
    print("Scraping 24/7 channels from source mirror...")
    html_247 = get_html("https://daddylive.org/24-7-channels.php")
    
    # If the main domain blocks the GitHub IP, fallback to the community link hub
    if not html_247:
        print("⚠️ Primary domain blocked or timed out. Attempting backup hub stream fetch...")
        html_247 = get_html("https://dlhd.link")

    if html_247:
        soup = BeautifulSoup(html_247, 'html.parser')
        cards = soup.find_all('a', class_='card')
        print(f"Found {len(cards)} entries on channel layout.")
        
        for card in cards:
            title_div = card.find('div', class_='card__title')
            if not title_div: continue
            name = title_div.text.strip()
            href = card.get('href', '')
            
            # Extract stream ID from standard or alternative layout formats
            ch_id = None
            if 'id=' in href:
                ch_id = href.split('id=')[1].split('&')[0]
            elif 'stream-' in href:
                match = re.search(r'stream-(\d+)\.php', href)
                if match: ch_id = match.group(1)
                
            if not ch_id: continue
            
            if name == "Sky Calcio 7 (257) Italy": name = "DAZN"
            if ch_id == "853": name = "Canale 5 Italy"
            
            # Map structural paths directly to the live stream engine
            stream_url = f"https://dlhd.pk/stream/stream-{ch_id}.php"
            channels.append((name, stream_url))

    # Safety Guard: If firewalls return completely empty lists, 
    # stop execution to protect any existing local backup files.
    if not channels:
        print("❌ Scraper failed to fetch channel data. Halting write to prevent empty playlist file.")
        return

    # ==========================================
    # DUPLICATE ENGINE (PREVENTS REMOVAL)
    # ==========================================
    name_counts = {}
    for name, _ in channels:
        name_counts[name] = name_counts.get(name, 0) + 1

    final_channels = []
    name_counter = {}
    for name, url in channels:
        if name_counts[name] > 1:
            if name not in name_counter:
                name_counter[name] = 1
            else:
                name_counter[name] += 1
            new_name = f"{name} ({name_counter[name]})"
            final_channels.append((new_name, url))
        else:
            final_channels.append((name, url))

    # ==========================================
    # GENERATE THE COMBINED M3U FILE
    # ==========================================
    output_file = "dlhd.m3u"
    print(f"Writing clean playlist with {len(final_channels)} streams...")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for name, url in final_channels:
                for play_num in range(1, 7):
                    clean_url = f"{url}?p={play_num}"
                    f.write(f'#EXTINF:-1 group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{clean_url}\n\n")
        print("✅ Clean dlhd.m3u generated successfully with duplicate filtering intact!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()

