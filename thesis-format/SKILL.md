---
name: thesis-format
description: Canonical 7-part investment thesis structure. Use whenever you write a position note, proposal memo, decision-reasoning row, idea-scout idea, theme note, or chat brief naming a specific bet. Every new thesis MUST follow this skeleton. Not investment advice.
version: 1.0.0
author: Bubble Invest
license: MIT
allowed-tools:
  - Read
  - Edit
  - Write
---

# thesis-format — the 7-part structure

> **Not investment advice.** This skill is a method for structuring your own research and reasoning. It recommends no investment, and nothing it produces is personalised advice.

This is a single source of truth for HOW to articulate an investment bet. Every new thesis MUST conform to this structure. The structure renders at three depths — a reference file, a proposal memo, a chat/phone render — using the same skeleton, just at different densities.

The idea is **progressive disclosure**: the same content, three rendering surfaces, no thesis ever lives at only one depth.

## Why this exists

Three problems this solves:

1. **Comparability.** Without a fixed structure, theses can't be ranked, conviction can't be tracked, kill triggers can't be audited. A standardized skeleton makes any thesis comparable to any other in the book.
2. **Falsifiability.** Section 4 (INVALIDATION) is mandatory. No thesis enters the book without a written kill condition. This is the discipline that prevents narrative drift.
3. **AI-agent + human dual readability.** The YAML frontmatter is machine-queryable; the prose body is human-readable; the chat render is phone-skim-friendly. One source, three surfaces.

## The 7 sections

Every thesis MUST have these 7 sections, in this order, with these exact section names. Skip a section ONLY by writing one line stating WHY it doesn't apply (e.g., "no asymmetry framing for a hedge — see section 4"). A section silently omitted is a bug.

### 1. CLAIM
A single declarative sentence stating the directional bet. No qualifiers ("potentially," "should," "may"). Just the bet.

Pattern: `[Buy / Sell / Hedge with] [INSTRUMENT] because [SPECIFIC OBSERVABLE WILL HAPPEN] over [HORIZON].`

Examples (good):
- "Buy EXBIO 2% NAV because equal-weight biotech captures the AI-drug-discovery premium that cap-weight EXCAP dilutes, over 6-18 months."
- "Hedge with EXINF 1% NAV because inflation will surprise upward as the central bank lags AI-capex spillover, over 12-24 months."

(All tickers and numbers in this skill are invented for illustration: EXBIO, EXCAP, EXINF, EXMP and their peers are not real instruments.)

Examples (bad — rewrite):
- "EXBIO looks attractive given biotech tailwinds." (No bet, no observable, no horizon.)
- "Add some infrastructure exposure for diversification." (Diversification is not a thesis.)

### 2. CAUSAL MECHANISM
The chain of cause-and-effect that connects the observable in §1 to the price moving in your favor. Must be explicit, not assumed.

Format: numbered chain, 3-7 links. Each link names an actor or mechanism, not a vibe.

Example (EXBIO):
1. Large pharma companies facing patent cliffs → must replenish pipeline
2. AI-drug-discovery shortens preclinical timeline from several years to a few
3. Small/mid AI-native biotechs become M&A targets
4. Equal-weight EXBIO captures takeover premium across many candidates
5. Cap-weight EXCAP blunts effect (a few large acquirers = a large share of the fund, no upside from M&A on themselves)
6. → EXBIO outperforms EXCAP; you own the right vehicle for the structural pattern.

This forces "I believe X because Y because Z" articulation. No pattern-matching.

### 3. PORTFOLIO FIT
Where this slots in the existing book. CITE NUMBERS — correlations to current holdings, cluster impact, sleeve consumption.

Required sub-elements:
- **Diversifies what?** Specific cluster or position the bet's correlation profile reduces overlap with.
- **Duplicates what?** Specific cluster or position the bet partially overlaps. State the overlap so you don't pretend it's pure-new.
- **Cluster impact:** Does this add to an existing cluster (concentration risk), open a new cluster, or sit between clusters?
- **Sleeve consumption:** which sleeve (e.g. ETF backbone / single-stock / crypto / event) and how much of it does this consume post-add?

A thesis without a portfolio-fit section is incomplete because it doesn't answer "why now, why this, why not something else you already own?"

### 4. INVALIDATION (kill conditions) — MANDATORY, NUMERIC
The most important section. What concrete, observable, numeric event would PROVE this thesis wrong (in part or full)?

