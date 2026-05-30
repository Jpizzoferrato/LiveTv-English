import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

    print(f"✅ Successfully loaded {len(raw_channels)} raw channels. Filtering news, porn, and UK...")
    for name, ch_id in raw_channels:
        for play_num in range(1, 7):
            stream_url = f"http://pizzotv.duckdns.org:8080/dlhd/stream-{ch_id}.php?p={play_num}"
            final_channels.append((f"{name} (P{play_num})", stream_url))

    print("Writing processed IPTV playlist lines...")
    with open("dlhd.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        
        valid_idx = 1
        for name, url in final_channels:
            clean_name = str(name).split('\n')[0].strip()
            name_lower = clean_name.lower()
            
            # 1. Strict Porn / Adult Content Filter
            if "adult swim" in name_lower:
                pass 
            else:
                adult_keywords = ["xxx", "porn", "adult", "18+", "playboy", "hustler", "penthouse", "pink", "brazzers"]
                if any(word in name_lower for word in adult_keywords):
                    continue
                
            # 2. News Filter: Block unwanted news, explicitly keeping Fox and Israel
            if "news" in name_lower or "msnbc" in name_lower or "cnn" in name_lower or "cbsn" in name_lower:
                # Safe pass if it's Fox or Israel
                if "fox" in name_lower or "israel" in name_lower or "i24" in name_lower:
                    pass
                else:
                    continue
                    
            # 3. Dynamic Country Whitelist Check: Always keep Israel news feeds
            is_israel_feed = any(word in name_lower for word in ["israel", "i24", "ch 12 il", "ch 13 il", "ch 11 il"])
            
            if not is_israel_feed:
                # Strict UK & Foreign Country Filter for non-Israel channels
                unwanted_regions = [
                    "uk", "united kingdom", "sky sports", "tnt sports", "itv", "bbc", "bt sport", "premier sports",
                    "italy", "italia", "spain", "espana", "germany", "deutschland", " de", "(de)",
                    "france", "fr ", "portugal", "arabic", "netherlands", "greece", "cyprus", 
                    "albania", "romania", "poland", "polska", "turkey", "turkiye", "indonesia", "indosiar",
                    "india", "pakistan", "latino", "mexico", "argentina", "austria", "slovakia", "slovenia",
                    "sweden", "chile", "colombia", "peru", "ecuador", "venezuela", "uruguay", "paraguay"
                ]
                if any(f" {region}" in name_lower or f"({region})" in name_lower or name_lower.endswith(region) for region in unwanted_regions):
                    continue
            
            # 4. Clean US / General Group Assignment
            if "live event:" in name_lower or "vs" in name_lower:
                group = "DLHD Live Sports"
            else:
                group = "DLHD United States & General"
                
            f.write(f'#EXTINF:-1 tvg-id="ch-{valid_idx}" tvg-name="{clean_name}" group-title="{group}",{clean_name}\n')
            f.write(f'{url}\n\n')
            valid_idx += 1
    print(f"All done! Processed {valid_idx - 1} filtered entries into your playlist.")

if __name__ == "__main__":
    main()
