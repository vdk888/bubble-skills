---
name: telegram-reporter
description: Send Telegram messages via curl. Send Telegram messages via curl from any script or cron. Reads a bot token from a config file.
user-invocable: false
---

# Telegram Reporter — Shared Utility

Standard Telegram delivery for cron jobs. DO NOT use MCP telegram tools in crons — use curl.

## Send to one channel

```bash
BOT_TOKEN=$(cat ~/.config/telegram/bot_token_$CHANNEL)
CHAT_ID="$TARGET_CHAT_ID"
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"${CHAT_ID}\", \"text\": $(echo "$MESSAGE" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'), \"parse_mode\": \"Markdown\"}"
```

## Send to Joris + Jade

```bash
BOT_TOKEN=$(cat ~/.config/telegram/bot_token_$CHANNEL)
for CHAT_ID in "YOUR_CHAT_ID"; do
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"${CHAT_ID}\", \"text\": $(echo "$MESSAGE" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'), \"parse_mode\": \"Markdown\"}"
done
```

## Channel → Token mapping

| Agent | Token file | Chat targets |
|-------|-----------|--------------|
| Content | bot_token_socials | Joris + Jade |
| Security | bot_token_security | Joris only |
| Lab | bot_token_rnd | Joris only |

## Heartbeat

```bash
  -H 'Content-Type: application/json' \
  -d "{\"task\":\"$TASK_NAME\",\"severity\":\"heartbeat\",\"message\":\"Completed at $(date +%H:%M). $OUTCOME\"}"
```

## Error Report

```bash
  -H 'Content-Type: application/json' \
  -d "{\"task\":\"$TASK_NAME\",\"severity\":\"error\",\"message\":\"$ERROR_DESCRIPTION\"}"
```
