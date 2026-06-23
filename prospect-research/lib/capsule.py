"""
Capsule helpers — pure Python, stdlib only.

Used by the `prospect-research` skill. SKILL.md provides the natural-language
workflow; this module provides deterministic, testable rendering primitives so
the Markdown output is reproducible across runs.

Public API
----------
render_capsule(research_input, template_path=None) -> str
    Render a Research Capsule from a research_input dict + the Markdown template.
    String-based substitution with `.replace()`. No Jinja dependency.

write_capsule_file(slug, content, vault_dir) -> Path
    Write `{vault_dir}/Capsules/{slug}.md`. Idempotent overwrite.

compute_notes_projection(research_input, max_len=200) -> str
    Build a short ≤200-char summary suitable for a CRM notes field.

append_interaction_line(capsule_path, line) -> None
    Append a bullet under the "Interaction history" section, no duplication.

Design constraints
------------------
- Stdlib only (pathlib, re). No external dependencies.
- Defensive: missing optional fields render gracefully ("To enrich.") rather
  than producing literal "{placeholder}" tokens or crashing.
- Audience-agnostic: all template strings live in capsule-template.md, not here.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

# Default template path (relative to this file's location).
_DEFAULT_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "templates" / "capsule-template.md"
)

# Placeholder default — used when an optional field is missing or empty.
_PLACEHOLDER = "To enrich."

# Required keys in the research_input dict — render_capsule raises KeyError
# on any of these. Optional keys default to _PLACEHOLDER.
_REQUIRED_KEYS = (
    "slug",
    "display_name",
    "company",
    "role",
    "workflow_pain",
    "executive_summary",
    "angles",
    "angle_recommended",
    "angle_reason",
    "action",
    "action_reason",
    "iso_date",
    "iso_timestamp",
)

_OPTIONAL_STRINGS = ("parcours_anterieur", "mutuel")


def render_capsule(
    research_input: dict,
    template_path: Optional[Path] = None,
) -> str:
    """Render the Research Capsule Markdown for a single prospect.

    Parameters
    ----------
    research_input : dict
        Keys — see _REQUIRED_KEYS + _OPTIONAL_STRINGS:
          - slug, display_name, company, role
          - parcours_anterieur (optional), mutuel (optional)
          - workflow_pain, executive_summary
          - signals (list[str]) — rendered as Markdown bullet lines
          - angles (dict with V1/V2/V3 → str)
          - angle_recommended ("V1"|"V2"|"V3"), angle_reason
          - tier (1|2|3 or None), action (str), action_reason
          - iso_date (YYYY-MM-DD), iso_timestamp (ISO 8601)

    template_path : Path | None
        Defaults to templates/capsule-template.md relative to this file.

    Returns
    -------
    str
        Rendered Markdown with all {placeholders} substituted.
    """
    missing = [k for k in _REQUIRED_KEYS if k not in research_input]
    if missing:
        raise KeyError(f"render_capsule: research_input missing required keys: {missing!r}")

    tpl_path = template_path or _DEFAULT_TEMPLATE
    template = Path(tpl_path).read_text(encoding="utf-8")

    # Signals: list → Markdown bullets, or fallback.
    signals = research_input.get("signals") or []
    if signals:
        signals_block = "\n".join(f"- {s}" for s in signals)
    else:
        signals_block = _PLACEHOLDER

    angles = research_input.get("angles") or {}

    def _opt(key: str) -> str:
        v = research_input.get(key)
        return v if (v and str(v).strip()) else _PLACEHOLDER

    # Tier — accept int, str, or None.
    tier_raw = research_input.get("tier")
    if tier_raw in (None, ""):
        tier_str = "to be determined"
    else:
        tier_str = str(tier_raw)

    substitutions = {
        "{display_name}": str(research_input["display_name"]),
        "{company}": str(research_input["company"]),
        "{iso_date}": str(research_input["iso_date"]),
        "{slug}": str(research_input["slug"]),
        "{executive_summary}": str(research_input["executive_summary"]).strip(),
        "{role}": str(research_input["role"]),
        "{parcours_anterieur}": _opt("parcours_anterieur"),
        "{mutuel}": _opt("mutuel"),
        "{workflow_pain}": str(research_input["workflow_pain"]).strip(),
        "{signals_block}": signals_block,
        "{angle_V1}": str(angles.get("V1", _PLACEHOLDER)).strip(),
        "{angle_V2}": str(angles.get("V2", _PLACEHOLDER)).strip(),
        "{angle_V3}": str(angles.get("V3", _PLACEHOLDER)).strip(),
        "{angle_recommended}": str(research_input["angle_recommended"]),
        "{angle_reason}": str(research_input["angle_reason"]).strip(),
        "{tier}": tier_str,
        "{action}": str(research_input["action"]),
        "{action_reason}": str(research_input["action_reason"]).strip(),
        "{iso_timestamp}": str(research_input["iso_timestamp"]),
    }

    out = template
    for placeholder, value in substitutions.items():
        out = out.replace(placeholder, value)
    return out


def write_capsule_file(slug: str, content: str, vault_dir: Path) -> Path:
    """Write capsule content to `{vault_dir}/Capsules/{slug}.md`.

    Idempotent: overwrites cleanly if the file already exists.
    Creates the Capsules/ subdirectory if it does not exist.

    Returns the resolved Path of the written file.
    """
    vault_dir = Path(vault_dir).expanduser()
    capsules_dir = vault_dir / "Capsules"
    capsules_dir.mkdir(parents=True, exist_ok=True)
    out = capsules_dir / f"{slug}.md"
    out.write_text(content, encoding="utf-8")
    return out


def compute_notes_projection(research_input: dict, max_len: int = 200) -> str:
    """Build a short CRM notes projection from the research_input dict.

    Format:
        {role} at {company}. Pain: {workflow_pain truncated}. Recommended angle: {V1|V2|V3}.

    Guarantees:
      - Length ≤ max_len characters (default 200).
      - ≤ 3 lines.
      - Contains role + company + recommended angle for at-a-glance scanning.
    """
    role = str(research_input.get("role", "")).strip()
    company = str(research_input.get("company", "")).strip()
    pain = str(research_input.get("workflow_pain", "")).strip()
    angle = str(research_input.get("angle_recommended", "")).strip()

    # Collapse multi-line pain descriptions to a single line.
    pain_one_line = re.sub(r"\s+", " ", pain)

    # Avoid duplicating company name if role already includes it.
    if company and company.lower() in role.lower():
        head = f"{role}."
    else:
        head = f"{role} at {company}."

    angle_suffix = f" Recommended angle: {angle}." if angle else ""
    fixed = len(head) + len(" Pain: ") + len(".") + len(angle_suffix)
    remaining = max_len - fixed

    if remaining < 10:
        candidate = (head + angle_suffix).strip()
    else:
        pain_trim = pain_one_line[:remaining].rstrip()
        if len(pain_one_line) > remaining and " " in pain_trim:
            pain_trim = pain_trim[: pain_trim.rfind(" ")].rstrip()
        pain_trim = pain_trim.rstrip(" .,;:")
        candidate = f"{head} Pain: {pain_trim}.{angle_suffix}"

    if len(candidate) > max_len:
        candidate = candidate[: max_len - 1].rstrip() + "…"

    return candidate


def append_interaction_line(capsule_path: Path, line: str) -> None:
    """Append a bullet line under the 'Interaction history' section.

    Idempotent: if the exact `line` already exists anywhere in the file,
    this is a no-op (no duplication). Otherwise the line is appended at
    the end of the file (which is, by template convention, inside the
    Interaction history block).
    """
    capsule_path = Path(capsule_path)
    content = capsule_path.read_text(encoding="utf-8")
    if line in content:
        return  # already there — no-op
    if not content.endswith("\n"):
        content += "\n"
    content += line + "\n"
    capsule_path.write_text(content, encoding="utf-8")
