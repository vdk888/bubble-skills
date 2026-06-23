"""
Example research_input dict for prospect-research.

Replace the values below with real data from your research session.
Pass this dict to render_capsule() from lib/capsule.py.

All fields marked "(optional)" default to "To enrich." if omitted.
"""

RESEARCH_INPUT = {
    # ---- Identity --------------------------------------------------------
    "slug": "jane-smith-acme",                     # stable kebab-case ID
    "display_name": "Jane Smith",                   # display name for the capsule header
    "company": "Acme Corp",
    "role": "Head of Operations at Acme Corp",

    # ---- Background (optional) -------------------------------------------
    "parcours_anterieur": (                         # prior roles / career path
        "10 years at GlobalCo as Operations Manager before joining Acme in 2023."
    ),
    "mutuel": (                                     # mutual contacts or prior interactions
        "Introduced by Alex Chen (shared connection on LinkedIn)."
        # Leave as None or omit if no mutual exists.
    ),

    # ---- Research core ---------------------------------------------------
    "executive_summary": (
        "Head of Operations at Acme Corp (joined 2023 from GlobalCo). "
        "Manages a 15-person ops team, heavy reliance on manual reporting. "
        "Strong ICP fit — workflow pain is the daily reconciliation step."
    ),
    "workflow_pain": (
        "Daily reconciliation of three data sources (ERP, CRM, spreadsheets) "
        "done manually by two analysts. Estimated 3–4 hours per day. "
        "No automated handoff between systems; copy-paste is the integration."
    ),
    "signals": [
        "Posted on LinkedIn about 'ops bottlenecks in scaling teams' (2 weeks ago).",
        "Acme recently announced a Series B ($20M) — growth phase likely = more ops pressure.",
        "Hiring for a second Data Analyst (LinkedIn job posting, active).",
    ],

    # ---- Angles ----------------------------------------------------------
    "angles": {
        "V1": (
            "The 3-hour daily reconciliation is the exact problem our agent solves — "
            "automated end-to-end, no copy-paste, your analysts focus on exceptions not data entry."
        ),
        "V2": (
            "Ops-to-ops: we've seen this same bottleneck at every company crossing 100 employees. "
            "Happy to share what the breakpoint usually looks like and how others solved it."
        ),
        "V3": (
            "With the Series B fresh, this is exactly the moment to decide whether the ops "
            "stack scales with the company or becomes the bottleneck that caps growth."
        ),
    },
    "angle_recommended": "V1",
    "angle_reason": (
        "The LinkedIn post signals she's actively thinking about this pain — V1 is a direct "
        "rebound on something she already articulated publicly."
    ),

    # ---- Action ----------------------------------------------------------
    "tier": 1,              # 1 = strong ICP fit, 2 = partial fit, 3 = weak / skip
    "action": "draft-outreach",
    "action_reason": (
        "Tier 1 fit, active signal (post + hiring), warm intro path available. "
        "Draft a short outreach message using angle V1."
    ),

    # ---- Timestamps (ISO 8601) -------------------------------------------
    "iso_date": "2026-06-23",
    "iso_timestamp": "2026-06-23T09:00:00+00:00",
}
