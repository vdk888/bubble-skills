---
name: prospect-research
description: Build or refresh a Research Capsule for a sales prospect. Pulls background, workflow pain points, recent signals, and three outreach angles (V1/V2/V3). Writes a structured Markdown file to your local vault. Read-only on social sources — never sends or posts anything.
version: 1.0.0
author: Bubble Invest
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebSearch
  - WebFetch
---

# prospect-research

Build or refresh a **Research Capsule** for a sales prospect: a structured Markdown file in your local vault plus an optional short summary projection you can paste into your CRM.

## When to invoke

- **On demand:** "Research [prospect name / company]" or "refresh capsule for [slug]"
- **In a pipeline:** call this skill after a discovery step produces a new lead row, before drafting outreach
- **Batch:** iterate over a list of slugs sorted by `next_refresh_at ASC`, research each one before handing off to your outreach step

## Inputs

- `slug` (required) — a short kebab-case identifier for this prospect (e.g. `jane-smith-acme`). You define the slug convention; keep it stable across refreshes.
- `force_refresh` (optional, default `false`) — if `true`, recompute all sections even when a capsule file already exists. If `false` and the file exists, append a refresh timestamp line to the History section and stop.

## Configuration — fill in before first use

Before running this skill, set your context in `prospect-research/config.md` (create it from the template at `prospect-research/templates/config-template.md`):

- **ICP definition** — who your ideal customer is (industry, role, company size, geography, problem type)
- **Your product/service** — what you offer and the core value proposition
- **Outreach angles** — customize the V1/V2/V3 framework (see below) to fit your offer
- **Vault directory** — where Research Capsules will be written (`~/your-vault/Capsules/` or any absolute path)
- **CRM field name** — the label for the short summary projection in your CRM (optional)

## Process

1. **Check for an existing capsule** at `{vault_dir}/Capsules/{slug}.md`.
   - If it exists and `force_refresh=false` → append a one-line refresh note to the History section and stop.
   - Otherwise → full research.

2. **Gather prospect data** — collect the following. **If a source is unavailable or uncertain, write `To enrich.`** (do not invent).
   - **Current role and background:** LinkedIn profile, company website, press releases. Note title, company, tenure, and any recent role change.
   - **Company context:** industry, size, business model. Public filings, Crunchbase, or company site.
   - **Mutual connections / existing relationship:** note any shared contacts, past interactions, or referrals.
   - **Recent signals:** LinkedIn activity (posts, comments), job postings at their company, recent news (funding, product launch, M&A, regulatory event). These are the hooks for V3.
   - **Workflow pain:** infer from their role + industry + your ICP definition. What time-consuming, error-prone, or high-stakes workflow does your product address for this person? Be specific (e.g. "manual reconciliation of X", "copy-paste between Y and Z").

3. **Build three outreach angles** — adapt these to your product using your `config.md`:
   - **V1 — Workflow pain:** the concrete, manual task your product removes. Frame it from their daily reality, not your feature list.
   - **V2 — Expertise / peer credibility:** a "practitioner-to-practitioner" angle — you understand their domain, not just their job title.
   - **V3 — External signal:** a rebound off a recent market event, regulatory change, industry consolidation, or news item relevant to them. Shows you did your homework.
   - **Recommended angle:** pick V1/V2/V3 based on what you found. Justify in one sentence.

4. **Recommended action:** propose a next step (`draft-outreach`, `warm-engage`, `research-more`, or `skip`). Base it on fit with your ICP + strength of signals found.

5. **Render the capsule** using `lib/capsule.py:render_capsule(research_input)` and the template at `templates/capsule-template.md`.

6. **Write the capsule file** to `{vault_dir}/Capsules/{slug}.md` (idempotent overwrite).

7. **Compute the CRM projection** (optional): `lib/capsule.py:compute_notes_projection(research_input)` → a ≤ 200-character summary suitable for a CRM notes field.

8. **Log a line** in `{vault_dir}/Daily/{YYYY-MM-DD}.md`: skill name, slug, recommended angle, proposed action, capsule path.

## Output

- **Capsule path** — absolute path of the written `.md` file
- **One-line summary** for your log or CRM:
  > `{slug} — capsule {created|refreshed} — angle V{1|2|3} — action {draft-outreach|warm-engage|research-more|skip}`

## Guardrails

- **Read-only on social sources.** This skill never posts, likes, comments, or sends messages. Outreach is a separate, human-approved step.
- **Do not invent signals.** If a piece of information cannot be found or verified, write `To enrich.` — never fabricate data to fill a section.
- **Defensive CRM writes.** If you integrate CRM writes, wrap them so a transient API error never prevents the capsule file from being written (the `.md` is the primary output).
- **Idempotent.** Re-running without `force_refresh=true` only adds a history line — nothing is overwritten.

## Files in this skill

```
prospect-research/
  SKILL.md                      # this file — skill instructions for Claude
  lib/
    capsule.py                  # pure-Python rendering helpers (stdlib only)
  templates/
    capsule-template.md         # Markdown template for Research Capsules
    config-template.md          # Fill this in with your ICP + vault path
  examples/
    example-research-input.py   # Annotated example of a research_input dict
```

## Quick start

1. Copy `templates/config-template.md` to `prospect-research/config.md` and fill it in.
2. Ask Claude: `"Research [Name] at [Company] — slug: name-company"`.
3. The capsule lands in your configured vault directory.

## Python helpers

See `lib/capsule.py` for the public API:

- `render_capsule(research_input, template_path=None) -> str`
- `write_capsule_file(slug, content, vault_dir) -> Path`
- `compute_notes_projection(research_input, max_len=200) -> str`
- `append_interaction_line(capsule_path, line) -> None`

All functions are pure Python (stdlib only), fully documented, and tested independently of any CRM or database backend.
