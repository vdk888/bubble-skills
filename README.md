# Bubble Skills

Free, open-source [Claude Code](https://claude.com/claude-code) skills by [Bubble Invest](https://bubbleinvest.org) — small, sharp utilities for agentic workflows.

These are building blocks we use to run an AI-native investment firm. We open-source the generic ones because the best way to show what's possible with agents is to let you run them yourself.

## Install

```
/plugin marketplace add vdk888/bubble-skills
/plugin install <skill-name>
```

## Skills

| Skill | What it does |
|-------|--------------|
| **suno-extract** | Extract the MP3 from any Suno song URL. No key needed. |
| **telegram-reporter** | Send Telegram messages from any script or cron via curl. |
| **scheduled-task-creation** | Guide for creating and debugging Claude Desktop scheduled tasks. |
| **notion-linker** | Auto-link published content back to project rows in a Notion database. |
| **generate-image** | Generate images locally with FLUX.2 Klein (Apple Silicon). Free, offline, no API. |
| **notion-reader** | Query a Notion database or page from any script. |
| **voice-transcribe** | Transcribe voice notes / audio to text locally & offline (whisper.cpp, no API key). |
| **longform-video** | Turn an article into a 1-5 min narrated landscape video essay: Remotion + local TTS voice cloning + Pexels b-roll + kinetic typography. |
| **deepseek-brain** | Run Claude Code on DeepSeek instead of Anthropic, keeping the full harness. The reasoning-effort proxy, model routing, channels fix, and rollback. |
| **fund-source-verification** | Source-tier + independent-verification rubric before you act on any third-party claim. Tier gating, corroboration math, paywall discipline. |
| **fund-thesis-format** | A 7-part investment-thesis structure (claim → mechanism → fit → invalidation → sizing → asymmetry → conviction levers) that renders as a file, a memo, or a chat message. |
| **cron-preflight** | Pre-flight scaffolding for scheduled tasks: catch-up SKEW math, policy-hash gate, source verifier. |
| **cron-postflight** | Post-flight scaffolding: audit-log row, git commit + push with lane discipline, notification send. |
| **publish-substack-note** | Publish a short-form Substack Note (image-first) via the Claude-in-Chrome extension. |
| **publish-substack-post** | Publish or schedule a long-form Substack Post (inline images, hero, subscribe button) via Playwright — the selectors + timing that actually work. |
| **local-tts** | Local text-to-speech (30 languages, voice cloning). → [vdk888/local-tts](https://github.com/vdk888/local-tts) |
| **boycott-filter** | Brand-boycott enforcer + Chrome extension. → [vdk888/boycott-filter](https://github.com/vdk888/boycott-filter) |

These are building blocks we actually run to operate the firm — we're not professional developers, we built them for ourselves and open-source the generic ones. Found a bug or a sharper way to do it? Open an issue or a PR — help us improve them.

`local-tts` and `boycott-filter` ship from their own repos (linked above) and are included in this marketplace for one-stop install.

## License

MIT — see [LICENSE](LICENSE). Use them, fork them, build on them.

---

Made by [Bubble Invest](https://bubbleinvest.org) · Navigating the AI transition, one agent at a time.
