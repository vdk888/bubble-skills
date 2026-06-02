---
name: suno-extract
version: 1.0.0
author: Bubble Invest
license: MIT
description: Extract MP3 audio from Suno URLs. Use when asked to download a Suno song, extract audio from suno.com, or convert a Suno link to MP3. Works with both full URLs (suno.com/song/UUID) and short URLs (suno.com/s/xxx).
allowed-tools:
  - Bash
---

# Suno Audio Extractor

Download MP3 files from Suno song URLs. No API key needed — uses the public studio API.

## How it works

Two-step process:
1. Call `studio-api-prod.suno.com/api/clip/{UUID}` (public, no auth) to get song metadata + CDN audio URL
2. Download the MP3 from the CDN URL

## Extract a song

### From a full URL (suno.com/song/UUID)

```bash
# Extract UUID from URL
UUID=$(echo "SUNO_URL_HERE" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# Get metadata
curl -s "https://studio-api-prod.suno.com/api/clip/$UUID" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'Title: {d.get(\"title\")}')
print(f'Artist: {d.get(\"display_name\")}')
print(f'Duration: {d.get(\"metadata\",{}).get(\"duration\",0):.0f}s')
print(f'Audio: {d.get(\"audio_url\")}')
print(f'Video: {d.get(\"video_url\")}')
"

# Download MP3
AUDIO_URL=$(curl -s "https://studio-api-prod.suno.com/api/clip/$UUID" | python3 -c "import json,sys; print(json.load(sys.stdin).get('audio_url',''))")
curl -sL -H "Referer: https://suno.com/" -o /tmp/suno_download.mp3 "$AUDIO_URL"
```

### From a short URL (suno.com/s/xxx)

```bash
# Resolve short URL to UUID
UUID=$(curl -sI "https://suno.com/s/SHORT_CODE_HERE" | grep -i location | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# Then same as above
AUDIO_URL=$(curl -s "https://studio-api-prod.suno.com/api/clip/$UUID" | python3 -c "import json,sys; print(json.load(sys.stdin).get('audio_url',''))")
curl -sL -H "Referer: https://suno.com/" -o /tmp/suno_download.mp3 "$AUDIO_URL"
```

## One-liner (full pipeline)

```bash
# Replace URL with any Suno link
SUNO_URL="https://suno.com/song/UUID_OR_SHORT"
UUID=$(curl -sLI "$SUNO_URL" 2>/dev/null | grep -ioE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
[ -z "$UUID" ] && UUID=$(echo "$SUNO_URL" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
META=$(curl -s "https://studio-api-prod.suno.com/api/clip/$UUID")
TITLE=$(echo "$META" | python3 -c "import json,sys; print(json.load(sys.stdin).get('title','unknown'))" 2>/dev/null)
AUDIO=$(echo "$META" | python3 -c "import json,sys; print(json.load(sys.stdin).get('audio_url',''))" 2>/dev/null)
OUT="/tmp/${TITLE// /_}.mp3"
curl -sL -H "Referer: https://suno.com/" -o "$OUT" "$AUDIO"
echo "Downloaded: $OUT ($(ls -lh "$OUT" | awk '{print $5}'))"
```

## API reference

### Clip metadata (public, no auth)
```
GET https://studio-api-prod.suno.com/api/clip/{UUID}
```

Returns JSON with:
- `title` — song title
- `display_name` — artist name
- `audio_url` — CDN URL for MP3 (e.g. `https://cdn1.suno.ai/UUID.mp3`)
- `video_url` — CDN URL for MP4
- `image_url` / `image_large_url` — cover art
- `metadata.duration` — duration in seconds
- `metadata.tags` — genre/style tags
- `metadata.prompt` — lyrics/prompt used to generate
- `is_public` — whether the song is public

## Video download

Same pattern — use `video_url` instead of `audio_url`:
```bash
VIDEO=$(echo "$META" | python3 -c "import json,sys; print(json.load(sys.stdin).get('video_url',''))")
curl -sL -H "Referer: https://suno.com/" -o /tmp/suno_video.mp4 "$VIDEO"
```
