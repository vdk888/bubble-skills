#!/usr/bin/env python3
"""Mechanical check of a weekly regulatory watch digest: structure, dates, links, wording.

Usage: check_digest.py [--structure-only] <digest.md>
Exit 0 = pass, 1 = problems, 2 = usage/IO error. Standard library only, no network.
Item titles (### lines) and links are official text and are not scanned for wording.
"""
import datetime as dt
import re
import sys
from urllib.parse import urlparse

REQUIRED = ["Publications de la semaine", "Sources consultées", "Relecture"]
SOURCES = {"amf": {"www.amf-france.org", "amf-france.org"},
           "acpr": {"acpr.banque-france.fr"}}
SOURCE_HOSTS = {"AMF": SOURCES["amf"], "ACPR": SOURCES["acpr"],
                "AMF ET ACPR": SOURCES["amf"] | SOURCES["acpr"]}
DATE = r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})"
FORBIDDEN = [
    (r"\bconformes?\b|\bcompliant\b|\b(êtes|est|sont|être) en règle\b|\bconformité (est )?(assurée|garantie)\b|\bgarantit la conformité\b", "compliance wording"),
    (r"\bnous recommandons\b|\bje recommande\b|\bnous vous conseillons\b|\bvous devriez\b|\bwe (recommend|advise)\b", "recommendation wording"),
    (r"\bil faut (acheter|vendre|investir|arbitrer|souscrire)\b|\b(achetez|vendez|investissez)\b|\byou should (buy|sell|invest)\b", "investment advice wording"),
    (r"\brendements? garantis?\b|\bguaranteed returns?\b", "return promise"),
]


def parse_date(s):
    s = s.strip()
    try:
        return dt.date.fromisoformat(s) if "-" in s else dt.datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def field(block, name):
    m = re.search(r"^\s*-\s*\*\*" + name + r"\s*:\*\*\s*(.*)$", block, re.M | re.I)
    return m.group(1).strip() if m else ""


def check_items(text, problems):
    m = re.search(r"^\s*-\s*\*\*Période :\*\*\s*du\s+" + DATE + r"\s+au\s+" + DATE, text, re.M)
    start = end = None
    if m:
        start, end = parse_date(m.group(1)), parse_date(m.group(2))
    if not start or not end:
        problems.append("missing or unreadable period: '- **Période :** du YYYY-MM-DD au YYYY-MM-DD'")
    elif not 0 <= (end - start).days <= 6:
        problems.append(f"period {start} to {end} is not within one week")
        start = end = None
    sec = re.search(r"^##\s+Publications de la semaine.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    body = sec.group(1) if sec else ""
    blocks = re.split(r"^###\s+", body, flags=re.M)[1:]
    if not blocks and "aucune publication retenue" not in body.lower():
        problems.append("no item and no 'Aucune publication retenue' line")
    for i, b in enumerate(blocks, 1):
        title = re.sub(r"^\d+\.\s*", "", b.splitlines()[0].strip())
        tag = f"item {i} ({title[:40]})"
        if not title or title.startswith("("):
            problems.append(f"{tag}: missing title")
        day = parse_date(field(b, "Date"))
        if not day:
            problems.append(f"{tag}: missing or unreadable date")
        elif start and not start <= day <= end:
            problems.append(f"{tag}: date {day} outside the period {start} to {end}")
        src = field(b, "Source").upper()
        hosts = SOURCE_HOSTS.get(src)
        if hosts is None:
            problems.append(f"{tag}: source must be AMF, ACPR or AMF et ACPR")
        url = field(b, "Lien")
        u = urlparse(url)
        if u.scheme != "https" or u.hostname not in SOURCES["amf"] | SOURCES["acpr"] or len(u.path) < 2:
            problems.append(f"{tag}: link must be an https page on amf-france.org or acpr.banque-france.fr")
        elif hosts and u.hostname not in hosts:
            problems.append(f"{tag}: link host {u.hostname} does not match source {src}")
        why = field(b, "Pourquoi c'est utile")
        if not why or why.startswith("("):
            problems.append(f"{tag}: missing 'Pourquoi c'est utile' line")


def check(text, structure_only=False):
    problems = []
    lines = text.splitlines()
    banner = next((i for i, l in enumerate(lines[:5]) if l.lstrip("> *").strip().upper().startswith("BROUILLON")), None)
    if banner is None or "pas un conseil en investissement" not in lines[banner].lower():
        problems.append("missing BROUILLON banner (with 'Pas un conseil en investissement') in the first lines")
    heads = [m.group(1).strip().lower() for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.M)]
    for r in REQUIRED:
        if not any(h.startswith(r.lower()) for h in heads):
            problems.append(f"missing section: {r}")
    if not structure_only:
        check_items(text, problems)
    for pat, label in FORBIDDEN:
        for n, line in enumerate(lines, 1):
            if n - 1 == banner or line.startswith("###") or re.match(r"\s*-\s*\*\*Lien", line):
                continue  # banner, official titles and links
            if re.search(pat, line, re.I):
                problems.append(f"line {n}: {label}")
    return problems


def main(argv):
    args = argv[1:]
    structure_only = "--structure-only" in args
    args = [a for a in args if a != "--structure-only"]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    problems = check(text, structure_only)
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("OK: structure, dates, links and wording checks passed (not a review)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
