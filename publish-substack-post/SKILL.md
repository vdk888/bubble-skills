---
name: publish-substack-post
description: Publish a long-form Substack Post (1500-2500 words) with inline images, hero image, and a subscribe button, via a logged-in Playwright browser profile. Supports scheduling. Use when you have an approved essay ready to publish.
version: 1.0.0
author: Bubble Invest
license: MIT
disable-model-invocation: true
---

# Publish a Substack Post

You receive: article text (markdown or structured blocks) + title + subtitle. You insert content, add images, and publish or schedule.

This skill automates the long-form Substack editor with Playwright driving a
**logged-in browser profile** (a persistent Chromium profile already signed into
your Substack account). The selectors and timing below are the load-bearing part.

## Pre-requisites

- A persistent Playwright/Chromium profile already logged into Substack
- Python venv with Playwright installed
- Your publication's publish URL: `https://<your-publication>.substack.com/publish/post`
- Image-generation tooling of your choice (any model that outputs PNG/JPEG)

## Copy guidelines

Match your own publication's voice, language, and house style. Verify spelling/accents and that every numeric claim is sourced. Verify the final word count against the original draft.

## Step 1 — Assemble article content

Parse your source into a list of `(type, html_content)` tuples. Preserve bold (`<strong>`), italic (`<em>`), headings (`h2`), dividers (`<hr>`), paragraphs (`<p>`). Save as JSON for the publish script.

**Verify word count** against the original.

## Step 2 — Plan image placement

Identify 3 image insertion points between major sections. Images go BETWEEN content chunks, not at the end. Split content into 4 chunks:

- Chunk A: Intro + Section 1
- **→ Image 1**
- Chunk B: Section 2 + Section 3
- **→ Image 2**
- Chunk C: Section 4 + Section 5
- **→ Image 3**
- Chunk D: Remaining sections + conclusion + CTA

## Step 3 — Generate images (4 total)

Generate with whatever image model you use, applying a consistent style prefix so all images share a look:

1. **Hero** (cover/thumbnail): landscape 16:9, relates to the article thesis
2. **Inline 1**: square 1:1, relates to the first section
3. **Inline 2**: square 1:1, relates to the middle section
4. **Inline 3**: square 1:1, relates to a later section

**Tip:** some image models output PNG regardless of the requested extension. Convert to a real JPEG before upload:

```python
from PIL import Image
img = Image.open(tmp_png_path).convert('RGB')
img.save(output_path, 'JPEG', quality=92)
```

## Step 4 — Create the post and insert content

### 4a. Navigate and fill title/subtitle

```python
await page.goto('https://<your-publication>.substack.com/publish/post', timeout=30000)
await asyncio.sleep(5)

# Title
await page.click('[placeholder*="Title"]')
await page.keyboard.type(TITLE, delay=15)
await asyncio.sleep(0.5)

# Subtitle
await page.keyboard.press('Tab')
await asyncio.sleep(0.3)
await page.keyboard.type(SUBTITLE, delay=10)
await asyncio.sleep(0.5)

# Move to body editor
await page.keyboard.press('Tab')
await asyncio.sleep(1)
```

### 4b. Insert content with images (THE CRITICAL PART)

**NEVER use `keyboard.type()` for article body. It drops characters on long text.**

Use `insertHTML` in chunks. The cursor stays at the end after each insertion, so images inserted between chunks land at the correct position.

```python
async def insert_html(page, html):
    return await page.evaluate("""(html) => {
        const e = document.querySelector('.ProseMirror');
        e.focus();
        const s = window.getSelection();
        s.selectAllChildren(e);
        s.collapseToEnd();
        document.execCommand('insertHTML', false, html);
        return e.innerText.length;
    }""", html)

async def insert_image(page, path):
    img_btn = page.locator('[aria-label*="image"], [aria-label*="Image"]')
    if await img_btn.count() > 0:
        await img_btn.first.click()
        await asyncio.sleep(1)
        menu = page.locator('[role="menuitem"]:has-text("Image")')
        if await menu.count() > 0:
            await menu.first.click()
            await asyncio.sleep(1)
        fi = page.locator('input[type="file"]')
        if await fi.count() > 0:
            await fi.last.set_input_files(path)  # .last — Substack has multiple file inputs
            await asyncio.sleep(4)
            return True
    return False
```

**Insertion sequence:**
```python
for ctype, content in CHUNKS:
    if ctype == 'html':
        length = await insert_html(page, content)
    elif ctype == 'image':
        await insert_image(page, content)
```

### 4c. Verify word count

```python
wc = len((await page.evaluate("document.querySelector('.ProseMirror').innerText")).split())
print(f"Word count: {wc} (target: XXXX)")
# Must match the original. If not, stop and investigate.
```

### 4d. Take screenshots to verify layout

