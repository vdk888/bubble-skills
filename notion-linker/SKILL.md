---
name: notion-linker
description: Automatically link content (Substack articles, LinkedIn posts) to Notion projects
---

# Notion Linker

Automated tool to update Notion project pages when new content is created.

## Usage

### Link Substack Article
```bash
python3 skills/notion-linker/notion_linker.py \
  --type substack \
  --title "Article Title" \
  --url "https://substack.com/..." \
  --status Published
```

### Link LinkedIn Post
```bash
python3 skills/notion-linker/notion_linker.py \
  --type linkedin \
  --title "FR/EN - Post Title" \
  --status Scheduled
```

## Status Options
- `Draft` — Content being written
- `Scheduled` — Approved, waiting for publication
- `Published` — Live on platform

## Projects Linked

| Content Type | Notion Project | Project ID |
|--------------|----------------|------------|
| Substack articles | Substack - Newsletter | <YOUR_NOTION_DB_ID> |
| LinkedIn posts | LinkedIn Sage Agent | <YOUR_NOTION_DB_ID> |

## Integration with Agents

### For Substack Agent
After publishing an article, run:
```python
import sys
sys.path.insert(0, "skills/notion-linker")
from notion_linker import link_substack_article

link_substack_article(
    title="Article Title",
    url="https://substack.com/...",
    status="Published"
)
```

### For Content (LinkedIn) Agent
After scheduling a post, run:
```python
import sys
sys.path.insert(0, "skills/notion-linker")
from notion_linker import link_linkedin_post

link_linkedin_post(
    title="FR/EN - Post Title",
    status="Scheduled"
)
```
