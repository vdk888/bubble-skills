---
name: publish-substack-note
description: Publish a short-form Substack Note (300-600 words) with an optional hero image, using the Claude-in-Chrome extension (Playwright gets 403 on Substack). Use when you have approved note content ready to post.
version: 1.0.0
author: Bubble Invest
license: MIT
disable-model-invocation: true
---

# Publish a Substack Note

You receive: note text (300-600 words) + optional hero image. You publish it as a Substack Note.

## Method — Claude-in-Chrome extension

Playwright gets a 403 on Substack. Use the Chrome-extension MCP tools (a logged-in browser session) instead.

### Step-by-step

```bash
# 1. If a hero image exists, load it to the macOS clipboard
osascript -e 'set the clipboard to (read (POSIX file "/path/to/hero.jpg") as JPEG picture)'
```

Then use the Chrome-extension MCP tools:

```
# 2. Get tab context
tabs_context_mcp(createIfEmpty=true) -> tabId

# 3. Navigate
navigate(url="https://substack.com/home", tabId=tabId)

# 4. Click the composer ("What's on your mind?" / your locale's equivalent)
click(<composer prompt>)

# 5. Click inside the composer area
click(coordinate=[530, 400])

# 6. IMAGE FIRST (if any) — paste from clipboard
key("cmd+v") -> wait 5 seconds

# 7. TEXT SECOND — type (do NOT paste/fill)
type(text="note content here")

# 8. Click the orange "post" button (bottom-right of the composer)
#    Take a screenshot first to locate its exact position
click(coordinate=[772, 672])
```

## Critical rules

- **Image FIRST, text SECOND.** Pasting text first can clobber the pending image.
- Use the `type` action, never paste text (pasting can disturb the image).
- The "post" button position varies — take a screenshot to locate it before clicking.
- Playwright does NOT work for Substack (403) — always use the Chrome extension.

## Note format guidelines

- 300-600 words max
- One idea, one angle, one conclusion
- Match your own publication's voice and language

## Pre-publish QA checklist

- [ ] Spelling and accents correct for your language
- [ ] Title ↔ content coherent
- [ ] Copy consistent if the Note also exists in another format (e.g. a social teaser, a newsletter)
- [ ] Sources cited for any numeric claim
- [ ] Image FIRST, text SECOND respected
