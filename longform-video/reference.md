# Long Form Video: reference for Claude

What Claude needs to write `script.json`, run the pipeline and change the template.
The user guide is [SKILL.md](SKILL.md).

---

## Project structure

Step 1 of SKILL.md builds this folder from `template/` and `scripts/`. The scripts work from
their own folder: they read `script.json`, `audio/` and `public/` next to themselves.

```
my-video/
├── package.json              # Remotion 4 and React, pinned; npm run render / npm run studio
├── tsconfig.json             # lets the bundler compile JSX without React imports
├── remotion.config.ts        # entry point ./src/index.ts
├── .gitignore                # keeps the voice clip, media and render out of git
├── script.json               # narration + per-scene specs (see the schema below)
├── batch_tts.py              # one-process VoxCPM2 generator (model loaded once)
├── fetch_broll.py            # Pexels b-roll downloader (reads PEXELS_API_KEY from env)
├── normalize_broll.sh        # re-encodes b-roll to 1920x1080, 30 fps, H.264 baseline, no B-frames
├── build_voice.py            # paces and pads each clip, builds the voice track and the timings
├── audio/
│   ├── _ref.wav              # voice reference (3-10 s, 48 kHz mono)
│   ├── <scene>.wav           # raw clip per scene
│   └── _proc_<scene>.wav     # paced and padded clip (build artifact)
├── public/
│   ├── voice.wav             # the assembled voice track, played by src/Main.tsx
│   ├── scene_timings.json    # AUDIO-DRIVEN scene durations, read by src/timeline.ts
│   ├── music.mp3             # optional background track ("music" in script.json)
│   └── broll/
│       ├── _raw/             # Pexels downloads as fetched (don't touch)
│       └── <scene>.mp4       # normalized 1920x1080 @ 30 fps clips
├── src/
│   ├── index.ts              # registerRoot(RemotionRoot)
│   ├── Root.tsx              # the "Main" composition: 1920x1080, 30 fps
│   ├── timeline.ts           # scene_timings.json -> each scene's length in frames
│   ├── Main.tsx              # scenes in a Series, fade-in, subtitles, voice, music
│   ├── parts.tsx             # Backdrop, Watermark, Subtitles, Enter, formatNumber
│   ├── brand.ts              # brand tokens (name, font, colors, number locale): EDIT THIS
│   └── scenes/               # one component per scene type
│       ├── TitleScene.tsx
│       ├── StatCounterScene.tsx
│       ├── KineticQuoteScene.tsx
│       ├── BarChartScene.tsx
│       ├── ComparisonScene.tsx
│       ├── ScenarioScene.tsx
│       ├── OutroScene.tsx
│       └── BrollScene.tsx    # full-bleed video with Ken Burns + chapter banner
└── out/
    └── video.mp4             # final render
```

---

## script.json schema

