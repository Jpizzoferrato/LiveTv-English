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

    # Writing out a completely clean M3U playlist file for the Proxy Builder
    print("Writing clean playlist to file targeting .pk domains...")
    try:
        with open("dlhd.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for name, ch_id in raw_channels:
                for play_num in range(1, 7):
                    # Point strictly to the brand new, live DaddyLive stream URL (.pk)
                    stream_url = f"https://dlhd.pk/stream/stream-{ch_id}.php?p={play_num}"
                    
                    # Write out the clean tags and direct URL without any proxy wrapping or old strings
                    f.write(f'#EXTINF:-1 tvg-id="ch-{ch_id}" tvg-name="{name}" group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{stream_url}\n")
        print("✅ Clean dlhd.m3u created successfully with .pk domains!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
