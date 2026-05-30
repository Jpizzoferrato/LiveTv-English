import requests
import urllib3
import json
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def slugify(name):
    char_map = {
        'á':'a','à':'a','â':'a','ä':'a','ã':'a','å':'a','æ':'ae',
        'é':'e','è':'e','ê':'e','ë':'e','í':'i','ì':'i','î':'i','ï':'i',
        'ó':'o','ò':'o','ô':'o','ö':'o','õ':'o','ø':'o','œ':'oe',
        'ú':'u','ù':'u','û':'u','ü':'u','ý':'y','ÿ':'y',
        'ñ':'n','ç':'c','ß':'ss','ð':'d','þ':'th'
    }
    text = name.strip().lower()
    for c, r in char_map.items():
        text = text.replace(c, r)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')

def main():
    raw_channels = []
    final_channels = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": "https://daddylive.org/channel"
    }
    
    url = "https://daddylive.org/cache/channels.json"
    print(f"Fetching channels directly from database endpoint: {url}")
    
    try:
        res = requests.get(url, headers=headers, timeout=15, verify=False)
        if res.status_code == 200:
            channels_data = res.json()
            
            for ch in channels_data:
                ch_id = str(ch.get('id', '')).strip()
                name = str(ch.get('title', '')).strip()
                
                if not ch_id or not name or ch_id == "00":
                    continue
                
                if name == "Sky Calcio 7 (257) Italy": name = "DAZN"
                if ch_id == "853": name = "Canale 5 Italy"
                
                raw_channels.append((name, ch_id))
        else:
            print(f"Server returned non-200 status code: {res.status_code}")
    except Exception as e:
        print(f"Network processing error occurred: {e}")

    if not raw_channels:
        print("⚠️ No channels parsed! Stopping run to protect your current dlhd.m3u file.")
        return

    print(f"✅ Successfully loaded {len(raw_channels)} raw channels. Formatting php proxy links without DNS...")
    
    for name, ch_id in raw_channels:
        if ch_id.isdigit() and int(ch_id) < 500:
            stream_identifier = ch_id
        else:
            stream_identifier = slugify(name)
            
        for play_num in range(1, 7):
            # DuckDNS stripped out completely, but the exact proxy stream php path and duplicates remain
            stream_url = f"/dlhd/stream-{stream_identifier}.php?p={play_num}"
            final_channels.append((f"{name} (P{play_num})", stream_url))

    print("Writing processed IPTV playlist lines...")
    with open("dlhd.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        
        valid_idx = 1
        for name, url in final_channels:
            clean_name = str(name).split('\n')[0].strip()
            name_lower = clean_name.lower()
            
            if "adult swim" in name_lower:
                pass 
            else:
                adult_keywords = ["xxx", "porn", "adult", "18+", "playboy", "hustler", "penthouse", "pink", "brazzers"]
                if any(word in name_lower for word in adult_keywords):
                    continue
                
            if "news" in name_lower or "msnbc" in name_lower or "cnn" in name_lower or "cbsn" in name_lower:
                if "fox" in name_lower or "israel" in name_lower or "i24" in name_lower:
                    pass
                else:
                    continue
                    
            is_israel_feed = any(word in name_lower for word in ["israel", "i24", "ch 12 il", "ch 13 il", "ch 11 il"])
            is_sky_sports = "sky sports" in name_lower
            
            if not is_israel_feed and not is_sky_sports:
                global_exclusions = [
                    "uk", "united kingdom", "itv", "bbc", "bt sport", "premier sports", "tnt sports",
                    "italy", "italia", "spain", "espana", "germany", "deutschland", " de", "(de)",
                    "france", "fr ", "portugal", "arabic", "netherlands", "greece", "cyprus", 
                    "albania", "romania", "poland", "polska", "turkey", "turkiye", "indonesia", "indosiar",
                    "india", "pak Pakistan", "latino", "mexico", "argentina", "austria", "slovakia", "slovenia",
                    "sweden", "chile", "colombia", "peru", "ecuador", "venezuela", "uruguay", "paraguay",
                    "tabii", "eleven sports", "dazn", "bein sports", "superSport", "canale", "rai", "rtve"
                ]
                if any(f" {region}" in name_lower or f"({region})" in name_lower or name_lower.endswith(region) or name_lower.startswith(region) for region in global_exclusions):
                    continue
            
            if "live event:" in name_lower or "vs" in name_lower:
                group = "DLHD Live Sports"
            else:
                group = "DLHD United States & General"
                
            f.write(f'#EXTINF:-1 tvg-id="ch-{valid_idx}" tvg-name="{clean_name}" group-title="{group}" http-referrer="https://daddylive.org/",{clean_name}\n')
            f.write(f'#EXTVLCOPT:http-referrer=https://daddylive.org/\n')
            f.write(f'{url}\n\n')
            valid_idx += 1
    print(f"All done! Processed {valid_idx - 1} entries into your playlist.")

if __name__ == "__main__":
    main()
