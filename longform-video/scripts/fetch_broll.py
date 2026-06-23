#!/usr/bin/env python3
"""Fetch b-roll videos from Pexels for each broll scene.

Requires a Pexels API key (free): https://www.pexels.com/api/
Set it in the environment before running:  export PEXELS_API_KEY="..."
"""
import json, os, sys, urllib.request, urllib.parse, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
if not PEXELS_KEY:
    sys.exit("ERROR: set PEXELS_API_KEY in the environment (get one free at https://www.pexels.com/api/)")
script = json.loads((ROOT / 'script.json').read_text())
broll_dir = ROOT / 'public' / 'broll'
broll_dir.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Macintosh) longform-video/1.0"

def search_pexels(q, per_page=15):
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page={per_page}&orientation=landscape&size=medium"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def pick_hd(vid):
    # prefer 1920x1080 hd mp4; else largest
    files = vid.get('video_files', [])
    hd = [f for f in files if f.get('width') == 1920 and f.get('height') == 1080 and f.get('file_type','').endswith('mp4')]
    if hd:
        return hd[0]['link']
    files.sort(key=lambda f: (f.get('width',0)*f.get('height',0)), reverse=True)
    return files[0]['link'] if files else None

for s in script['scenes']:
    if s['type'] != 'broll':
        continue
    out = broll_dir / f"{s['id']}.mp4"
    if out.exists() and out.stat().st_size > 100_000:
        print(f"SKIP {s['id']}")
        continue
    q = s['broll_query']
    print(f"=== {s['id']}: {q}")
    try:
        data = search_pexels(q)
    except Exception as e:
        print(f"  ERR search: {e}"); continue
    vids = data.get('videos', [])
    # filter: duration >= scene duration (give us room) and landscape
    candidates = [v for v in vids if v.get('duration', 0) >= s['duration'] and v.get('width', 0) >= v.get('height', 0)]
    if not candidates:
        candidates = vids
    if not candidates:
        print(f"  NO RESULTS"); continue
    pick = candidates[0]
    link = pick_hd(pick)
    if not link:
        print(f"  NO HD"); continue
    print(f"  picked id={pick['id']} {pick.get('duration')}s  url={link[:60]}...")
    # Download
    tmp = str(out) + ".tmp"
    try:
        r = subprocess.run(['curl','-sSL','-A',UA,'-o',tmp,link], capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) < 100_000:
            print(f"  curl failed: rc={r.returncode} stderr={r.stderr[:200]}")
            continue
        os.rename(tmp, out)
        print(f"  -> {out} ({out.stat().st_size//1024} KB)")
    except Exception as e:
        print(f"  DOWNLOAD ERR: {e}")
print("DONE")
