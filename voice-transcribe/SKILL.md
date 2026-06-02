---
name: voice-transcribe
description: Transcribe a voice note or audio file to text locally (offline, no API/key) — Ogg/Opus (Telegram voice), WAV, MP3, FLAC. Use when a message arrives with a voice attachment, or whenever you need speech-to-text for an audio file. Outputs the transcript text; supports French/English/auto language detection.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: true
allowed-tools:
  - Bash
  - Read
---

# Voice transcription (local, offline)

Transcribes audio to text on-device using [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
(`small` multilingual model) plus a pure-WASM Opus decoder. No network, no API key, works
headless. Good for French and English.

## Setup (one time)

```bash
bash ${CLAUDE_SKILL_DIR}/setup.sh
```

This installs the Node Opus decoder and builds whisper.cpp + downloads the `small` model
(~466 MB) into the skill's `engine/` folder. Idempotent — safe to re-run. Requires `git`,
`cmake`, a C compiler, and `node` (18+).

## When to use

- A message arrives with a voice attachment (`audio/ogg`, Telegram `.oga`).
- You have any audio file (`.oga`, `.ogg`, `.wav`, `.mp3`, `.flac`) and need its text.

## How to use

```bash
${CLAUDE_SKILL_DIR}/bin/transcribe.sh <audio-path> [lang]
```

- `lang` is optional: `fr`, `en`, or `auto` (default). Force `fr`/`en` for best accuracy.
- The transcript is printed to stdout.

Example:

```bash
${CLAUDE_SKILL_DIR}/bin/transcribe.sh ~/Downloads/voice-note.oga fr
```

## Notes

- First word of output may have a leading space — trim if needed.
- A ~15 s clip transcribes in a few seconds on CPU.
- To point at an existing whisper.cpp build instead of the bundled one, export
  `VT_ENGINE=/path/to/whisper.cpp` (must contain `build/bin/whisper-cli` + `models/ggml-small.bin`).
- For higher accuracy at the cost of speed/size, swap the model in `setup.sh` (e.g. `medium`).
