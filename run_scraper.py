import requests, urllib3, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = 'https://dlhd.pk/24-7-channels.php'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Accept': 'text/html', 'Referer': 'https://dlhd.pk/'}
final_channels = []
try:
    res = requests.get(url, headers=headers, timeout=20, verify=False)
    if res.status_code == 200:
        matches = re.findall(r'href=["\'][^"\']*?watch\.php\?id=(\d+)[^"\']*?["\']\s+data-title=["\']([^"\']+)["\']', res.text)
        if not matches:
            matches = re.findall(r'data-title=["\']([^"\']+)["\']\s+href=["\'][^"\']*?watch\.php\?id=(\d+)', res.text)
            if matches: matches = [(item[1], item[0]) for item in matches]
        for ch_id, name in matches:
            ch_id, clean_name = str(ch_id).strip(), str(name).strip().upper()
            if not ch_id or not clean_name or ch_id == '00': continue
            name_lower = clean_name.lower()
            if 'adult swim' in name_lower: pass
            elif any(w in name_lower for w in ['xxx','porn','adult','18+','playboy','hustler','pink','brazzers']): continue
            if any(w in name_lower for w in ['news','msnbc','cnn','cbsn']) and not any(w in name_lower for w in ['fox','israel','i24']): continue
            if not any(w in name_lower for w in ['israel','i24','ch 12 il','ch 13 il','ch 11 il']) and 'sky sports' not in name_lower:
                if any(' ' + r in name_lower or '(' + r in name_lower or name_lower.endswith(r) or name_lower.startswith(r) for r in ['uk','united kingdom','itv','bbc','bt sport','premier sports','tnt sports','italy','italia','spain','espana','germany','deutschland',' de','(de)','france','fr ','portugal','arabic','netherlands','greece','cyprus','albania','romania','poland','polska','turkey','turkiye','indonesia','indosiar','india','pakistan','latino','mexico','argentina','austria','slovakia','slovenia','sweden','chile','colombia','peru','ecuador','venezuela','uruguay','paraguay','tabii','eleven sports','dazn','bein sports','supersport','canale','rai','rtve']): continue
            for p in range(1, 7):
                stream_url = f'/dlhd/stream-{ch_id}.php?p={p}'
                final_channels.append((f'{clean_name} (P{p})', stream_url))
        with open('dlhd.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n\n')
            idx = 1
            for name, url in final_channels:
                group = 'DLHD Live Sports' if ('live event:' in name.lower() or 'vs' in name.lower()) else 'DLHD United States & General'
                f.write(f'#EXTINF:-1 tvg-id="ch-{idx}" tvg-name="{name}" group-title="{group}" http-referrer="https://dlhd.pk/",{name}\n#EXTVLCOPT:http-referrer=https://dlhd.pk/\n{url}\n\n')
                idx += 1
        print(f'Build complete. Generated {idx - 1} channels.')
except Exception as e: print(f'Error: {e}')
