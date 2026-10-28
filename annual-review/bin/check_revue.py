#!/usr/bin/env python3
"""Mechanical check of an annual-review draft: sections, rule, lists, invitations, wording, no send.

Usage: check_revue.py [--structure-only] <brouillon.md>
Exit 0 = pass, 1 = problems, 2 = usage/IO error. Standard library only, no network.
Every client of the « Clients retenus » table must be in exactly one list (due,
late, to check), with the same list and the same date read, and every listed
client must be in the table. Every due or late client has one invitation
(« ### référence »); clients to check have none.
"""
import re
import sys

REQUIRED = ["Règle appliquée", "Clients retenus", "Revues dues", "Revues en retard", "À vérifier",
            "Ordre du jour", "Invitations", "Limites", "Relecture"]
LISTS = {"Revues dues": "due", "Revues en retard": "late", "À vérifier": "check"}
EMPTY = {"due": "aucune revue due", "late": "aucune revue en retard", "check": "aucune ligne à vérifier"}
FORBIDDEN = [
    (r"\brecommand\w*|\b(nous vous|je vous) conseill\w*|\bconseil(lons|lé) d[e']|\barbitr(age|er|ez)\b|\brendements?\b|\bgaranti(e|s|es)?\b|\brecommend\w*",
     "advice wording"),
    (r"\bconformes?\b|\bconformité\b|\ben règle\b|\bcompliant\b", "compliance wording"),
    (r"\bexhausti(f|ve)\b|\baucun oubli\b|\btous les clients (sont )?à jour\b|\bliste (complète|certaine)\b",
     "verdict wording (exhaustive list)"),
    (r"\b(a|ont) été (envoyée?s?|transmise?s?)\b|\b(mail|e-mail|courriel|invitation|message)s? envoyée?s?\b|\benvoi effectué\b|\b(j'ai|nous avons) envoyé\b|\bsent\b",
     "send claim"),
]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def sections(text, level="##"):
    parts = re.split(rf"^{level}\s+(.*)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def section(secs, name):
    return next((body for head, body in secs if head.lower().startswith(name.lower())), None)


def bullets(body):
    return [l.strip() for l in body.splitlines() if re.match(r"\s*-\s+(?!\[)", l)]


def check_lists(text, secs, delay, problems):
    if "YYYY-MM-DD" in text:
        problems.append("unfilled template: 'YYYY-MM-DD' left")
    body = section(secs, "Clients retenus") or ""
    rows = [l for l in body.splitlines() if l.startswith("|") and not re.match(r"\|\s*-+", l)][1:]
    if not rows:
        problems.append("Clients retenus: no row (one row per listed client, or '(aucun client retenu)')")
    table = {}
    for r in rows:
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r)[1:-1]]
        if len(cells) != 5:
            problems.append(f"Clients retenus: row without 5 cells: {r[:50]}")
            continue
        if cells[0].startswith("("):
            continue
        st = next((s for p, s in (("due", "due"), ("en retard", "late"), ("à vérifier", "check"))
                   if cells[4].lower().startswith(p)), None)
        if st is None:
            problems.append(f"Clients retenus: '{cells[0]}' has an unknown list '{cells[4]}'")
        if cells[0] in table:
            problems.append(f"Clients retenus: '{cells[0]}' appears twice")
        table[cells[0]] = (st, cells[1])
    seen = {}
    for name, status in LISTS.items():
        body = section(secs, name)
        if body is None:
            continue
        items = bullets(body)
        if not items and EMPTY[status] not in body.lower():
            problems.append(f"{name}: no client and no '{EMPTY[status]} ...' line")
        for b in items:
            m = re.match(r"-\s+\*\*(.+?)\*\*\s+—\s+date lue (« [^»]* »|\(vide\))", b)
            if not m:
                problems.append(f"{name}: item without '**client** — date lue « ... »': {b[:60]}")
                continue
            label, read = m.group(1).strip(), m.group(2)
            seen.setdefault(label, []).append(status)
            if status in ("due", "late") and not re.search(rf"échéance \d{{4}}-\d{{2}}-\d{{2}} \(dernière revue \+ {delay} mois\)", b):
                problems.append(f"{name}: '{label}' does not show its due date and the rule (+ {delay} mois)")
            if status == "check" and ";" not in b:
                problems.append(f"{name}: '{label}' does not say why it is to check")
            if label not in table:
                problems.append(f"{name}: '{label}' is not in the Clients retenus table")
            elif table[label] != (status, read):
                problems.append(f"{name}: '{label}' differs from the Clients retenus table (list or date read)")
    for label, where in seen.items():
        if len(where) > 1:
            problems.append(f"client '{label}' listed more than once ({', '.join(where)})")
    for label in table:
        if label not in seen:
            problems.append(f"Clients retenus: '{label}' is in no list")
    inv = sections(section(secs, "Invitations") or "", "###")
    invited = [h for h, _ in inv]
    wanted = [l for l, w in seen.items() if set(w) & {"due", "late"}]
    for label in wanted:
        if invited.count(label) != 1:
            problems.append(f"Invitations: '{label}' needs exactly one invitation (### {label})")
    for h, b in inv:
        if h not in wanted:
            problems.append(f"Invitations: '{h}' is not a due or late client")
        if not re.search(r"^\s*Objet\s*:", b, re.M) or "Bonjour," not in b:
            problems.append(f"Invitations: '{h}' has no 'Objet :' or 'Bonjour,' line")


def check(text, structure_only=False):
    problems = []
    lines = text.splitlines()
    banner = next((i for i, l in enumerate(lines[:5]) if l.lstrip("> *").strip().upper().startswith("BROUILLON")), None)
    if banner is None or "aucun envoi" not in lines[banner].lower():
        problems.append("missing BROUILLON banner (with 'Aucun envoi') in the first lines")
    secs = sections(text)
    for r in REQUIRED:
        if section(secs, r) is None:
            problems.append(f"missing section: {r}")
    limits = (section(secs, "Limites") or "").lower()
    for word in ("date fausse", "aucun conseil"):
        if word not in limits:
            problems.append(f"Limites: must contain '{word}'")
    if not structure_only:
        rule = section(secs, "Règle appliquée") or ""
        m = re.search(r"dernière revue \+ (\d+) mois", rule)
        if not m or "Mois examiné" not in rule:
            problems.append("Règle appliquée: must state 'dernière revue + N mois' and the 'Mois examiné'")
        check_lists(text, secs, m.group(1) if m else r"\d+", problems)
    for n, line in enumerate(lines, 1):
        if n - 1 == banner:
            continue
        if EMAIL.search(line):
            problems.append(f"line {n}: e-mail address (no addressing, no client data)")
        for pat, label in FORBIDDEN:
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
        print("OK: sections, lists and wording checks passed (not a review of the dates)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
