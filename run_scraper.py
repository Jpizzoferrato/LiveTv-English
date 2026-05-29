import os
import requests

def fetch_channels():
    """Fetches raw channel data from the source."""
    print("Fetching raw channel list...")
    try:
        # If you need your real scraper logic here, make sure to add it.
        # This keeps the current layout safe so the file compiles.
        channels = [("Sky Sports Main Event", "51"), ("TNT Sports 1", "52")]
        return channels
    except Exception as e:
        print(f"Error fetching channels: {e}")
        return []

def main():
    raw_channels = fetch_channels()
    if not raw_channels:
        print("No channels found. Exiting.")
        return

    final_channels = []

    print("Generating proxy URLs...")
    for name, ch_id in raw_channels:
        for play_num in range(1, 7):
            # Target the exact /proxy/ endpoint the unified-iptv-proxy container is looking for
            daddylive_target = f"https://dlhd.sx/stream/stream-{ch_id}.php?p={play_num}"
            stream_url = f"http://pizzotv.duckdns.org:8080/proxy/manifest.m3u8?url={daddylive_target}"
            final_channels.append((f"{name} (P{play_num})", stream_url))

    # Writing out the formatted M3U playlist file
    print("Writing playlist to file...")
    try:
        with open("dlhd.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for name, ch_id in raw_channels:
                for play_num in range(1, 7):
                    # 1. Target the raw DaddyLive stream destination
                    daddylive_target = f"https://dlhd.sx/stream/stream-{ch_id}.php?p={play_num}"
                    
                    # 2. Wrap it perfectly inside your working proxy route
                    stream_url = f"http://pizzotv.duckdns.org:8080/proxy/manifest.m3u8?url={daddylive_target}"
                    
                    # 3. Write out the tags and the new proxy URL
                    f.write(f'#EXTINF:-1 tvg-id="ch-{ch_id}" tvg-name="{name}" group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{stream_url}\n")
        print("✅ dlhd.m3u created successfully!")
    except Exception as e:
        print(f"Error writing file: {e}")
