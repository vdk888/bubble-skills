---
name: generate-image
description: Generate images locally using FLUX.2 Klein 4B via mflux on Apple Silicon. Use when asked to create, generate, or make an image, illustration, photo, thumbnail, cover art, banner, or visual. Free, no API calls. Outputs PNG.
user-invocable: true
allowed-tools:
  - Bash
  - Read
---

# Local Image Generation (FLUX.2 Klein 4B)

Generate images locally via mflux on Apple Silicon. FLUX.2 Klein 4B, 4-bit quantized, optimized for M4 16GB. Apache-2.0, zero cost, zero cloud.

## When to use

- User asks to "generate an image", "create a picture", "make a visual", "design a thumbnail"
- Need a cover image for a blog post, article, or social media
- Need an illustration, banner, photo-style image, or any visual asset
- User describes a scene and wants it rendered
- Any image generation task

## Quick start

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/generate.sh \
  --prompt "your detailed prompt here" \
  --out /tmp/my_image.png
```

The script prints `OK <path>` on success. The PNG is ready to attach to Telegram, embed in articles, etc.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | (required) | Text description of the image to generate |
| `--out` | `/tmp/flux2_<timestamp>.png` | Output file path |
| `--width` | 512 | Image width in pixels |
| `--height` | 512 | Image height in pixels |
| `--steps` | 4 | Inference steps (more = better quality, slower) |
| `--seed` | (random) | Seed for reproducibility |
| `--quantize` | 4 | Quantization level (3,4,5,6,8). Lower = less RAM, slightly less quality |

## Supported resolutions

These fit comfortably in 16GB RAM at 4-bit quantization:

| Size | Use case | ~Time |
|------|----------|-------|
| 512x512 | Thumbnails, social media, quick visuals | ~24s |
| 768x768 | Medium quality, blog headers | ~45s |
| 512x768 / 768x512 | Portrait / landscape variants | ~35s |

1024x1024 is possible but tight on 16GB — may need `--quantize 3`. Expect ~90s+.

## Writing good prompts

FLUX.2 Klein responds well to detailed, descriptive prompts. Tips:

1. **Be specific**: "A golden retriever wearing sunglasses on a Paris cafe terrace, warm afternoon light, photorealistic" > "dog photo"
2. **Include style**: Add style keywords like "photorealistic", "watercolor", "digital illustration", "minimalist", "cinematic lighting"
3. **Describe composition**: "close-up", "wide angle", "bird's eye view", "centered", "rule of thirds"
4. **Set mood**: "warm tones", "moody", "bright and cheerful", "dramatic shadows"
5. **For text in images**: FLUX.2 has decent text rendering. Include the exact text in quotes.

### Prompt examples by use case

**Blog thumbnail:**
```
"A clean minimalist illustration of financial charts rising upward, blue and gold color scheme, modern flat design, white background"
```

**Article cover (investing):**
```
"A dramatic close-up of a bull statue on Wall Street, golden hour lighting, shallow depth of field, photorealistic"
```

**Social media visual:**
```
"An elegant infographic-style layout showing a portfolio pie chart, dark blue background, gold accents, modern typography, clean design"
```

**Portrait / headshot style:**
```
"Professional headshot of a confident businesswoman, studio lighting, neutral background, photorealistic, sharp focus"
```

## Common patterns

### Generate and attach to Telegram

```bash
OUT=/tmp/image_$(date +%s).png
bash ${CLAUDE_SKILL_DIR}/scripts/generate.sh \
  --prompt "your prompt" \
  --out "$OUT"
# Then use mcp__plugin_telegram_telegram__reply with files=["$OUT"]
```

### Generate multiple variations (different seeds)

```bash
for SEED in 1 2 3; do
  bash ${CLAUDE_SKILL_DIR}/scripts/generate.sh \
    --prompt "your prompt" \
    --seed $SEED \
    --out "/tmp/variation_${SEED}.png"
done
```

### Blog cover image workflow

1. Generate the image at the right aspect ratio
2. Read it to verify quality
3. Save to the article's asset directory or attach to the content pipeline

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/generate.sh \
  --prompt "your detailed blog cover prompt" \
  --width 768 --height 512 \
  --out ~/claude-workspaces/Miranda_Socials/assets/cover.png
```

## Performance (Apple M4 16GB)

- **First run**: ~18 min (downloads ~8GB model weights to `~/.cache/huggingface/`)
- **Subsequent runs**: ~24s for 512x512 (model cached on disk, loads into RAM each run)
- **Peak memory**: ~10.4 GB at 4-bit quantization
- **Model**: FLUX.2 Klein 4B via mflux (native MLX, Apple Silicon optimized)

## Requirements

- `mflux` installed via `uv tool install mflux --python 3.12` (binary at `~/.local/bin/mflux-generate-flux2`)
- `~/.cache/huggingface/` with model weights (auto-downloaded on first run)
- ~8 GB disk for model weights

If mflux is not installed:
```bash
uv tool install mflux --python 3.12
```

## Troubleshooting

- **"command not found: mflux-generate-flux2"** — mflux not installed or not on PATH. Run `uv tool install mflux --python 3.12`.
- **Out of memory at 1024x1024** — Try `--quantize 3` or reduce to 768x768.
- **Slow first run** — Normal. Model weights (~8GB) download once to `~/.cache/huggingface/`.
- **Blurry or low quality** — Increase `--steps` to 8 or use a more detailed prompt.
- **Wrong colors/style** — Be more explicit about colors, lighting, and style in the prompt.

## References

- mflux: https://github.com/filipstrand/mflux
- FLUX.2 Klein: https://huggingface.co/black-forest-labs/FLUX.2-klein-4B
- License: Apache-2.0 (commercial use allowed)