Must be:
- **Numeric** — "rate spikes >5.5%" not "rates rise"
- **Time-bound** — "5+ consecutive sessions" not "for a while"
- **Distinct** — full-exit triggers separated from trim triggers separated from "watch closely" triggers
- **Asymmetric to entry** — exit triggers should be tighter than entry conviction, not looser

Three classes of trigger:
- **HARD STOP** — full exit, no judgment call. Usually -20% from entry, or a specific structural break.
- **THESIS KILL** — full exit because the underlying mechanism (§2) is broken. E.g., "AI-capex guidance reduced at the largest cloud providers" for an infra bet.
- **TRIM TRIGGER** — partial exit (typically 50%) on heightened risk that doesn't fully break the thesis. E.g., "10Y rates spike >5.5% sustained" for a rate-sensitive bet.

A thesis without numeric invalidation is faith, not investment.

### 5. SIZING + TIME HORIZON
Why THIS size, not bigger or smaller. Why this horizon to evaluate.

Required sub-elements:
- **Size class:** STARTER (1-2% NAV, low conviction or new asset class) / CONVICTION (3-5% NAV, well-understood thesis with track record) / CORE (6%+, only after multi-month positive evidence) / HEDGE (sized to the risk it offsets, not the alpha)
- **Why this size:** Articulate the bound. "Why not 5% NAV? Because correlation to AI-credit cracks scenario is unproven; need 3 months of behavior before upsize."
- **Horizon to evaluate:** When do you re-grade conviction? "12 weeks for a starter; if tracking diverges by >5ppts that's the upsize/exit decision."
- **Marginal-risk-contribution citation** (recommended for any addition >2% NAV, required for single-stock if your mandate demands it).

### 6. ASYMMETRY
Up-case vs down-case rough magnitudes. Without this, sizing is arbitrary.

Format: `Up: +X% over <horizon> if <condition>. Down: -Y% over <horizon> if <condition>. Asymmetry ratio ≈ X:Y.`

Example (EXBIO): "Up: +30% over 12-18m if AI-drug-discovery thesis manifests as accelerating M&A flow. Down: -15% if rates spike + biotech credit dries up. Asymmetry ≈ 2:1."

If asymmetry is less than 1:1, the thesis must explicitly frame as a HEDGE (i.e., you accept negative-EV in exchange for protection in a tail scenario). Don't pretend a hedge is a positive-EV bet.

### 7. CONVICTION LEVERS
The middle ground between "intact" and "killed." What concrete observables would move conviction up or down WITHOUT triggering full exit/upsize?

Format: bulleted list, each line declarative + observable.

Examples:
- Up-conviction (would prompt upsize proposal):
  - A high-trust outlet specifically corroborates the thesis
  - 3-month price action confirms the mechanism
  - Cross-asset confirmation (e.g., bond market signals same regime)
- Down-conviction (would prompt watch elevation, not full exit):
  - A single high-trust outlet refutes a key link in §2
  - 3-month action diverges meaningfully from the comparable (e.g., EXBIO vs EXCAP)
  - Cross-asset divergence (e.g., AI capex narrative confirmed in equity but rejected in credit)

## Surface 1: REFERENCE FILE — the canonical implementation

A per-position file (e.g. `positions/<TICKER>.md`) and per-theme file (e.g. `themes/<theme>.md`).

YAML frontmatter — machine-queryable. Suggested fields:

```yaml
---
ticker: EXMP
weight_pct: 2.0
conviction: 3
view: hold
opened_at: 2025-01-15T00:00:00Z

thesis_slug: example-infra-broad
claim: "Buy EXMP 2% NAV because a broad infrastructure basket captures AI-data-center power demand more broadly than the narrow nuclear fund EXNUC, over 12-24 months."
size_class: starter
horizon_weeks: 52
diversifies: [narrow_nuclear, single-country-utility]
duplicates: [partial: ex_us_equity]
hedge_for: null  # null if directional bet; ticker/scenario name if hedge
asymmetry:
  up_pct: 30
  down_pct: -15
  horizon_months: 18
  ratio: "2:1"
invalidation_triggers:
  - type: hard_stop
    rule: "EXMP -20% from entry price"
  - type: thesis_kill
    rule: "Largest cloud providers cut next-year capex guidance"
  - type: trim_50
    rule: "10Y rates >5.5% sustained 5+ sessions"
  - type: structural_break
    rule: "EXMP closes below its 200-day moving average"
correlations_at_entry:  # illustrative round values
  EXSEMI: 0.3
  EXBOND: 0.3
  EXWORLD: 0.4
upcase_levers: ["high-trust corroboration of AI-power thesis", "3m EXMP tracks its peer EXPEER", "transmission cap-rate compression"]
downcase_levers: ["single high-trust refutation of capex thesis", "3m EXMP underperforms EXPEER >5ppts", "credit cracks not transmitting to equity"]
---
```

