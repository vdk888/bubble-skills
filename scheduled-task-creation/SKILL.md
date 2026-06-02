---
name: scheduled-task-creation
description: Step-by-step guide for creating, registering, and debugging Claude Desktop scheduled tasks. Use when creating, registering, or debugging an automated scheduled task in the Desktop app.
version: 1.0.0
author: Bubble Invest
license: MIT
allowed-tools:
  - Bash
  - Read
  - Edit
---

# Creating Claude Desktop Scheduled Tasks

Desktop scheduled tasks have **TWO required components** — both must exist or the task won't appear in the UI and won't fire.

## Component 1: SKILL.md file

Location: `~/.claude/scheduled-tasks/{task-id}/SKILL.md`

Format:
```yaml
---
name: task-id
description: Short description of what it does and when it fires
---

[Prompt body — the exact instructions sent to Claude when the task fires]
```

Rules:
- YAML frontmatter has only `name` and `description` — nothing else
- The body is the prompt Claude receives at runtime
- The directory name must match the `id` in the registry entry

## Component 2: Registry entry in `scheduled-tasks.json`

Location: `~/Library/Application Support/Claude/claude-code-sessions/*/scheduled-tasks.json`

Find the file first:
```bash
find ~/Library/Application\ Support/Claude/claude-code-sessions -name "scheduled-tasks.json" 2>/dev/null
```

Registry entry schema:
```json
{
  "id": "task-name-kebab-case",
  "cronExpression": "3 8 * * *",
  "enabled": true,
  "filePath": "/Users/YOU/.claude/scheduled-tasks/task-name/SKILL.md",
  "createdAt": 1775643180398,
  "cwd": "/Users/YOU",
  "useWorktree": false,
  "permissionMode": "acceptEdits",
  "notifySessionId": "optional-session-id"
}
```

## Step-by-Step: Creating a New Scheduled Task

### Step 1 — Write the SKILL.md

```bash
mkdir -p ~/.claude/scheduled-tasks/my-task-name
```

Create `~/.claude/scheduled-tasks/my-task-name/SKILL.md`:
```yaml
---
name: my-task-name
description: What this task does and when it fires (e.g. Daily market check, Mon-Fri 8am)
---

Your prompt here. Write the full instructions Claude will receive when this task fires.
Be specific — Claude has no other context at runtime.
```

### Step 2 — Find the registry file

```bash
find ~/Library/Application\ Support/Claude/claude-code-sessions -name "scheduled-tasks.json" 2>/dev/null
```

This returns a path like:
`/Users/YOU/Library/Application Support/Claude/claude-code-sessions/abc123/scheduled-tasks.json`

### Step 3 — Add the entry to the registry

Read the current registry:
```bash
cat "/Users/YOU/Library/Application Support/Claude/claude-code-sessions/abc123/scheduled-tasks.json"
```

The file contains a JSON array. Add your new entry to the array. Use the current Unix timestamp in milliseconds for `createdAt`:
```bash
date +%s000
```

New entry to add:
```json
{
  "id": "my-task-name",
  "cronExpression": "3 8 * * 1-5",
  "enabled": true,
  "filePath": "/Users/YOU/.claude/scheduled-tasks/my-task-name/SKILL.md",
  "createdAt": 1775643180398,
  "cwd": "/Users/YOU",
  "useWorktree": false,
  "permissionMode": "acceptEdits"
}
```

Write the updated array back to the file.

### Step 4 — Verify in the Desktop app

Open Claude Desktop → Scheduled Tasks. The new task should appear. If it doesn't:
- Check that both the SKILL.md file and registry entry exist
- Verify the `id` in the JSON matches the directory name exactly
- Verify `filePath` is an absolute path to the SKILL.md

## Key Rules and Gotchas

**Cron format** — standard 5-field: `minute hour day-of-month month day-of-week`
- `3 8 * * 1-5` → 8:03am Monday–Friday
- `3 15 * * 1-5` → 3:03pm Monday–Friday
- `3 9 1 * *` → 9:03am on the 1st of each month
- `*/30 * * * *` → every 30 minutes

**Use :03 offset** — schedule at `:03` past the hour (e.g. `3 8 * *`) instead of `:00` to stagger API traffic.

**Minimum interval** — 1 minute for Desktop tasks.

**`permissionMode`** — use `"acceptEdits"` for most automated tasks (auto-approves file edits, still prompts for riskier actions). ⚠️ `"bypassPermissions"` runs with NO prompts at all — only opt into it for a task you fully trust, since a scheduled task running unattended with bypassed permissions can take any action without review.

**`useWorktree`** — set `true` if the task should run in an isolated git worktree. Usually `false`.

**`notifySessionId`** — optional; omit if not needed for session notifications.

**Tasks only run when:**
- The Claude Desktop app is open
- The computer is awake

**Catch-up behavior** — if the app was closed when a task was scheduled to fire, Desktop does one catch-up run when it reopens (looks back up to 7 days, runs once per missed task).

## NEVER do this

Do NOT use the Cowork MCP `create_scheduled_task` tool — it writes to a separate, disconnected registry that the Desktop app does not read. Tasks created that way will not appear in the Desktop UI and will not fire.

## Editing an Existing Task

- **Change the prompt**: edit `~/.claude/scheduled-tasks/{task-id}/SKILL.md` — next run uses the updated instructions automatically.
- **Change the schedule**: update `cronExpression` in the registry JSON.
- **Disable a task**: set `"enabled": false` in the registry JSON.

## Example: Full Working Task

SKILL.md at `~/.claude/scheduled-tasks/morning-briefing/SKILL.md`:
```yaml
---
name: morning-briefing
description: Daily morning briefing — checks news and portfolio, Mon-Fri 8am
---

Good morning. Please:
1. Check the latest financial news relevant to the portfolio
2. Summarize overnight market moves
3. Flag any urgent items that need attention today
Send a Telegram message with your briefing.
```

Registry entry in `scheduled-tasks.json`:
```json
{
  "id": "morning-briefing",
  "cronExpression": "3 8 * * 1-5",
  "enabled": true,
  "filePath": "/Users/YOU/.claude/scheduled-tasks/morning-briefing/SKILL.md",
  "createdAt": 1775643180398,
  "cwd": "/Users/YOU",
  "useWorktree": false,
  "permissionMode": "acceptEdits"
}
```
