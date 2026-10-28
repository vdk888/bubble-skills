#!/usr/bin/env python3
"""Mechanical check of a missing-documents draft: sections, item lists, wording, no send.

Usage: check_relance.py [--structure-only] [--liste <liste-pieces.txt>] <brouillon.md>
Exit 0 = pass, 1 = problems, 2 = usage/IO error. Standard library only, no network.
With --liste, every item of the firm's checklist must appear exactly once, as
found, to check or missing, and no other item may appear. Every file named in
the found / to-check lists must match the Correspondance table. File names (`...`)
are not scanned for wording.
"""
import re
import sys

REQUIRED = ["Correspondance fichiers", "Pièces trouvées", "À vérifier", "Pièces manquantes",
            "Fichiers non rattachés", "Projet de mail de relance", "Limites", "Relecture"]
ITEM_SECTIONS = {"Pièces trouvées": "found", "À vérifier": "to check", "Pièces manquantes": "missing"}
NONE_MISSING = "aucune pièce manquante d'après les noms de fichiers"
FORBIDDEN = [
    (r"\b(in)?compl(et|ète|ets|ètes)\b|\b(in)?complete\b", "verdict wording (complet)"),
    (r"\bconformes?\b|\bconformité\b|\bcompliant\b", "verdict wording (conforme)"),
    (r"\bvalidée?s?\b|\bapprouvée?s?\b|\bdossier (accepté|ok|en ordre|bon)\b|\ben règle\b|\bvalidated\b|\bapproved\b",
     "verdict wording (validé)"),
    (r"\btout est (en ordre|là|bon|ok)\b|\brien ne manque\b|\bil ne manque (rien|aucune)\b|\bexhausti(f|ve)\b|\bnothing (is )?missing\b",
     "verdict wording (nothing missing)"),
    (r"\bidentité (est |a été )?(vérifiée|confirmée|contrôlée|établie)\b|\bauthentiques?\b|\bauthentifiée?s?\b|\b(pièces?|documents?) (sont |est )?vérifiée?s?\b",
     "identity or authenticity claim"),
    (r"\b(a|ont) été (envoyée?s?|transmise?s?)\b|\b(mail|e-mail|courriel|message) envoyé\b|\benvoi effectué\b|\b(j'ai|nous avons) envoyé\b|\bsent\b",
     "send claim"),
]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def labels_of(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and ":" in line:
                out.append(line.partition(":")[0].strip())
    return out


def sections(text):
    parts = re.split(r"^##\s+(.*)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def section(secs, name):
    return next((body for head, body in secs if head.lower().startswith(name.lower())), None)


def bullets(body):
    return [l.strip() for l in body.splitlines() if re.match(r"\s*-\s+(?!\[)", l)]


def check_lists(text, secs, liste, problems):
    if "YYYY-MM-DD" in text:
        problems.append("unfilled template: 'YYYY-MM-DD' left")
    corr = section(secs, "Correspondance fichiers") or ""
    rows = [l for l in corr.splitlines() if l.startswith("|") and not re.match(r"\|\s*-+", l)][1:]
    if not rows:
        problems.append("Correspondance: no file row (one row per file, or '(dossier vide)')")
    table = {}  # file name -> (items, matched by name without doubt)
    for r in rows:
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", r)[1:-1]]
        if len(cells) == 4 and cells[0].startswith("`"):
            name = cells[0].replace("\\|", "|").strip("`")
            table[name] = ({x.strip() for x in cells[1].split(" ; ")}, cells[2] == "par le nom")
    seen = {}
    for name, status in ITEM_SECTIONS.items():
        body = section(secs, name)
        if body is None:
            continue
        items = bullets(body)
        if not items:
            ok = NONE_MISSING if status == "missing" else "aucune."
            if ok not in body.lower():
                problems.append(f"{name}: no item and no '{ok}' line")
        for b in items:
            m = re.match(r"-\s+\*\*(.+?)\*\*", b)
            if not m:
                problems.append(f"{name}: item without a **libellé**: {b[:50]}")
                continue
            if status != "missing" and "`" not in b:
                problems.append(f"{name}: '{m.group(1)}' does not name the matched file")
            for f in re.findall(r"`([^`]*)`", b):
                items, sure = table.get(f, (set(), False))
                if m.group(1).strip() not in items or (status == "found" and not sure):
                    problems.append(f"{name}: '{m.group(1)}' with `{f}` does not match the Correspondance table")
            seen.setdefault(m.group(1).strip(), []).append(status)
    for label, where in seen.items():
        if len(where) > 1:
            problems.append(f"item '{label}' listed more than once ({', '.join(where)})")
    mail = section(secs, "Projet de mail de relance") or ""
    if not re.search(r"^\s*Objet\s*:", mail, re.M):
        problems.append("Projet de mail de relance: missing 'Objet :' line")
    for label, where in seen.items():
        if "missing" in where and label.lower() not in mail.lower():
            problems.append(f"missing item '{label}' is not in the reminder email")
    if liste:
        for label in liste:
            if label not in seen:
                problems.append(f"checklist item '{label}' is in no list (found, to check or missing)")
        for label in seen:
            if label not in liste:
                problems.append(f"item '{label}' is not in the firm's checklist")


def check(text, structure_only=False, liste=None):
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
    for word in ("identité", "lcb-ft"):
        if word not in limits:
            problems.append(f"Limites: must say the draft does not check '{word}'")
    if not structure_only:
        check_lists(text, secs, liste, problems)
    for n, line in enumerate(lines, 1):
        if n - 1 == banner:
            continue
        bare = re.sub(r"`[^`]*`", "", line)  # file names are shown as they are
        if EMAIL.search(bare):
            problems.append(f"line {n}: e-mail address (no addressing, no client data)")
        for pat, label in FORBIDDEN:
            if re.search(pat, bare, re.I):
                problems.append(f"line {n}: {label}")
    return problems


def main(argv):
    args = argv[1:]
    structure_only = "--structure-only" in args
    args = [a for a in args if a != "--structure-only"]
    liste = None
    try:
        if "--liste" in args:
            i = args.index("--liste")
            liste = labels_of(args[i + 1])
            del args[i:i + 2]
        if len(args) != 1:
            raise IndexError
    except IndexError:
        print(__doc__, file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    problems = check(text, structure_only, liste)
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("OK: sections, lists and wording checks passed (not a review, not a completeness verdict)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
