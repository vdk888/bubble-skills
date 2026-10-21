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

## Setup (one time)

1. Create a bot with Telegram's [@BotFather](https://t.me/BotFather) (`/newbot`) and copy its token.
2. Send any message to your bot, then read your chat ID from
   `https://api.telegram.org/bot<TOKEN>/getUpdates` (`"chat":{"id":...}`).
3. Save the token in a file named after a channel of your choice (here `alerts`), readable only by you:

```bash
mkdir -p ~/.config/telegram
printf '%s' 'YOUR_BOT_TOKEN' > ~/.config/telegram/bot_token_alerts
chmod 600 ~/.config/telegram/bot_token_alerts
```

The commands below expect `CHANNEL` (e.g. `alerts`), `TARGET_CHAT_ID` and `MESSAGE` to be set.
Check the config before sending:

```bash
[ -s ~/.config/telegram/bot_token_$CHANNEL ] || echo "Missing ~/.config/telegram/bot_token_$CHANNEL (see Setup)"
```

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

One token file per channel; the names are yours to choose. Example with three channels:

| Channel | Token file | Chat targets |
|-------|-----------|--------------|
| socials | bot_token_socials | your configured chat(s) |
| security | bot_token_security | your configured chat(s) |
| rnd | bot_token_rnd | your configured chat(s) |
