#!/bin/bash
# generate.sh — Wrapper for FLUX.2 Klein 4B image generation via mflux
# Usage: generate.sh --prompt "..." [--out /path/to/output.png] [--width 512] [--height 512] [--steps 4] [--seed 42]
#
# Defaults optimized for M4 16GB: 512x512, 4-bit quantized, low-ram mode, 4 steps.
# Supports 1024x1024 but slower and tighter on memory.

set -euo pipefail

# Defaults
PROMPT=""
OUT=""
WIDTH=512
HEIGHT=512
STEPS=4
SEED=""
QUANTIZE=4

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --prompt) PROMPT="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --width) WIDTH="$2"; shift 2;;
    --height) HEIGHT="$2"; shift 2;;
    --steps) STEPS="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    --quantize) QUANTIZE="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "ERROR: --prompt is required" >&2
  exit 1
fi

# Default output path
if [[ -z "$OUT" ]]; then
  OUT="/tmp/flux2_$(date +%s).png"
fi

# Ensure output dir exists
mkdir -p "$(dirname "$OUT")"

# Build command
CMD=(mflux-generate-flux2
  --base-model flux2-klein-4b
  --quantize "$QUANTIZE"
  --low-ram
  --prompt "$PROMPT"
  --width "$WIDTH"
  --height "$HEIGHT"
  --steps "$STEPS"
  --output "$OUT"
)

if [[ -n "$SEED" ]]; then
  CMD+=(--seed "$SEED")
fi

echo "Generating image..."
echo "  Prompt: $PROMPT"
echo "  Size: ${WIDTH}x${HEIGHT}"
echo "  Steps: $STEPS"
echo "  Quantize: ${QUANTIZE}-bit"
echo "  Output: $OUT"
echo ""

"${CMD[@]}" 2>&1

echo ""
echo "OK $OUT"
