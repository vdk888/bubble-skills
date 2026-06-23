---
name: longform-video
description: Produce 1-5 min landscape (1920x1080) video essays from an article, using a fully local Remotion project — React scene components, local TTS voice cloning, Pexels b-roll, kinetic typography, burned-in subtitles, chapter transitions, ambient music. Use when asked to turn an article into a narrated explainer video.
version: 1.0.0
author: Bubble Invest
license: MIT
---

# SKILL.md — Long-Form Video (Remotion + Local TTS)

Produces 1-5 min landscape (1920×1080) video essays from an article using a
**fully local, self-contained Remotion project** with React scene components,
local TTS (VoxCPM2) voice cloning, Pexels b-roll, kinetic typography, burned-in
subtitles, chapter transitions, and ambient background music.

This skill creates **one standalone Remotion project per video** for maximum
flexibility, scene-component composition, and zero external API dependencies for
voice (TTS runs locally — see the companion `local-tts` skill).

Adapt the visual tokens (colors, fonts, logo) in `src/brand.ts` to your own
brand before rendering.

---

## When to use

- Turn a long-form article into a narrated landscape (1920×1080) video essay
- A video with data viz + b-roll + kinetic typography
- Clone a narrator's voice for the voiceover (local, offline)
- A Kurzgesagt / video-essay-style explainer

Do NOT use for vertical short-form (9:16) — this is a landscape template.

---

## Project structure

```
<project>/
├── package.json              # Remotion 4.x + transitions + google-fonts
├── tsconfig.json             # include src + public/scene_timings.json + script.json
├── remotion.config.ts        # entry point ./src/index.ts
├── script.json               # narration + per-scene specs (see Schema below)
├── batch_tts.py              # single-process VoxCPM generator (model loaded once)
├── build_voice.py            # ffmpeg timeline assembly with mix A+B wpm normalization
├── fetch_broll.py            # Pexels b-roll downloader (reads PEXELS_API_KEY from env)
├── normalize_broll.sh        # Re-encodes b-roll to H.264 baseline, no B-frames, 30fps
├── audio/
│   ├── _ref.wav              # Voice reference (ffmpeg'd from a short narrator clip)
│   ├── <scene>.wav           # Per-scene raw TTS output
│   └── _proc_<scene>.wav     # Speed-adjusted + padded clips (build artifact)
├── public/
│   ├── voice.wav             # Final assembled voice timeline (Remotion via staticFile)
│   ├── music.mp3             # Background ambient track
│   ├── scene_timings.json    # AUDIO-DRIVEN timing data, consumed by Root.tsx
│   └── broll/
│       ├── _raw/             # Pristine Pexels downloads (don't touch)
│       └── <scene>.mp4       # Normalized 1920×1080 @ 30fps H.264 baseline
├── src/
│   ├── index.ts              # registerRoot(RemotionRoot)
│   ├── Root.tsx              # Composition registration — imports scene_timings.json
│   ├── Main.tsx              # TransitionSeries orchestration: scenes + audio + music
│   ├── Backdrop.tsx          # Background wash + dot grid
│   ├── Logo.tsx              # Your logo SVG
│   ├── LogoBadge.tsx         # Corner watermark
│   ├── SubtitleLayer.tsx     # Burned-in pill captions, chunked & kinetic
│   ├── brand.ts              # Brand tokens (colors, fonts) — EDIT THIS
│   └── scenes/
│       ├── TitleScene.tsx
│       ├── StatCounterScene.tsx
│       ├── KineticQuoteScene.tsx
│       ├── BarChartScene.tsx
│       ├── ComparisonScene.tsx
│       ├── ScenarioScene.tsx
│       ├── OutroScene.tsx
│       └── BrollScene.tsx    # Full-bleed video with Ken Burns + chapter banner
└── out/
    └── video.mp4             # Final render
```

---

## script.json schema