Body sections — prose 1-7 with these exact headers (use `## 1. CLAIM`, `## 2. CAUSAL MECHANISM`, etc).

Length: 400-800 words. Above 1000, split detail into a `theses/<slug>.md` reference file and link.

## Surface 2: PROPOSAL MEMO + decision-reasoning

A dated proposal memo (e.g. `YYYY-MM-DD-<slug>-proposal.md`) and the reasoning field of your decision record.

The proposal memo opens with a 6-line summary block (machine-readable, human-skim-friendly):

```
CLAIM:        Buy EXMP 2% NAV because a broad infra basket captures AI-data-center power demand, over 12-24m.
SIZE:         2% NAV (starter); upsize gate at 12 weeks if EXMP tracks its peer EXPEER within 2ppts.
HORIZON:      12-18 months evaluation; multi-year hold if thesis confirms.
CONVICTION:   3/5; would move to 4 if cloud-provider capex re-accelerates next year.
ASYMMETRY:    +30% / -15% over 18m (~2:1 up-skew).
KILL:         Cloud-provider capex cuts (thesis-kill) · 10Y >5.5% 5+ sessions (trim-50) · 200d MA break (structural).
```

Then sections 1-7 in detail. Keep the memo ~600-1200 words; defer correlation tables and detailed math to the reference note.

The decision-reasoning field gets the 6-line summary block + 2-3 sentences per section. Total ~500-800 chars — long enough for audit-trail completeness, short enough for quick review.

## Surface 3: CHAT — 5-line compact render

The phone-friendly version. Use for: idea-scout TOP-N ideas, brief mentions of new bets, formal proposal pings, execution confirmations, weekly retrospective per-position summaries.

Exact format (5 lines + 1 header line):

```
🎯 EXMP (2% NAV, conv 3/5, starter · 12-18m)
CLAIM: Capture AI-data-center power demand broadly via a broad infra basket.
WHY: Data-center power demand doubles → utilities/transmission/grid pricing power. Not redundant w/ EXNUC narrow-nuclear (corr EXSEMI +0.3).
KILL: Cloud-provider capex cuts · 10Y >5.5% 5+ sessions · 200d MA break.
ASYM: +30% / -15% over 18m (~2:1 up-skew).
```

Rules:
- **Line 1 header:** `🎯 <TICKER> (<size>% NAV, conv <X>/5, <size_class> · <horizon>)`
- **Line 2 CLAIM:** the single sentence, copied verbatim from §1 of the reference file.
- **Line 3 WHY:** condensed §2 mechanism, 1-2 sentences. Cite at least one concrete number (correlation, return, threshold).
- **Line 4 KILL:** condensed §4 — top 3 invalidators separated by `·`. Use the type-prefix format ("trim-50", "thesis-kill") only for clarity.
- **Line 5 ASYM:** §6 magnitudes + ratio. If hedge, write `HEDGE FOR: <scenario>` instead of asymmetry numbers.

Total: 5 lines, ~250-350 chars per thesis. Three theses = ~1000-1100 chars — fits inside a typical 4096-char chat message cap with room for other sections.

## Failure modes to avoid

- **Filling sections with vibes.** §2 CAUSAL MECHANISM is the test — if you can't write 3-7 specific links, you don't have a thesis, you have a hunch.
- **Vague invalidators.** "If it doesn't work" is not a kill trigger. Numeric + time-bound or it doesn't count.
- **Sizing without horizon.** "2% NAV starter" is meaningless without "evaluated at 12 weeks." Say when you'll re-grade.
- **Pretending a hedge is a directional bet.** If §6 ASYMMETRY ratio is ≤1:1, the thesis is a hedge. Frame it as one explicitly, including a written "what's it hedging" line.
- **Chat render skipping the WHY line.** The 5-line format is tight; the temptation is to drop the mechanism. Don't. Pure CLAIM + KILL + ASYM is just a trade alert; you're aiming for analysis someone can challenge.
