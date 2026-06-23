#!/bin/bash
# Normalize all Pexels b-roll to 1920x1080 @ 30 fps
# Uses H.264 baseline profile with no B-frames + short GOP for precise Remotion seeking (avoids glitchy playback)
set -e
cd "$(dirname "$0")"
mkdir -p public/broll/_raw
for f in public/broll/*.mp4; do
  name=$(basename "$f")
  if [[ "$name" == _* ]]; then continue; fi
  raw="public/broll/_raw/$name"
  if [ ! -f "$raw" ]; then
    mv "$f" "$raw"
  fi
  echo "=== $name"
  ffmpeg -y -i "$raw" \
    -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30" \
    -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
    -profile:v baseline -level 4.0 \
    -bf 0 -refs 1 -g 30 -keyint_min 30 -sc_threshold 0 \
    -x264opts no-scenecut \
    -movflags +faststart \
    -an \
    "public/broll/$name" 2>&1 | tail -2
done
echo "DONE"
