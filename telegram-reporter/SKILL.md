---
name: telegram-reporter
description: Send Telegram messages from any script or cron via curl. Use when you need to send a notification, alert, or report to a Telegram chat. Reads a bot token from a config file.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: false
allowed-tools:
  - Bash
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

## Send to one or more recipients

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
| socials | bot_token_socials | your configured chat(s) |
| security | bot_token_security | your configured chat(s) |
| rnd | bot_token_rnd | your configured chat(s) |
