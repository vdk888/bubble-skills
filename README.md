# Bubble Skills — The Bubble Shop

Free, open-source [Claude Code](https://claude.com/claude-code) skills and plugins by [Bubble Invest](https://bubbleinvest.org).

We're not developers — we built and use these tools to run our own family office. They're free, MIT. We'd love the community's help to improve them.

## One-command install

```
/plugin marketplace add vdk888/bubble-skills
/plugin install <skill-name>
```

That's it. Every skill and plugin below becomes available in your Claude Code agent.

## What's in the shop

### Media

| Skill | What it does |
|-------|--------------|
| **generate-image** | Generate images locally with FLUX.2 Klein (Apple Silicon). Free, offline, no API. |
| **local-tts** | Local text-to-speech: 30 languages, voice cloning, VoxCPM2. Free, offline. → [vdk888/local-tts](https://github.com/vdk888/local-tts) |
| **voice-transcribe** | Transcribe voice notes / audio to text locally & offline (whisper.cpp, no API key). |
| **suno-extract** | Extract the MP3 from any Suno song URL. No key needed. |
| **longform-video** | Turn an article into a 1–5 min narrated landscape video essay: Remotion + local TTS voice cloning + Pexels b-roll + kinetic typography. |

### Automation & Cron

| Skill | What it does |
|-------|--------------|
| **telegram-reporter** | Send Telegram messages from any script or cron via curl. |
| **scheduled-task-creation** | Guide for creating and debugging Claude Desktop scheduled tasks. |
| **cron-postflight** | Post-flight scaffolding: audit-log row, git commit + push with lane discipline, notification send. |
| **deepseek-brain** | Run Claude Code on DeepSeek instead of Anthropic, keeping the full harness. |

### Productivity

| Skill | What it does |
|-------|--------------|
| **notion-linker** | Auto-link published content back to project rows in a Notion database. |
| **notion-reader** | Query a Notion database or page from any script. |
| **boycott-filter** | Brand-boycott enforcer + Chrome extension. → [vdk888/boycott-filter](https://github.com/vdk888/boycott-filter) |

### Content

| Skill | What it does |
|-------|--------------|
| **publish-substack-note** | Publish a short-form Substack Note (image-first) via the Claude-in-Chrome extension. |
| **publish-substack-post** | Publish or schedule a long-form Substack Post (inline images, hero, subscribe button) via Playwright — the selectors + timing that actually work. |

### Sales

| Skill | What it does |
|-------|--------------|
| **prospect-research** | Build or refresh a Research Capsule for any prospect: background, workflow pain, recent signals, and three outreach angles (V1/V2/V3). Writes a local Markdown file. Read-only — never sends or posts. |

### Research & Investing

| Skill | What it does |
|-------|--------------|
| **fund-source-verification** | Source-tier + independent-verification rubric before you act on any third-party claim. Tier gating, corroboration math, paywall discipline. |
| **fund-thesis-format** | A 7-part investment-thesis structure (claim → mechanism → fit → invalidation → sizing → asymmetry → conviction levers) that renders as a file, a memo, or a chat message. |

### Security & Privacy

| Skill | What it does |
|-------|--------------|
| **bubble-shield** | PreToolUse guard that blocks reads of protected client folders until data is anonymised. 100% local, fail-closed (GDPR art. 25 & 32). → [vdk888/bubble-shield-public](https://github.com/vdk888/bubble-shield-public) |

## Coming soon (fast-follow)

A couple more are still in active development; we'll add them shortly:

- **bubble-artist** — AI-native design agent for generative brand assets and visual content pipelines.
- **ben-example-agent** — a fully-wired example dept-manager agent. (Already shipping inside `bubble-ops-loop/agents/ben` — clone the framework to use it today.)

## More Bubble marketplaces

The following repos ship their own standalone marketplaces — add them independently if you want just those plugins:

- `Bubble-invest/bubble-shield` — the internal (private) Bubble Shield marketplace (same plugin as above, internal versioning)

## License

MIT — see [LICENSE](LICENSE). Use them, fork them, build on them.

---

Made by [Bubble Invest](https://bubbleinvest.org) · Navigating the AI transition, one agent at a time.

We're not professional developers. We built these tools to run our own firm, and we open-source the generic ones because the best way to show what's possible with agents is to let you run them yourself. Found a bug or a sharper way to do it? Open an issue or a PR — we'd love the help.
