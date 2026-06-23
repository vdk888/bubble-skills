---
name: cron-postflight
description: Cron-fire post-flight scaffolding. Audit-log INSERT, git commit + push, notification send. Replaces inline wrap-up boilerplate across scheduled tasks. Companion to cron-preflight.
version: 1.0.0
author: Bubble Invest
license: MIT
allowed-tools:
  - Bash
  - Read
---

# Cron post-flight — shared scaffolding

Every scheduled task tends to end with the same 3 chores:
1. Write an `audit_log` row recording what happened (actor, action, target, outcome)
2. Commit + push any repo state mutated this run
3. Send a notification with the run summary

This skill provides parametric helpers for all three. Companion to `cron-preflight` (which handles the start of the run).

> Notification routing comes from env vars so this skill ships clean. Set
> `OPERATOR_CHAT_ID` and a token file path before using Block 3.

## When to invoke

In any cron's wrap-up STEP. Each helper is a separate Block — invoke whichever you need; you don't have to use all 3.

## Block 1 — Audit log row

```bash
# === cron-postflight: audit_log helper ===
# Required env:
#   POSTFLIGHT_DB        — path to your sqlite DB
#   POSTFLIGHT_ACTOR     — e.g. 'scout' | 'risk-manager'
#   POSTFLIGHT_ACTION    — e.g. 'cluster_refresh' | 'heartbeat_complete'
#   POSTFLIGHT_TARGET    — entity touched, e.g. 'vault/clusters/'
#   POSTFLIGHT_DETAILS   — pipe-separated key=value summary
#   POSTFLIGHT_OUTCOME   — 'success' | 'partial' | 'failed'
sqlite3 "${POSTFLIGHT_DB:?must set POSTFLIGHT_DB}" \
  "INSERT INTO audit_log (logged_at, actor, action, target, details, outcome)
   VALUES (
     strftime('%Y-%m-%dT%H:%M:%fZ','now'),
     '${POSTFLIGHT_ACTOR:?must set POSTFLIGHT_ACTOR}',
     '${POSTFLIGHT_ACTION:?must set POSTFLIGHT_ACTION}',
     '${POSTFLIGHT_TARGET:?must set POSTFLIGHT_TARGET}',
     '${POSTFLIGHT_DETAILS:-}',
     '${POSTFLIGHT_OUTCOME:-success}'
   );"
```

## Block 2 — Git commit + push

```bash
# === cron-postflight: git commit + push helper ===
# Required env:
#   POSTFLIGHT_GIT_WORKDIR  — absolute path to repo root
#   POSTFLIGHT_GIT_MESSAGE  — commit message body (multi-line OK; use $'\n' for literal newlines)
# Optional env:
#   POSTFLIGHT_GIT_PATHSPEC — files to add (default: -A); e.g. "vault/clusters/" to scope
#   POSTFLIGHT_GIT_PUSH     — 'yes' (default) | 'no' (skip remote push)
#   POSTFLIGHT_GIT_LANE     — if set, refuses to commit changes outside this path

cd "${POSTFLIGHT_GIT_WORKDIR:?must set POSTFLIGHT_GIT_WORKDIR}"

# Pre-check — show what would be committed
echo "[postflight] git status (before commit):"
git status --short

# Lane discipline — if pathspec is restricted, abort if changes leak outside
if [ -n "${POSTFLIGHT_GIT_LANE:-}" ]; then
  OFFENDING=$(git status --short | awk '{print $2}' | grep -v "^${POSTFLIGHT_GIT_LANE}" | head -3)
  if [ -n "$OFFENDING" ]; then
    echo "[postflight] git LANE breach — changes outside ${POSTFLIGHT_GIT_LANE}: $OFFENDING"
    echo "[postflight] aborting commit; investigate the lane crossing manually"
    exit 1
  fi
fi

# Add + commit
git add ${POSTFLIGHT_GIT_PATHSPEC:--A}
if git diff --cached --quiet; then
  echo "[postflight] no staged changes — skipping commit (no-op)"
  COMMIT_OUTCOME="noop"
else
  git commit -m "${POSTFLIGHT_GIT_MESSAGE:?must set POSTFLIGHT_GIT_MESSAGE}"
  COMMIT_OUTCOME="committed"
fi

# Push (non-fatal — local commit stands either way)
if [ "${POSTFLIGHT_GIT_PUSH:-yes}" = "yes" ] && [ "$COMMIT_OUTCOME" = "committed" ]; then
  git push origin main 2>&1 || echo "[postflight] push failed — local commit intact"
fi
```

## Block 3 — Notification

```bash
# === cron-postflight: notification helper ===
# Required env:
#   POSTFLIGHT_TG_BODY  — message body (string; most chat APIs cap at ~4096 chars per message)
# Optional env:
#   OPERATOR_CHAT_ID         — target chat id
#   TELEGRAM_BOT_TOKEN_FILE  — path to a file holding the bot token

BOT_TOKEN=$(cat "${TELEGRAM_BOT_TOKEN_FILE:?set TELEGRAM_BOT_TOKEN_FILE}")
CHAT_ID="${OPERATOR_CHAT_ID:?set OPERATOR_CHAT_ID}"
BODY="${POSTFLIGHT_TG_BODY:?must set POSTFLIGHT_TG_BODY}"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHAT_ID}" \
  --data-urlencode "text=${BODY}"
```

**Note on Markdown rendering**: Block 3 sends as plain text — no `parse_mode`. Asterisks, underscores, backticks render literally. If you need Markdown rendering, use a JSON-POST pattern with `parse_mode: Markdown` instead — but then every caller must escape special chars, which is usually more friction than it's worth.

For attachments (chart PNGs etc.), use `sendPhoto` instead:

```bash
BOT_TOKEN=$(cat "$TELEGRAM_BOT_TOKEN_FILE")
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
  -F chat_id="$OPERATOR_CHAT_ID" \
  -F photo=@/tmp/brief_chart.png \
  -F caption="<one-line caption>"
```

## What the calling cron sees

Each block is independent — they don't communicate via env vars. After each successful block, the calling cron simply continues. After a failed block (e.g. git lane breach), exit code is non-zero — the cron should not assume Block N+1 ran.

## Hard invariants

- **DB writes only via Block 1**: keep a single audit-trail discipline — never INSERT to your DB from elsewhere in the post-flight phase.
- **Notification routing**: all chat IDs and tokens come from env vars.
- **Git push is non-fatal**: a failed `git push origin main` does NOT fail the cron; local commit stands and the next run retries the push.
- **Lane discipline (Block 2)**: when `POSTFLIGHT_GIT_LANE` is set, refuses to commit anything outside that path — prevents a cron crossing perimeter.
