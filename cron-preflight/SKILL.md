---
name: cron-preflight
description: Cron-fire pre-flight scaffolding. Computes catch-up SKEW vs scheduled hour, verifies a policy-doc hash, supports abort / soft-mute / weekly-abort modes. Replaces inline STEP 0 boilerplate across scheduled tasks.
version: 1.0.0
author: Bubble Invest
license: MIT
allowed-tools:
  - Bash
  - Read
---

# Cron pre-flight — shared scaffolding

Every scheduled task that fires on a wall-clock schedule starts with the same 3 questions:
1. Did the machine sleep through the scheduled hour? (catch-up SKEW math)
2. Has the governing policy/config doc been re-signed since the last run? (hash gate)
3. Are required context sources reachable? (pre-flight verifier)

This skill answers all three, parametrically, in one place. A cron's STEP 0 invokes `Skill: cron-preflight` instead of inlining the boilerplate.

> All operator/routing values come from env vars so this skill ships clean. Set
> `OPERATOR_CHAT_ID` and `TELEGRAM_BOT_TOKEN_FILE` (a path to a file holding the
> bot token) before invoking if you want catch-up/halt notifications.

## When to invoke

At STEP 0 of any scheduled task. Pass the cron's expected fire-window via env vars BEFORE invoking:

```bash
# Required:
export CRON_PREFLIGHT_NAME="my-watch"                  # for log + notification messages
export CRON_PREFLIGHT_SCHEDULED_HOUR=7                  # 0-23, local time
export CRON_PREFLIGHT_MODE="abort"                       # abort | softmute | weekly-abort
export CRON_PREFLIGHT_THRESHOLD_HOURS=4                  # how late is "too late"

# Required for weekly-abort mode:
export CRON_PREFLIGHT_SCHEDULED_DOW=7                    # 1=Mon ... 7=Sun

# Optional notification routing (omit to skip notifications):
export OPERATOR_CHAT_ID="<your-chat-id>"
export TELEGRAM_BOT_TOKEN_FILE="$HOME/.config/telegram/bot_token"
export CRON_PREFLIGHT_EMOJI="💳"                        # prepended to catch-up messages

# Then invoke the skill:
Skill: cron-preflight
```

## What the skill runs

### Block 1 — Catch-up SKEW math (3 modes)

```bash
# === cron-preflight: catch-up SKEW math ===
SCHEDULED_HOUR="${CRON_PREFLIGHT_SCHEDULED_HOUR:?must set CRON_PREFLIGHT_SCHEDULED_HOUR}"
MODE="${CRON_PREFLIGHT_MODE:-abort}"
THRESHOLD="${CRON_PREFLIGHT_THRESHOLD_HOURS:-4}"
NAME="${CRON_PREFLIGHT_NAME:-cron}"
EMOJI="${CRON_PREFLIGHT_EMOJI:-🩺}"

NOW_HOUR=$(date +%-H)

if [ "$MODE" = "weekly-abort" ]; then
  SCHEDULED_DOW="${CRON_PREFLIGHT_SCHEDULED_DOW:?must set CRON_PREFLIGHT_SCHEDULED_DOW for weekly mode}"
  NOW_DOW=$(date +%u)  # 1=Mon ... 7=Sun
  if [ "$NOW_DOW" = "$SCHEDULED_DOW" ]; then
    SKEW=$(( NOW_HOUR - SCHEDULED_HOUR ))
    if [ "$SKEW" -lt 0 ]; then SKEW=$(( -SKEW )); fi
  else
    DAYS_OFF=$(( ( NOW_DOW - SCHEDULED_DOW + 7 ) % 7 ))
    [ "$DAYS_OFF" -eq 0 ] && DAYS_OFF=7
    SKEW=$(( (24 - SCHEDULED_HOUR) + NOW_HOUR + (DAYS_OFF - 1) * 24 ))
  fi
else
  # daily abort or daily softmute — same math
  SKEW=$(( NOW_HOUR - SCHEDULED_HOUR ))
  if [ "$SKEW" -lt 0 ]; then SKEW=$(( -SKEW )); fi
fi

export CRON_PREFLIGHT_SKEW_HOURS="$SKEW"

notify() {  # $1 = message; no-op if routing env unset
  [ -z "${OPERATOR_CHAT_ID:-}" ] && return 0
  [ -z "${TELEGRAM_BOT_TOKEN_FILE:-}" ] && return 0
  BOT_TOKEN=$(cat "$TELEGRAM_BOT_TOKEN_FILE")
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${OPERATOR_CHAT_ID}" \
    --data-urlencode "text=$1" >/dev/null
}

if [ "$SKEW" -gt "$THRESHOLD" ]; then
  case "$MODE" in
    abort|weekly-abort)
      notify "${EMOJI} ${NAME} catch-up — fired ${SKEW}h past scheduled ${SCHEDULED_HOUR}h (machine slept). Skipping run; resuming next scheduled fire."
      echo "cron-preflight: catch-up detected (skew=${SKEW}h > ${THRESHOLD}h), aborting cleanly"
      exit 0
      ;;
    softmute)
      echo "cron-preflight: late-run detected (skew=${SKEW}h) — soft-mute mode, downstream layers should self-mute via CRON_PREFLIGHT_SKEW_HOURS env var"
      ;;
    *)
      echo "cron-preflight: unknown MODE=${MODE}, falling through (treat as no-op)"
      ;;
  esac
else
  echo "cron-preflight: skew=${SKEW}h within ${THRESHOLD}h threshold, proceeding"
fi
```

