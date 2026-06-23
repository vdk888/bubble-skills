---
name: deepseek-brain
description: Switch a Claude Code agent (Mac CLI, VPS systemd, or launchd) from Anthropic to DeepSeek as the LLM backend. Use when you want to run Claude Code with DeepSeek while keeping the full harness (tools, files, skills, channels). Covers the reasoning-effort proxy, model routing, channels fix, and rollback.
version: 1.0.0
author: Bubble Invest
license: MIT
---

# deepseek-brain — Run Claude Code on DeepSeek

Switch any Claude Code agent's LLM backend from Anthropic to DeepSeek.
The Claude Code harness (tools, files, skills, MCP servers, channels) stays
intact — only the brain changes.

> This skill documents a configuration pattern. It does not bundle a proxy
> binary; the proxy is ~120 lines of Python 3 stdlib that you write once from
> the spec below (or adapt from any minimal Anthropic-passthrough proxy).

## When to use

- You want an always-on Claude Code agent on a VPS running DeepSeek instead of Anthropic
- You want to run a local DeepSeek-powered Claude Code session (CLI or persistent bot)
- You're migrating an agent to a different LLM backend
- You need a larger context window than your current backend offers

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code │────▶│ deepseek-proxy.py │────▶│ api.deepseek.com │
│  (harness)   │     │ 127.0.0.1:8746    │     │ /anthropic/v1/...│
└─────────────┘     └──────────────────┘     └─────────────────┘
   ▲                        │
   │  strips reasoning_effort from
   │  thinking:disabled aux calls
   │  (fixes WebSearch/WebFetch 400)
   │
   ANTHROPIC_BASE_URL=http://127.0.0.1:8746/anthropic
```

### Why the proxy is needed

DeepSeek's `/anthropic` endpoint accepts exactly two states:
- **(A) thinking ON:** `reasoning_effort` set, `thinking:{type:"enabled"}` → OK
- **(B) thinking OFF:** NO `reasoning_effort`, `thinking:{type:"disabled"}` → OK

The Claude Code harness, on cheap aux calls (WebSearch result-summary, WebFetch,
sub-agents), sends BOTH `thinking:{type:"disabled"}` AND `reasoning_effort`
→ 400 error. The proxy strips `reasoning_effort` from those calls, leaving a clean
state (B). All other requests pass through untouched.

Build the proxy as a **streaming** (chunked transfer, no buffering) and **threaded**
(concurrent aux+main calls don't deadlock) passthrough. Pure Python 3 stdlib — zero
dependencies. It listens on `127.0.0.1:8746/anthropic`, forwards to
`https://api.deepseek.com/anthropic`, and on each request body removes the
`reasoning_effort` key whenever `thinking.type == "disabled"`.

## Prerequisites

1. **DeepSeek API key** from https://platform.deepseek.com/api_keys
2. **Claude Code** installed (any recent version)
3. **Python 3** (for the proxy; stdlib only)
4. For VPS deployments: a secret-management approach (e.g. SOPS + age) for the API key

## Deployment — Mac (CLI session)

### One-shot or interactive session

Write a `run-deepseek.sh` launcher that starts the proxy, waits for it to bind, exports the env vars below, then `exec claude`:

```bash
export DEEPSEEK_API_KEY="sk-..."
./run-deepseek.sh           # interactive
./run-deepseek.sh -p "..."  # headless one-shot
```

Env vars the launcher must set:

| Env var | Value | Why |
|---|---|---|
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:8746/anthropic` | Route to proxy |
| `ANTHROPIC_AUTH_TOKEN` | DeepSeek API key | Auth |
| `ANTHROPIC_MODEL` | `deepseek-v4-pro[1m]` | 1M context (no `[1m]` = 200K) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | same | All tiers → pro |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | same | All tiers → pro |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `deepseek-v4-pro[1m]` | **Critical**: flash tier disables thinking → 400 |
| `ANTHROPIC_SMALL_FAST_MODEL` | `deepseek-v4-pro[1m]` | Same — prevent thinking disable |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `deepseek-v4-pro[1m]` | Sub-agents also use pro |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | Reasoning depth |

**Key rule:** All model aliases point to the same pro model. Never route aux
calls to a flash tier — it disables thinking and the endpoint rejects the combo.

### Persistent bot (Mac launchd)

```bash
# 1. Put your channel/bot token where your launcher can read it, e.g.:
mkdir -p ~/.config/claude-deepseek
echo "BOT_TOKEN=<bot_token>" > ~/.config/claude-deepseek/.env

