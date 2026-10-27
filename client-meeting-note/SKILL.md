---
name: client-meeting-note
description: Turn a voice note or transcript of a client meeting into a structured draft note (objectives, situation, next steps) for the adviser to review. Runs on the adviser's own machine, writes a local Markdown file, never sends anything. Use when an adviser has just met a client and wants a first-draft meeting note. Not investment advice.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: true
allowed-tools:
  - Bash(python3 *check_note.py*)
  - Bash(*voice-transcribe/bin/transcribe.sh*)
  - Read
  - Write
---

# client-meeting-note — from a meeting to a draft note

> **Draft only. Not investment advice.** The skill prepares, you validate. It recommends no product, no allocation, no action for the client, and it does not make a note compliant with any rule. The adviser stays responsible for the content and for what is filed.

## What it does

Takes the transcript (or the voice note, transcribed locally) of a client meeting and writes ONE local Markdown file with a fixed structure: objectives, situation, next steps, plus open questions for the adviser. The adviser reads, corrects and validates it.

## Privacy rules (non-negotiable)

- Everything stays on this machine. Do not upload audio, transcript or note anywhere. No web search, no web fetch, no messaging, no email, no calendar, no CRM write.
- Never send the note. No automatic send of any kind. Output is a file the adviser opens.
- Transcribe locally only (see `voice-transcribe`, offline whisper.cpp). Do not use a cloud speech service.
- Write the note next to the transcript, or in a folder the adviser names. Do not commit it to git, do not copy it elsewhere.
- Do not keep client data in memory files or logs.

## Steps

1. **Input.** If given audio, run `${CLAUDE_SKILL_DIR}/../voice-transcribe/bin/transcribe.sh <audio> [fr|en]` (needs the voice-transcribe skill installed; if it is not, ask the adviser for a text transcript, never use a cloud service). If given text, read it. Ask the adviser for the language of the note if unclear (default: the language of the meeting).
2. **Draft** using `${CLAUDE_SKILL_DIR}/template.md`. Rules:
   - Record only what was said in the meeting. Quote or paraphrase; do not infer or fill gaps. If something is unclear or missing, put it in **Open questions**, never invent it.
   - Figures, dates and names exactly as spoken. If a figure is uncertain (transcription), mark it `[to confirm]`.
   - Next steps: who, what, when if stated. Only actions that were agreed or requested in the meeting.
   - Neutral reporting. Do not add recommendations, suitability judgements, return forecasts, "should" advice or any statement that the note meets a regulatory requirement. If the adviser gave advice in the meeting, report it as "the adviser said ...", attributed.
   - Keep the `DRAFT` banner and the review checklist.
3. **Check.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/check_note.py <note.md>`. It verifies the structure and flags forbidden phrasing. Exit 0 = pass, 1 = fix and rerun. It is a mechanical aid, not a review (it does not flag unfilled placeholders).
4. **Hand over.** Tell the adviser where the file is and that it is a draft to validate. Stop. Do not send, share or file it.

## Files

- `template.md` — the note skeleton.
- `bin/check_note.py` — structure and wording check (Python 3 standard library, no network).
- `examples/` — a fictional transcript and the note produced from it.
- `tests/run.sh` — test suite.

## Limits

Transcription errors, names and figures need the adviser's eye. The skill does not identify speakers reliably, does not decide what is relevant for the file, and gives no assurance about regulatory compliance.