```json
{
  "title": "Main title shown on intro",
  "subtitle": "Intro subtitle",
  "voice_style": "(enthusiastic, passionate)",
  "voice_speed": 1.0,
  "scenes": [
    { "id": "intro", "type": "title", "duration": 6,
      "title": "Multi-line\ntitle",
      "subtitle": "Tagline shown beneath",
      "narration": "Voiced over this scene." },

    { "id": "stat-94", "type": "stat-counter", "duration": 7,
      "value": 94, "suffix": "%",
      "label": "Multi-line\nlabel",
      "source": "Source, 2026",
      "narration": "..." },

    { "id": "wrong-movie", "type": "broll", "duration": 11,
      "broll_query": "factory robotic arm",
      "subtitle": "Chapter banner text",
      "narration": "..." },

    { "id": "chart", "type": "bar-chart", "duration": 14,
      "title": "Chart title",
      "data": [{ "label": "Row", "value": 74.5 }],
      "narration": "..." },

    { "id": "comparison", "type": "comparison", "duration": 12,
      "left":  { "label": "Exposed",  "items": ["Master's", "+47% salary"] },
      "right": { "label": "Protected", "items": ["Cooks", "Mechanics"] },
      "narration": "..." },

    { "id": "quote", "type": "kinetic-quote", "duration": 9,
      "lines": ["Line 1,", "line 2,", "final punch line."],
      "narration": "..." },

    { "id": "scenario", "type": "scenario", "duration": 14,
      "title": "Scenario title",
      "before": { "label": "Today", "value": "10 consultants", "detail": "..." },
      "after":  { "label": "2 years", "value": "3 consultants",  "detail": "..." },
      "punch": "Italic punch line",
      "narration": "..." },

    { "id": "outro", "type": "outro", "duration": 9,
      "title": "Your brand",
      "subtitle": "Your tagline",
      "url": "yoursite.example",
      "narration": "..." }
  ]
}
```

---

## Workflow

### 1. Adapt your article into script.json
Pacing rule:
- **3-4 spoken words per second** of scene at voice_speed 1.0
- Keep each scene's narration within budget (e.g. a 6s scene ≈ 20-24 words max)
- Pick scene types: data-anim for numbers/comparisons, broll for narrative beats, kinetic-quote for impact lines

### 2. Prepare the voice reference
```bash
ffmpeg -i /path/to/narrator_sample.mp3 -ar 48000 -ac 1 -y audio/_ref.wav
```

### 3. Batch-generate voice clips
```bash
~/.venvs/voxcpm/bin/python batch_tts.py
```
Loads the VoxCPM2 model once, generates all clips with cloning + the `voice_style` prefix, cfg=2.5, 12 steps. RTF ~3x on Apple Silicon.

### 4. Fetch b-roll from Pexels
```bash
export PEXELS_API_KEY="..."   # free key: https://www.pexels.com/api/
python3 fetch_broll.py
```
Downloads via curl with a User-Agent (Python urllib gets 403 on the Pexels CDN).

### 5. Normalize b-roll (CRITICAL)
```bash
./normalize_broll.sh
```
Pexels clips come in a wild mix of fps (24, 25, 30, 60, 100) and resolutions (720p to 4K). Remotion's Video component struggles with mismatched fps and H.264 B-frames. This script re-encodes everything to 1920×1080 @ 30fps H.264 baseline, no B-frames, GOP 30 — eliminates stutter. **Do not skip this step.**

### 6. Build the voice timeline
```bash
python3 build_voice.py
```
- Measures per-clip wpm
- Applies **mix A+B normalization**: clips in the 150-200 wpm band are untouched (natural variability kept), outliers are brought back to the nearest band edge via ffmpeg atempo (clamped 0.85-1.35x)
- Adds 0.3s lead silence + 0.5s trailing silence per clip
- Concatenates into `public/voice.wav`
- Writes `public/scene_timings.json` — this drives Remotion's per-scene durationInFrames (audio-first architecture)

### 7. Render
```bash
npx remotion render Main out/video.mp4 --codec h264 --pixel-format yuv420p --crf 18 --concurrency 4
```
~5 min for 2 min of 1080p at concurrency=4 on an M-series Mac.

---