# 2. Encrypt the API key (example with SOPS + age)
# Create .sops.yaml with your age key, then:
sops --encrypt --age <age-pubkey> secrets.sops.env

# 3. Install a launchd agent that runs your launcher under tmux (see VPS note on PTY)
cp com.example.deepseek-bot.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.deepseek-bot.plist
```

## Deployment — VPS (systemd agent)

### Step 1 — Deploy the proxy

```bash
scp deepseek-proxy.py <host>:<agent-workspace>/deepseek-proxy.py
```

### Step 2 — Add the DeepSeek API key to your secret store

Add `DEEPSEEK_API_KEY` to whatever encrypted env file your service decrypts at
start (e.g. a SOPS-encrypted env file). Use your own secret-management tooling.

### Step 3 — Create the launcher script

The launcher is a shell script that:
1. Sources the decrypted env (API key)
2. Starts `deepseek-proxy.py` in the background
3. Waits for the proxy to bind
4. Exports all DeepSeek env vars (see Mac table above)
5. `exec claude` (replaces the shell process)

On a VPS the env is typically decrypted by a systemd `ExecStartPre` into a
runtime path (e.g. `/run/claude-agent/env`); the launcher sources that file
instead of decrypting inline.

### Step 4 — Create a systemd drop-in

Create `/etc/systemd/system/<service-name>.service.d/deepseek.conf`. Replace
`ExecStart` with a tmux pattern so Claude gets a real PTY (required for channels):

```ini
[Service]
ExecStart=
ExecStart=/bin/bash -c '\
  /usr/bin/tmux kill-session -t agent-deepseek 2>/dev/null || true; \
  /usr/bin/tmux new-session -d -s agent-deepseek \
    "cd <working-dir> && <agent-workspace>/run-deepseek.sh"; \
  while /usr/bin/tmux has-session -t agent-deepseek 2>/dev/null; do \
    sleep 30; \
  done'
```

**Critical:** Use tmux, not `script -qfc`. The tmux pattern gives Claude a real
PTY. Without it, channel registration may fail even when enabled in settings.

### Step 5 — Fix managed settings (if present)

If the agent uses managed settings at `/etc/claude-code/managed-settings.json`:

1. Add `"channelsEnabled": true` at the top level (recent Claude Code versions
   disable channels by default when managed settings are present)
2. Add `"api.deepseek.com"` to `sandbox.network.allowedDomains` (the sandbox
   proxy blocks egress to domains not in the allowlist)

```bash
python3 << 'PYEOF'
import json
with open("/etc/claude-code/managed-settings.json") as f:
    s = json.load(f)
s["channelsEnabled"] = True
domains = s.setdefault("sandbox", {}).setdefault("network", {}).setdefault("allowedDomains", [])
if "api.deepseek.com" not in domains:
    domains.append("api.deepseek.com")
with open("/etc/claude-code/managed-settings.json", "w") as f:
    json.dump(s, f, indent=2)
PYEOF
```

### Step 6 — Reload and verify

```bash
systemctl daemon-reload
systemctl restart <service-name>
systemctl status <service-name> --no-pager
# Should show: active (running), tmux session, deepseek-proxy.py running.
```

## Rollback

### VPS

```bash
rm /etc/systemd/system/<service-name>.service.d/deepseek.conf
systemctl daemon-reload
systemctl restart <service-name>
```

Back to Anthropic. Zero data loss — the workspace, memory, and channel state are untouched.

### Mac

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.example.deepseek-bot.plist
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "channels blocked by org policy" | managed settings lacks `channelsEnabled: true` | Add it (Step 5) |
| No channel messages received | channel registration failed (no PTY, or old Claude Code) | Use tmux pattern in ExecStart (Step 4) |
| WebSearch/WebFetch returns 400 | `thinking:disabled` + `reasoning_effort` combo rejected | Ensure proxy is running; check all model aliases point to `-pro[1m]`, not flash |
| Context meter shows >300% | Missing `[1m]` suffix on model name | Default context is 200K; `[1m]` unlocks 1M |
| npm auto-update on startup | Claude Code detects a newer version, installs it | Normal; wait ~30s. The updated version works if managed settings are correct |

## Files reference

| File | Purpose |
|---|---|
| `deepseek-proxy.py` | Reasoning-effort-stripping proxy (stdlib Python 3) — you write this from the spec above |
| `run-deepseek.sh` | CLI / bot launcher (sets env + starts proxy + exec claude) |
| `com.example.deepseek-bot.plist` | Mac launchd plist (reference for the tmux pattern) |
