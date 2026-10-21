---
name: longform-video
description: Turn an article into a 1-5 minute, 1920x1080 narrated video, rendered on your machine with Remotion, in a voice cloned locally with Local TTS, with Pexels b-roll, animated stats and charts, and burned-in subtitles. Use when asked to turn an article into a narrated explainer video.
version: 1.1.0
author: Bubble Invest
license: MIT
---

# Long Form Video

## What it makes
A 1 to 5 minute, 1920x1080 narrated video from an article, rendered on your machine.
A voice cloned locally with Local TTS narrates b-roll, animated stats and charts, with subtitles.

## Before you start
- An Apple Silicon Mac, or Linux with an NVIDIA (CUDA) card.
- About 11 GB free: 10 GB for Local TTS's model, 1 GB for the project and the render.
- Node.js 18 or later, and ffmpeg (on a Mac: `brew install node ffmpeg`).
- The Local TTS plugin, installed and set up once: `/plugin install local-tts@bubble-skills`, then ask Claude to say one sentence with it (this downloads its model).
- A free Pexels key (pexels.com/api), set before you start Claude Code: `export PEXELS_API_KEY=your-key`
- A 3 to 10 second clip of your own voice, or of someone who consents.
- Optional: a music track you have the right to use.
- Remotion, which renders the video, is free for individuals, non-profits and companies of up to 3 employees; larger companies need its company license (remotion.dev/license).

**Clone only your own voice, or that of someone who consents.**

## Make a video
Ask Claude "Make a video from this article", or run the steps yourself.
`${CLAUDE_SKILL_DIR}` is this skill's folder; Claude fills it in. Steps 2 to 9 run in the project folder.

1. Create the project and copy the four scripts into it:
   `mkdir my-video && cd my-video && cp -R "${CLAUDE_SKILL_DIR}/template/." . && cp "${CLAUDE_SKILL_DIR}"/scripts/* . && mkdir -p audio public/broll`
2. Install Remotion: `npm install`
3. Write `script.json` from the article: Claude does it, following [reference.md](reference.md).
4. Prepare your voice clip: `ffmpeg -i my-voice.m4a -ar 48000 -ac 1 -y audio/_ref.wav`
5. Generate the voice: `"${LOCAL_TTS_VENV:-$HOME/.local-tts/venv}/bin/python" batch_tts.py`
6. Download the b-roll: `python3 fetch_broll.py`
7. Normalize the b-roll (never skip it): `bash normalize_broll.sh`
8. Build the voice track and the timings: `python3 build_voice.py`
9. Render: `npm run render`. The first render downloads a headless Chrome (about 100 MB). Your video is `out/video.mp4`.

For music, copy your track to `public/music.mp3` and add `"music": "music.mp3"` to `script.json` before step 9.

## If something goes wrong
- **B-roll stutters or jumps:** run step 7 again; never render raw Pexels clips.
- **The intro voice runs much faster than the rest:** shorten `voice_style` to 2 to 4 words, such as `(warm, calm)`, delete the scene clips in `audio/` (keep `_ref.wav`), then redo steps 5 and 8.
- **One scene sounds rushed:** delete its clip, `audio/<scene id>.wav`, then redo steps 5 and 8.
- **The text looks generic:** set your font, colors and name in `src/brand.ts`.
- **A scene feels cluttered:** keep numbers for stat and chart scenes, tell the story in b-roll scenes, and cut words (about 3 per second of scene).

## For Claude
- Before step 4, ask the user to confirm that the clip is their own voice or that of someone who consents. Without that yes, stop.
- Read [reference.md](reference.md) before you write `script.json` or change the template: the schema, the project structure, the architecture principles and the scene component API.
- Run each step inside the project folder: the scripts read `script.json`, `audio/` and `public/` next to themselves.
- If step 5 says `No such file` or `No module named 'soundfile'` (or `'voxcpm'`), Local TTS is not set up yet: run its setup first.
