import os
import requests
import re

def fetch_backup_channels():
    """Extracts the full 3900+ channel list from your existing backup file."""
    print("🔄 Accessing local backup file to recover 3900+ channels...")
    backup_file = "dlhd_with_logos.m3u"
    
    # Fallback if the logo file isn't found
    if not os.path.exists(backup_file):
        backup_file = "dlhd_with_country_categories.m3u"
        
    channels = []
    if os.path.exists(backup_file):
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            current_name = None
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    # Extract the channel name from the end of the comma
                    if "," in line:
                        name_part = line.split(",")[-1].strip()
                        # Strip off any trailing (P1), (P2) indicators so the duplicate engine handles it cleanly
                        current_name = re.sub(r'\s*\(P\d+\)$', '', name_part)
                elif line.startswith("http") and current_name:
                    # Extract just the channel ID number from the URL
                    match = re.search(r'stream-(\d+)\.php', line)
                    if match:
                        ch_id = match.group(1)
                        # Avoid adding duplicates during the extraction phase
                        if (current_name, ch_id) not in channels:
                            channels.append((current_name, ch_id))
            print(f"📋 Successfully extracted {len(channels)} unique channels from backup!")
            return channels
        except Exception as e:
            print(f"Error reading backup file: {e}")
            return []
    else:
        print("❌ No backup playlist files found in the repository.")
        return []

def main():
    raw_channels = fetch_backup_channels()
    
    if not raw_channels:
        print("⚠️ No channels recovered. Restoring core sports channels to prevent empty file...")
        raw_channels = [
            ("Sky Sports Main Event", "51"), ("TNT Sports 1", "52"),
            ("Sky Sports Premier League", "53"), ("TNT Sports 2", "54"),
            ("Sky Sports Football", "55"), ("TNT Sports 3", "56")
        ]

    # ==========================================
    # DUPLICATE ENGINE (PREVENTS REMOVAL)
    # ==========================================
    name_counts = {}
    for name, _ in raw_channels:
        name_counts[name] = name_counts.get(name, 0) + 1

    final_channels = []
    name_counter = {}
    for name, ch_id in raw_channels:
        if name_counts[name] > 1:
            if name not in name_counter:
                name_counter[name] = 1
            else:
                name_counter[name] += 1
            new_name = f"{name} ({name_counter[name]})"
            final_channels.append((new_name, ch_id))
        else:
            final_channels.append((name, ch_id))

    # ==========================================
    # GENERATE THE COMBINED M3U FILE WITH .PK
    # ==========================================
    output_file = "dlhd.m3u"
    print(f"Writing clean playlist targeting .pk domains to {output_file}...")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for name, ch_id in final_channels:
                for play_num in range(1, 7):
                    stream_url = f"https://dlhd.pk/stream/stream-{ch_id}.php?p={play_num}"
                    f.write(f'#EXTINF:-1 group-title="DLHD Live", {name} (P{play_num})\n')
                    f.write(f"{stream_url}\n\n")
        print(f"✅ Clean dlhd.m3u successfully rebuilt with {len(final_channels) * 6} total stream lines!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
