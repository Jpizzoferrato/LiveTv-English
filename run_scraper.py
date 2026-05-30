import os
import requests

def fetch_channels():
    """Reads your local repository cache files to pull all 3,900+ channels."""
    print("Reading repository schedule caches...")
    channels = []
    
    # Check your cached files to load the full channel lineup instantly
    for cache_file in ["known_channel_ids.json", "daddyliveSchedule.json"]:
        if os.path.exists(cache_file):
            import json
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for k, v in data.items():
                        if str(v).isdigit(): 
                            channels.append((str(k), str(v)))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            cid = item.get("id") or item.get("ch_id") or item.get("channel_id")
                            cname = item.get("name") or item.get("channel_name")
                            if cid and cname: 
                                channels.append((str(cname), str(cid)))
                if channels:
                    print(f"✅ Loaded {len(channels)} channels from local cache.")
                    return channels
            except Exception as e:
                print(f"Error reading {cache_file}: {e}")
                continue
                
    # Direct fallback if caches are completely missing
    if not channels:
        print("⚠️ Caches empty. Loading core sports channels...")
        channels = [("Sky Sports Main Event", "51"), ("TNT Sports 1", "52")]
    return channels

def main():
    raw_channels = fetch_channels()
    if not raw_channels:
        print("No channels found. Exiting.")
        return

    # Writing out the clean M3U playlist file directly to the source streams
    print("Writing playlist to file...")
    try:
        with open("dlhd.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for name, ch_id in raw_channels:
                for play_num in range(1, 7):
                    # Direct stream destinations without the DuckDNS proxy layer
                    stream_url = f"https://dlhd.sx/stream/stream-{ch_id}.php?p={play_num}"
                    
                    # Write out your formatting tags and the clean URL
                    f.write(f'#EXTINF:-1 tvg-id="ch-{ch_id}" tvg-name="{name}" group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{stream_url}\n\n")
        print(f"✅ dlhd.m3u created successfully with {len(raw_channels) * 6} direct stream lines!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
