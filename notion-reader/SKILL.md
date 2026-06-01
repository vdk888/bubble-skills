---
name: notion-reader
description: Query Notion logbook and writing guidelines. Shared utility for all content and audit crons.
user-invocable: false
---

# Notion Reader — Shared Utility

Provides standard Notion queries used across multiple crons and skills.

## Logbook Query

Query the Agent Logbook (DB: `${NOTION_LOGBOOK_DB}`):

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -s -X POST "https://api.notion.com/v1/databases/${NOTION_LOGBOOK_DB}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d "$QUERY_JSON"
```

### Common query patterns

**Last N entries per agent:**
```json
{"page_size": 3, "sorts": [{"property": "Date", "direction": "descending"}], "filter": {"property": "Agent", "select": {"equals": "AGENT_NAME"}}}
```

**All entries from last 7 days:**
```json
{"page_size": 50, "sorts": [{"property": "Date", "direction": "descending"}], "filter": {"property": "Date", "date": {"on_or_after": "DATE_7_DAYS_AGO"}}}
```

**Parse response:**
```python
import json, sys
data = json.load(sys.stdin)
for p in data.get('results', []):
    props = p.get('properties', {})
    title = ''.join(t.get('plain_text', '') for t in props.get('Résumé', {}).get('title', []))
    agent = props.get('Agent', {}).get('select', {}).get('name', '?')
    date = props.get('Date', {}).get('date', {}).get('start', '?')
    tags = ', '.join(s.get('name', '') for s in props.get('Tags', {}).get('multi_select', []))
    print(f'[{agent}] {date} — {title} ({tags})')
```

## Writing Guidelines

Fetch from Notion page `${NOTION_GUIDELINES_PAGE}`:

```bash
curl -s "https://api.notion.com/v1/blocks/${NOTION_GUIDELINES_PAGE}/children" \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H "Notion-Version: 2022-06-28" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for b in data.get('results', []):
    bt = b.get('type', '')
    c = b.get(bt, {})
    if 'rich_text' in c:
        txt = ''.join(t.get('plain_text', '') for t in c['rich_text'])
        if txt: print(txt)
"
```

## Write to Logbook

Create a new entry:

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "${NOTION_LOGBOOK_DB}"},
    "properties": {
      "Résumé": {"title": [{"text": {"content": "TITLE_HERE"}}]},
      "Agent": {"select": {"name": "AGENT_NAME"}},
      "Date": {"date": {"start": "YYYY-MM-DD"}},
      "Tags": {"multi_select": [{"name": "TAG1"}, {"name": "TAG2"}]}
    }
  }'
```
