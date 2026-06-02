#!/usr/bin/env bash
# voice-transcribe skill — local offline speech-to-text.
# Usage: transcribe.sh <audio.oga|ogg|wav|mp3|flac> [lang]
#   lang: fr | en | auto (default auto)
# Self-contained Opus decoder (bundled node_modules) + a whisper.cpp engine
# installed by setup.sh into the skill's engine/ dir (or override with VT_ENGINE).
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IN="${1:?usage: transcribe.sh <audio> [lang]}"
LANG="${2:-auto}"

# Locate the whisper.cpp engine (binary + model + shared libs). First match wins.
# Override the search by exporting VT_ENGINE=/path/to/whisper.cpp.
ENGINE_CANDIDATES=(
  "${VT_ENGINE:-}"
  "$SKILL_DIR/engine/whisper.cpp"
  "$HOME/.voice-transcribe/whisper.cpp"
)
ENGINE=""
for c in "${ENGINE_CANDIDATES[@]}"; do
  [ -n "$c" ] && [ -x "$c/build/bin/whisper-cli" ] && ENGINE="$c" && break
done
[ -n "$ENGINE" ] || {
  echo "voice-transcribe: whisper engine not found. Run: bash $SKILL_DIR/setup.sh" >&2
  exit 1
}

BIN="$ENGINE/build/bin/whisper-cli"
MODEL="$ENGINE/models/ggml-small.bin"
export LD_LIBRARY_PATH="$ENGINE/build/src:$ENGINE/build/ggml/src:${LD_LIBRARY_PATH:-}"

WAV="$(mktemp "${TMPDIR:-/tmp}/vt-XXXXXX.wav")"
trap 'rm -f "$WAV"' EXIT

case "$IN" in
  *.wav) cp "$IN" "$WAV" ;;
  *)     node "$SKILL_DIR/bin/oga2wav.mjs" "$IN" "$WAV" >&2 ;;
esac

"$BIN" -m "$MODEL" -l "$LANG" -np -nt "$WAV" 2>/dev/null
