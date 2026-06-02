#!/usr/bin/env bash
# Setup for the voice-transcribe skill — installs the Opus decoder, builds whisper.cpp,
# and downloads the `small` model into the skill's engine/ dir.
# Idempotent: safe to run multiple times.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$SKILL_DIR/engine/whisper.cpp"
MODEL="ggml-small.bin"

echo "[voice-transcribe] Setup starting..."

# 1. Node Opus decoder (for .oga/.ogg → wav).
if command -v npm &>/dev/null; then
  echo "[voice-transcribe] Installing Node dependencies..."
  ( cd "$SKILL_DIR" && npm install --omit=dev --silent )
else
  echo "WARNING: npm not found — .oga/.ogg decoding needs it. WAV input still works." >&2
fi

# 2. Build whisper.cpp engine if missing.
if [ -x "$ENGINE_DIR/build/bin/whisper-cli" ]; then
  echo "[voice-transcribe] whisper.cpp already built."
else
  for tool in git cmake cc; do
    command -v "$tool" &>/dev/null || { echo "ERROR: '$tool' required to build whisper.cpp." >&2; exit 1; }
  done
  echo "[voice-transcribe] Cloning + building whisper.cpp..."
  mkdir -p "$SKILL_DIR/engine"
  [ -d "$ENGINE_DIR/.git" ] || git clone --depth 1 https://github.com/ggml-org/whisper.cpp "$ENGINE_DIR"
  cmake -B "$ENGINE_DIR/build" -S "$ENGINE_DIR" -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build "$ENGINE_DIR/build" --config Release -j --target whisper-cli >/dev/null
fi

# 3. Download the small model if missing.
if [ -f "$ENGINE_DIR/models/$MODEL" ]; then
  echo "[voice-transcribe] Model already present."
else
  echo "[voice-transcribe] Downloading $MODEL (~466 MB)..."
  if [ -x "$ENGINE_DIR/models/download-ggml-model.sh" ]; then
    ( cd "$ENGINE_DIR" && bash ./models/download-ggml-model.sh small )
  else
    mkdir -p "$ENGINE_DIR/models"
    curl -fL -o "$ENGINE_DIR/models/$MODEL" \
      "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$MODEL"
  fi
fi

echo "[voice-transcribe] Setup complete."
echo "[voice-transcribe] Try: $SKILL_DIR/bin/transcribe.sh <audio-file> [fr|en|auto]"
