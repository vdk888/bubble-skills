---
name: fund-source-verification
description: Source-tier classification + independent-verification rubric for any external signal (news, Substack, paywalled wires, sentiment trackers). Load whenever you're about to act on a third-party claim or write "<outlet> reports X" in a memo.
version: 1.0.0
author: Bubble Invest
license: MIT
---

# Fund source verification — tier discipline + corroboration rubric

Operating principle: **the source is a HYPOTHESIS, not an answer.** Cross-source independent verification is THE workflow, not a polish step.

## When to invoke

- Any research step that turns a third-party claim into a note, a proposal, or KPI commentary; whenever you're tempted to write "<outlet> reports X" without a second-source check.

## Source tier definitions

Maintain your own curated source-tier list (e.g. a `sources.yaml`) mapping each outlet to a tier. Tiers drive corroboration math:

- **tier_a — high trust; institutional wire / central bank / primary data.** Solo corroboration accepted for "investigate deeper". Examples: FT Markets, ECB Press, BEA, FRED Research News, FRED Blog.
- **tier_b — medium trust; curated commentary / paywall mirrors.** Examples: named research desks, financial-press mirrors of well-known commentators, thematic Substack pieces.
- **tier_c — noise-tolerant; contrarian/sentiment.** NEVER surfaces an idea alone. Examples: contrarian blogs, retail sentiment trackers.

Keep the full per-source classification in your sources list — look up `tier:` per source name when citing, rather than duplicating it in prose.

## Verification rubric

For every candidate, before you score, write up, or propose:

1. **Find ≥2 independent corroborating signals.** Independence means different information chain (Reuters citing Bloomberg ≠ Bloomberg citing Reuters — that is ONE chain), different measurement (headline + price/flow number = independent; two headlines saying the same = ONE point), or different angle/horizon.
2. **Use ≥2 of these methods:** price-action check (price bars on named tickers), structural data (filings, FRED, BEA, policy docs — primary not commentary), your own telemetry (prior memos, position history, KPI history), independent coverage (web search across 2-3 outlets), logic/math sanity check (work the numbers yourself).
3. **Tier gating:**
   - tier_a solo OK if rest of evidence is structural (price action, position flag, calendar event)
   - tier_b needs ≥1 tier_a OR ≥1 additional tier_b
   - tier_c needs ≥2 independent tier_a corroborations — tier_c solo gets a heavy penalty (effectively dead)
4. **Paywall check:** if you only see title/lede, treat the source as a hypothesis prompt, not evidence. Run the full rubric on the thesis as inferred from public coverage. Never fabricate what the paywalled body "probably" says.
5. **Recency / budget:** spend ≤3-5 minutes per candidate. If it doesn't corroborate inside that budget, drop it — a real signal will resurface tomorrow with more evidence.

## What to write when verified

In the brief / memo, every retained item shows:

```
Thesis source: <name, tier>
Verification:
  - <independent method 1>: <what you checked, what you found>
  - <independent method 2>: <what you checked, what you found>
Corroborated: yes / partial / no
```

When citing tier_c, ALWAYS pair with the tier_a signal that promoted it — e.g. "retail sentiment on URA bullish (tier_c) + uranium spot +8% WTD (Reuters Energy tier_a) + URA 20d RS vs SPY +4.3 ppts (calc)."

## Failure modes

- **No corroboration found inside budget** → mark `unverified — discarded`; demote per your gating math (tier_c solo penalized; tier_b unaccompanied does not pass; tier_a solo + structural is the minimum). Land it in the brief's `Discarded` section with one line on what failed — transparency matters.
- **Sibling-source dressing (FORBIDDEN):** never count a Reuters story re-published by a contrarian blog as two sources. That is one chain. Same for a Substack quoting FT, or a press outlet mirroring a commentator verbatim — the mirror plus the original ≠ two sources.
- **Paywall fabrication (FORBIDDEN):** never write "the FT piece probably argues X" as if it were evidence. The lede is the only thing that exists for verification purposes.
- **Skipping the rubric to pad a TOP-N list:** a brief with zero `Discarded` entries on an average-signal day is suspicious — either the rubric was skipped or weak candidates were smuggled in. The discard tail is a feature.

---

*Pure reference skill — no shell commands, no actions. This file is the rubric only; keep your per-source tier list and your scoring math elsewhere.*