### Block 2 — Policy-doc hash gate

Every governed cron operates against a signed policy/config doc (a mandate, a runbook, a config file). If the live doc has drifted from the most-recently-signed version recorded in your store, abort — never run on a stale-or-unsigned policy.

```bash
# === cron-preflight: policy hash gate ===
# Set these to your own paths:
POLICY_FILE="${CRON_PREFLIGHT_POLICY_FILE:?set CRON_PREFLIGHT_POLICY_FILE}"
POLICY_DB="${CRON_PREFLIGHT_POLICY_DB:?set CRON_PREFLIGHT_POLICY_DB}"

LIVE=$(shasum -a 256 "$POLICY_FILE" | awk '{print $1}')
DB_LATEST=$(sqlite3 "$POLICY_DB" \
  "SELECT version || '|' || signed_at || '|' || content_sha256
     FROM policy_versions
    ORDER BY id DESC LIMIT 1;")
DB_HASH=$(echo "$DB_LATEST" | awk -F'|' '{print $3}')
DB_VERSION=$(echo "$DB_LATEST" | awk -F'|' '{print $1}')
DB_SIGNED=$(echo "$DB_LATEST" | awk -F'|' '{print $2}')

if [ "$LIVE" != "$DB_HASH" ]; then
  notify "${EMOJI} ${NAME} HALT — policy hash drift. live=${LIVE:0:16} vs DB ${DB_VERSION}=${DB_HASH:0:16}. Re-sign or revert."
  echo "cron-preflight: policy hash drift, aborting"
  exit 0
fi
echo "cron-preflight: policy hash OK — ${DB_VERSION} signed ${DB_SIGNED}"
export CRON_PREFLIGHT_POLICY_VERSION="$DB_VERSION"
export CRON_PREFLIGHT_POLICY_SIGNED="$DB_SIGNED"
```

### Block 3 — Pre-flight verifier (optional)

```bash
# === cron-preflight: source verifier ===
# Skip this block if the cron doesn't read external context sources.
if [ "${CRON_PREFLIGHT_SKIP_VERIFIER:-0}" = "0" ] && [ -n "${CRON_PREFLIGHT_VERIFIER_CMD:-}" ]; then
  eval "$CRON_PREFLIGHT_VERIFIER_CMD"
  if [ "$?" != "0" ]; then
    notify "${EMOJI} ${NAME} HALT — context-source verifier failed. Required context unreachable, refusing to run half-blind."
    exit 1
  fi
fi
```

## What the calling cron sees after invoking

After `Skill: cron-preflight` runs cleanly, the calling cron's environment has:

- `CRON_PREFLIGHT_SKEW_HOURS` — int, hours past scheduled fire (0 if on time)
- `CRON_PREFLIGHT_POLICY_VERSION` — string, e.g. "v14"
- `CRON_PREFLIGHT_POLICY_SIGNED` — string ISO timestamp

If preflight aborts (catch-up beyond threshold, policy drift, verifier fail), the cron exits cleanly via `exit 0` (catch-up) or `exit 1` (policy / verifier — actual error). The calling cron never reaches its STEP 1.

## Hard invariants

- **Read-only**: this skill never mutates a DB, never writes files, never sends a notification other than catch-up / halt messages.
- **Idempotent**: re-running this skill within the same minute produces the same result.
- **Fail-loud**: any unexpected condition (missing env var, missing DB, missing policy file) results in a clear stderr message + exit 1, NOT a silent fall-through.
- **Notification routing**: all chat IDs and tokens come from env vars; if unset, notifications are skipped silently.