```json
{
  "title": "Main title, for your records",
  "subtitle": "Subtitle, for your records",
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
      "suffix": "%",
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

Field notes:
- `id`: unique, letters, digits and hyphens. It names the files: `audio/<id>.wav`, `public/broll/<id>.mp4`.
- `type`: one of the eight types above. A new type needs a component in `src/scenes/` and a line in `SCENES` in `src/Main.tsx`.
- `duration`: planning only (the word budget, and `fetch_broll.py` prefers clips at least this long).
  The real length of each scene comes from its voice clip.
- `narration`: what the voice says. Subtitles show it on every scene except `title`, `kinetic-quote` and `outro`.
- `voice_style`: a Voice Design prefix added to every clip by `batch_tts.py`. Keep it to 2-4 descriptors.
- `voice_speed`: recorded in `scene_timings.json` but does not change the audio; `build_voice.py` paces each clip.
- `music`: optional, top level, a file in `public/`, such as `"music": "music.mp3"`. Add it only
  when the file is there: a missing file stops the render.
- `suffix`: optional on `stat-counter` and `bar-chart`.
- Top-level `title` and `subtitle` are not shown; the `title` scene shows its own.

---

## Adapting the article

Pacing rule:
- **3-4 spoken words per second** of scene
- Keep each scene's narration within budget (e.g. a 6s scene ≈ 20-24 words max)
- Pick scene types: data-anim for numbers/comparisons, broll for narrative beats, kinetic-quote for impact lines

A 30-second test video is about 8 short scenes, one of each type.

---

## What each step does

### Voice reference
```bash
ffmpeg -i /path/to/narrator_sample.mp3 -ar 48000 -ac 1 -y audio/_ref.wav
```

### batch_tts.py
Loads the VoxCPM2 model once, generates all clips with cloning + the `voice_style` prefix,
cfg=2.5, 12 steps. RTF ~3x on Apple Silicon. It skips clips that already exist: delete
`audio/<id>.wav` to regenerate one. It runs in Local TTS's Python environment:
```bash
"${LOCAL_TTS_VENV:-$HOME/.local-tts/venv}/bin/python" batch_tts.py
```

### fetch_broll.py
Searches Pexels for each `broll` scene's `broll_query` and downloads via curl with a
User-Agent (Python urllib gets 403 on the Pexels CDN). It skips clips that already exist.

### normalize_broll.sh (CRITICAL)
Pexels clips come in a wild mix of fps (24, 25, 30, 60, 100) and resolutions (720p to 4K).
Remotion struggles with mismatched fps and H.264 B-frames. This script re-encodes everything
to 1920×1080 @ 30fps H.264 baseline, no B-frames, GOP 30, and keeps the originals in
`public/broll/_raw/`. **Do not skip this step.**

### build_voice.py
- Measures per-clip wpm
- Applies **mix A+B normalization**: clips in the 150-200 wpm band are untouched (natural
  variability kept), outliers are brought back to the nearest band edge via ffmpeg atempo
  (clamped 0.85-1.35x)
- Adds 0.3s lead silence + 0.5s trailing silence per clip
- Concatenates into `public/voice.wav`
- Writes `public/scene_timings.json`, which sets each scene's length (audio-first architecture)

### Render
```bash
npm run render    # remotion render Main out/video.mp4 --crf 18
```
~5 min for 2 min of 1080p on an M-series Mac. `npm run studio` opens a live preview.
The first render downloads a headless Chrome; after that, rendering works offline.

---

## Architecture principles (learned the hard way)

### Audio drives timing, not the reverse
`build_voice.py` paces and pads the clips → measures their actual durations → writes
`scene_timings.json` → `src/timeline.ts` turns it into each scene's `durationInFrames`. The
visual adapts to the audio, not the other way. This avoids per-clip speed-compensation that
creates uneven pacing. After changing a narration, regenerate its clip and run
`build_voice.py` again before rendering.

### Mix A+B voice pacing
VoxCPM2 produces wildly variable tempi (150-315 wpm on identical ref voice, depending on
content). Don't force uniform speed: it either butchers the slow clips or leaves the fast
ones untouched. Instead:
- Clips in the 150-200 wpm band: don't touch
- Outliers: normalize to the nearest band edge, capped at 0.85-1.35x atempo

A clip still above ~205 wpm after `build_voice.py` hit the cap: regenerate it.

### Short Voice Design prefixes only
Long prefixes (e.g. a 7-adjective style description) cause VoxCPM to generate 2-3x longer
audio than expected. Keep prefixes to 2-4 descriptors: `(enthusiastic, passionate)`.

### B-roll must be normalized before use
Pexels videos have B-frames, variable fps, and varied resolutions. Remotion produces
glitchy/stuttery playback on anything not conforming to the composition's fps + H.264
baseline. Always run `normalize_broll.sh` after `fetch_broll.py`. If a clip is shorter than
its scene, its last frame holds until the scene ends: give `broll` scenes a realistic
`duration` so `fetch_broll.py` picks a long enough clip.

### Transitions
The template uses a plain `Series` with a 10-frame fade-in on each scene, so every scene
starts exactly with its voice clip. A richer cut: fade everywhere (10 frames), slide spring
(16 frames) at semantic chapter changes, alternating direction (from-right/left/bottom) for
rhythm. If you add that with `@remotion/transitions` (`TransitionSeries`), each transition
overlaps two scenes and shortens the video by its length: add the transition's length to
the scene before it, or the pictures run ahead of the voice.

### Typography
Pick one display family and use weight contrast (400 body vs 800 titles vs 900 stats) and
aggressive negative letter-spacing (-1 to -14 depending on size) for punchy display text.
Set the family in `src/brand.ts`. Use a font installed on the machine, or font files in
`public/`: a web font service would break offline renders.

---

## Scene component API

Every scene component receives `{ scene }` props (its object from `script.json`) and reads
its fields. Inside a scene, `useCurrentFrame()` counts from the scene's start and
`useVideoConfig().durationInFrames` is the scene's own length. Main.tsx adds the fade-in,
the subtitles, the watermark, the voice and the music around every scene.

| type | fields | on screen |
|---|---|---|
| `title` | `title` (`\n` for line breaks), `subtitle` | large title, tagline |
| `stat-counter` | `value`, `suffix`, `label` (`\n`), `source` | number counting up, label, source |
| `broll` | `broll_query`, `subtitle` | full-bleed clip, slow zoom, chapter banner |
| `bar-chart` | `title`, `data` [{`label`, `value`}], `suffix` | horizontal bars growing in turn |
| `comparison` | `left`, `right` {`label`, `items`} | two cards side by side |
| `kinetic-quote` | `lines` | one line at a time, the last in the accent color |
| `scenario` | `title`, `before`, `after` {`label`, `value`, `detail`}, `punch` | before → after cards, punch line |
| `outro` | `title`, `subtitle`, `url` | closing card |

Helpers in `src/parts.tsx`: `<Enter delay distance>` (entry animation) and
`formatNumber(value, like)` (as many decimals as `like`, in `brand.locale`).

Common patterns:
- **Entry animations**: `spring({ frame, fps, config: { damping: 14, stiffness: 90 } })` + `interpolate(s, [0,1], [startY, 0])` for translateY-fade-in
- **Stat number ramp**: `interpolate(frame, [10, 10+rampFrames], [0,1])` cubic-eased, then post-ramp pulse via `Math.sin`
- **Stagger**: `frame - (i * spacing + offset)` offsets each element's animation start
- **Ken Burns**: `scale(1.02 + t * 0.04)` where `t = frame / durationInFrames`

Media: `Html5Audio` and `OffthreadVideo` from `remotion`, with files from `public/` through
`staticFile()`.

---

## Dependencies

- Node.js 18+, npm
- Remotion 4.x (pinned in `package.json`)
- Python venv with VoxCPM2 + soundfile (the Local TTS plugin's venv)
- ffmpeg, ffprobe
- Pexels API key (free; set `PEXELS_API_KEY` in the env)
- A short voice-reference clip of the user's own voice, or of someone who consents
- Optional: a music track the user has the right to use, at `public/music.mp3`

---

## Gotchas cheat sheet

| Symptom | Cause | Fix |
|---------|-------|-----|
| B-roll stutters | Source fps != 30, B-frames | `normalize_broll.sh` |
| Intro voice way faster than rest | Long Voice Design prefix bloated audio | Shorten to 2-4 descriptors |
| One scene feels super rapid | VoxCPM produced 250+ wpm raw | Regenerate, or let mix A+B clamp it |
| Uneven voice pacing | You tried to force uniform speed | Keep the mix A+B approach in build_voice.py |
| Fonts look generic | Using default weight 400 | Push to 800-900 with LS -1 to -14 for display |
| Scene too cluttered | Trying to animate everything | Data/stats = anim; narrative = broll |
| `Can't resolve '../public/scene_timings.json'` | `build_voice.py` has not run yet | Run steps 5 to 8 before rendering or opening the studio |
| `No voice timing for scene` | `script.json` changed after `build_voice.py` | Regenerate the clips, run `build_voice.py` again |
| `Could not play audio with src /public/...` | `music` names a file missing from `public/` | Copy the file there, or remove `music` |
| B-roll freezes at the end of a scene | Clip shorter than the scene | Raise the scene's `duration`, delete the clip, fetch again |

---

## Delivery checklist

- [ ] Brand tokens set in `src/brand.ts`
- [ ] B-roll normalized (fps probe = 30, no B-frames)
- [ ] Voice pacing uniform-feeling (no outlier > 205 wpm after build_voice.py)
- [ ] Music, if any, ducked under the voice (`volume` in `src/Main.tsx`)
- [ ] Brand name visible on every scene (corner watermark)
- [ ] Subtitles on non-text scenes (stat, chart, comparison, scenario, b-roll)
- [ ] Watched `out/video.mp4` once before sharing it