```python
await page.evaluate("window.scrollTo(0, 0)")
await page.screenshot(path='/tmp/sub_top.png')
await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
await page.screenshot(path='/tmp/sub_mid.png')
await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
await page.screenshot(path='/tmp/sub_bot.png')
```

## Step 5 — Add a subscribe button

**MUST be done BEFORE clicking Continue/Publish.** Otherwise Substack shows a popup that disrupts the scheduling flow.

```python
await page.evaluate("""() => {
    const e = document.querySelector('.ProseMirror');
    e.focus();
    const s = window.getSelection();
    s.selectAllChildren(e);
    s.collapseToEnd();
}""")
await page.keyboard.press('Enter')

# Toolbar > Button dropdown > Subscribe
await page.locator('button:has-text("Button")').first.click()
await asyncio.sleep(1)
# nth(1) because the first "Subscribe" match is the toolbar button itself
subs = page.locator('button:has-text("Subscribe")')
if await subs.count() > 1:
    await subs.nth(1).click()
await asyncio.sleep(2)
```

## Step 6 — Upload the hero image

```python
# Use data-testid — there are 2 "Settings" buttons; this targets the right one
await page.locator('[data-testid="settings-button"]').click()
await asyncio.sleep(2)

fi = page.locator('input[type="file"]')
if await fi.count() > 0:
    await fi.first.set_input_files(HERO_PATH)
    await asyncio.sleep(5)

await page.locator('button:has-text("Done")').first.click()
await asyncio.sleep(2)
```

**⚠️ Do NOT use `button:has-text("Settings")` — it resolves to 2 elements (strict-mode violation).**

## Step 7 — Schedule (or publish immediately)

```python
# Open publish dialog
await page.locator('button:has-text("Continue")').first.click()
await asyncio.sleep(3)

# Set audience to Everyone (click the LABEL, not the hidden radio input)
await page.locator('label:has-text("Everyone")').first.click()
await asyncio.sleep(1)

# Enable scheduling (click the LABEL, not the aria-hidden checkbox)
sched = page.locator('label:has-text("Schedule time to email and publish")')
await sched.scroll_into_view_if_needed()  # often below the viewport
await sched.click()
await asyncio.sleep(2)

# Set datetime via JS (native .fill() doesn't work on this input)
await page.evaluate("""(dt_value) => {
    const dt = document.querySelector('input[type="datetime-local"]');
    const setter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
    ).set;
    setter.call(dt, dt_value);
    dt.dispatchEvent(new Event('input', { bubbles: true }));
    dt.dispatchEvent(new Event('change', { bubbles: true }));
}""", '2026-04-16T10:00')  # Format: YYYY-MM-DDTHH:MM
await asyncio.sleep(1)

# Click send (button text is dynamic: "Send to everyone in X hours/days")
send = page.locator('button:has-text("Send to everyone")')
await send.last.click()
await asyncio.sleep(5)

# Handle the subscribe-button popup IF it still appears (shouldn't if Step 5 worked)
for sel in ['button:has-text("Publish without buttons")', 'button:has-text("Add subscribe buttons")']:
    b = page.locator(sel)
    if await b.count() > 0:
        await b.first.click()
        await asyncio.sleep(3)
        break
```

**For immediate publish (no scheduling):** skip the schedule-label click and datetime, just click "Send to everyone now".

## Step 8 — Verify

Screenshot the confirmation page. It should say **"Your post is scheduled!"** (or "Your post is live!").

## Step 9 — Delete a scheduled post (if needed)

The `...` menu buttons are SVG elements, not `<button>`. Find by position:

```python
results = await page.evaluate("""() => {
    const all = document.querySelectorAll('button, svg');
    return [...all].filter(el => {
        const r = el.getBoundingClientRect();
        return r.x > 550 && r.width < 40 && r.width > 10 && !el.textContent.trim();
    }).map(el => ({
        tag: el.tagName,
        x: el.getBoundingClientRect().x + el.getBoundingClientRect().width/2,
        y: el.getBoundingClientRect().y + el.getBoundingClientRect().height/2
    }));
}""")
# Click the SVG at the y-position of the target post row
await page.mouse.click(target_x, target_y)
# Then: [role="menuitem"]:has-text("Delete") → confirm button
```

## Known issues

- **Excessive spacing between paragraphs:** `insertHTML` with `<p>` tags sometimes adds extra margin in the Substack ProseMirror editor. Monitor visually. Potential fix: test `<br>` between paragraphs instead of separate `<p>` blocks.
- **Audience radio visual state:** The "Everyone" label click may not visually update the radio in the Settings panel, but the publish-button text ("Send to everyone") confirms the correct audience is selected.
- **Image-model timeouts:** Hero-image generation can time out. Retry once on failure.
