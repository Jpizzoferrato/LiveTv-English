import requests
import re
import json
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_html(url):
    # Fixed and hardened browser spoofing headers to bypass data-center blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://daddylive.org/",
        "Connection": "keep-alive"
    }
    try:
        res = requests.get(url, headers=headers, timeout=20, verify=False)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

def main():
    channels = []
    
    # ==========================================
    # 1. SCRAPE 24/7 CHANNELS (.ORG)
    # ==========================================
    print("Scraping 24/7 channels from daddylive.org...")
    html_247 = get_html("https://daddylive.org/24-7-channels.php")
    
    if html_247:
        soup = BeautifulSoup(html_247, 'html.parser')
        cards = soup.find_all('a', class_='card')
        print(f"Found {len(cards)} entries on 24/7 page.")
        
        for card in cards:
            title_div = card.find('div', class_='card__title')
            if not title_div: continue
            name = title_div.text.strip()
            href = card.get('href', '')
            if 'id=' not in href: continue
            ch_id = href.split('id=')[1].split('&')[0]
            
            # Map specific overrides
            if name == "Sky Calcio 7 (257) Italy": name = "DAZN"
            if ch_id == "853": name = "Canale 5 Italy"
            
            # Pure, clean source link pointing to the new live .pk server
            stream_url = f"https://dlhd.pk/stream/stream-{ch_id}.php"
            channels.append((name, stream_url))

    # ==========================================
    # 2. SCRAPE LIVE SCHEDULE EVENTS (.ORG)
    # ==========================================
    print("Scraping live scheduled events from daddylive.org...")
    html_schedule = get_html("https://daddylive.org/index.php")
    
    if html_schedule:
        soup = BeautifulSoup(html_schedule, 'html.parser')
        event_links = soup.find_all('a', href=re.compile(r'stream-\d+\.php'))
        print(f"Found {len(event_links)} scheduled event links.")
        
        for link in event_links:
            name = link.text.strip()
            href = link.get('href', '')
            if not name or not href: continue
            
            if "Stream" in name:
                name = f"Live Event: {name}"
                
            # Extracts the clean stream identifier out of the href link
            match = re.search(r'stream-(\d+)\.php', href)
            if match:
                ch_id = match.group(1)
                # Pure, clean source link pointing to the new live .pk server
                stream_url = f"https://dlhd.pk/stream/stream-{ch_id}.php"
                channels.append((name, stream_url))

    # ==========================================
    # 3. DUPLICATE ENGINE (PREVENTS REMOVAL)
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
    # 4. GENERATE THE COMBINED M3U FILE
    # ==========================================
    output_file = "dlhd.m3u"
    print(f"Writing clean playlist to {output_file}...")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for name, url in final_channels:
                # Add all 6 playlist numbers per stream so your proxy maps them safely
                for play_num in range(1, 7):
                    clean_url = f"{url}?p={play_num}"
                    f.write(f'#EXTINF:-1 group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{clean_url}\n\n")
        print("✅ Clean dlhd.m3u generated successfully with your duplicate engine intact!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
