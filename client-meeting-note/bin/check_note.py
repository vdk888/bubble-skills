#!/usr/bin/env python3
"""Mechanical check of a client meeting note: structure and forbidden wording.

Usage: check_note.py <note.md>   Exit 0 = pass, 1 = problems, 2 = usage/IO error.
Standard library only, no network.
"""
import re
import sys

REQUIRED = ["Objectives", "Situation", "Next steps", "Open questions", "Review checklist"]
FORBIDDEN = [
    (r"\bwe (recommend|advise)\b|\bi (recommend|advise)\b|\byou (must|need to) (buy|sell|invest)\b|\bvous devriez\b|\bnous vous conseillons\b|\bnous recommandons\b|\bje recommande\b", "recommendation wording"),
    (r"\byou should (buy|sell|invest|switch|move)\b|\bil faut (acheter|vendre|investir)\b", "investment advice wording"),
    (r"\bguarantee[sd]? (returns?|performance|gains?)\b|\bguaranteed returns?\b|\brendement garanti\b", "return promise"),
    (r"\b(fully|100%) compliant\b|\bconforme à la réglementation\b|\bcompliance is (ensured|guaranteed)\b|\bensures? compliance\b", "compliance promise"),
]


def check(text):
    problems = []
    lines = text.splitlines()
    banner = next((i for i, l in enumerate(lines[:5]) if l.lstrip("> *").strip().upper().startswith("DRAFT")), None)
    if banner is None or "not investment advice" not in lines[banner].lower():
        problems.append("missing DRAFT banner (with 'Not investment advice') in the first lines")
    heads = [m.group(1).strip().lower() for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.M)]
    for r in REQUIRED:
        if not any(h.startswith(r.lower()) for h in heads):
            problems.append(f"missing section: {r}")
    for pat, label in FORBIDDEN:
        for n, line in enumerate(lines, 1):
            if n - 1 == banner:
                continue  # the banner itself
            if re.search(pat, line, re.I):
                problems.append(f"line {n}: {label}")
    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    problems = check(text)
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("OK: structure and wording checks passed (not a review)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