## Architecture principles (learned the hard way)

### Audio drives timing, not the reverse
`build_voice.py` generates clips → measures actual durations → writes `scene_timings.json` → `Root.tsx` imports this to set each scene's `durationInFrames`. The visual adapts to the audio, not the other way. This avoids per-clip speed-compensation that creates uneven pacing.

### Mix A+B voice pacing
VoxCPM2 produces wildly variable tempi (150-315 wpm on identical ref voice, depending on content). Don't force uniform speed — it either butchers the slow clips or leaves the fast ones untouched. Instead:
- Clips in the 150-200 wpm band: don't touch
- Outliers: normalize to the nearest band edge, capped at 0.85-1.35x atempo

### Short Voice Design prefixes only
Long prefixes (e.g. a 7-adjective style description) cause VoxCPM to generate 2-3x longer audio than expected. Keep prefixes to 2-4 descriptors: `(enthusiastic, passionate)`.

### B-roll must be normalized before use
Pexels videos have B-frames, variable fps, and varied resolutions. Remotion's Video tag produces glitchy/stuttery playback on anything not conforming to the composition's fps + H.264 baseline. Always run `normalize_broll.sh` after `fetch_broll.py`.

### Chapter vs fade transitions
Fade everywhere (10 frames) for smoothness, slide spring (16 frames) at semantic chapter changes. Scene IDs in `CHAPTER_BOUNDARIES` set in both `Root.tsx` and `Main.tsx` trigger slide — alternate direction (from-right/left/bottom) for rhythm.

### Typography
Pick one display family and use weight contrast (400 body vs 800 titles vs 900 stats) and aggressive negative letter-spacing (-1 to -14 depending on size) for punchy display text. Define these tokens in `src/brand.ts`.

---

## Scene component API

Every scene component receives `{ scene: any }` props and reads fields from script.json. Common patterns:

- **Entry animations**: `spring({ frame, fps, config: { damping: 14, stiffness: 90 } })` + `interpolate(s, [0,1], [startY, 0])` for translateY-fade-in
- **Stat number ramp**: `interpolate(frame, [10, 10+rampFrames], [0,1])` cubic-eased, then post-ramp pulse via `Math.sin`
- **Stagger**: `frame - (i * spacing + offset)` offsets each element's animation start
- **Ken Burns**: `scale(1.02 + t * 0.04)` where `t = frame / durationInFrames`

---

## Dependencies

- Node.js 18+, npm
- Remotion 4.x suite (cli, transitions, google-fonts, media-utils, animation-utils)
- Python venv with VoxCPM2 + soundfile (see the `local-tts` skill)
- ffmpeg, ffprobe
- Pexels API key (free; set `PEXELS_API_KEY` in the env)
- A short voice-reference clip for cloning
- A background ambient music track at `public/music.mp3`

---

## Gotchas cheat sheet

| Symptom | Cause | Fix |
|---------|-------|-----|
| B-roll stutters | Source fps != 30, B-frames | `normalize_broll.sh` |
| Intro voice way faster than rest | Long Voice Design prefix bloated audio | Shorten to 2-4 descriptors |
| One scene feels super rapid | VoxCPM produced 250+ wpm raw | Regenerate, or let mix A+B clamp it |
| Uneven voice pacing | You tried to force uniform speed | Switch to mix A+B approach in build_voice.py |
| Fonts look generic | Using default weight 400 | Push to 800-900 with LS -1 to -14 for display |
| Scene too cluttered | Trying to animate everything | Data/stats = anim; narrative = broll |

---

## Delivery checklist

- [ ] Brand tokens set in `src/brand.ts`
- [ ] B-roll normalized (fps probe = 30, no B-frames)
- [ ] Voice pacing uniform-feeling (no outlier > 205 wpm after build_voice.py)
- [ ] Music ducked appropriately
- [ ] Logo visible on every scene (corner watermark or prominent on key scenes)
- [ ] Subtitles on non-text scenes (stat, comparison, scenario)
- [ ] Transitions: fade default, slide at chapter changes
