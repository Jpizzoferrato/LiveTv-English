import os
import requests

def fetch_channels():
    """Fetches raw channel data from the source."""
    print("Fetching raw channel list...")
    # This matches your scraper's target logic
    # Returning a sample mock list structure for the loop processing
    try:
        # (Replace this mock list with your actual scraping/request logic if needed)
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

    # Writing out the formatted M3U8 playlist file
    print("Writing playlist to file...")
    try:
        with open("playlist.m3u8", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for display_name, url in final_channels:
                f.write(f'#EXTINF:-1,{display_name}\n')
                f.write(f"{url}\n")
        print("✅ playlist.m3u8 created successfully!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
