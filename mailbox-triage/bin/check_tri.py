#!/usr/bin/env python3
"""Mechanical check of a mailbox triage draft and of its reply drafts: sections, lists, wording, no send.

Usage: check_tri.py [--structure-only] [--brouillons <dossier>] <tri.md>
Exit 0 = pass, 1 = problems, 2 = usage/IO error. Standard library only, no network.
Every message of the « Tri du courrier » table must be in exactly one list
(« Réponses à préparer » or « Sans brouillon ») with the same category and
urgency. Information and vigilance messages have no draft. With --brouillons,
every message to answer has exactly one completed draft file Mnn-reponse.md in
the folder, and no other draft is there.
"""
import os
import re
import sys

REQUIRED = ["Règle appliquée", "Tri du courrier", "Réponses à préparer", "Sans brouillon", "À vérifier",
            "Limites", "Relecture"]
CATEGORIES = {"Clients", "Partenaires", "Administratif", "Information", "À classer"}
URGENCIES = {"haute", "normale", "basse"}
EMPTY = {"Réponses à préparer": "aucune réponse à préparer", "Sans brouillon": "aucun message sans brouillon",
         "À vérifier": "aucun message à vérifier"}
FORBIDDEN = [
    (r"\b(je|nous) vous (recommand|conseill)\w*|\brecommandons\b|\bconseillons\b|\brecommandation\b|\brendements?\b"
     r"|\bgaranti(e|s|es)?\b|\brecommend\w*", "advice wording"),
    (r"\bconformes?\b|\bconformité\b|\ben règle\b|\bcompliant\b", "compliance wording"),
    (r"\b(a|ont) été (envoyée?s?|transmise?s?)\b|\b(mail|e-mail|courriel|réponse|message)s? envoyée?s?\b|\benvoi effectué\b"
     r"|\b(j'ai|nous avons) (envoyé|répondu)\b|\bsent\b", "send claim"),
]
EXECUTION = (r"\b(a|ont) été (effectuée?s?|exécutée?s?|réalisée?s?|validée?s?|enregistrée?s?|pris(e|es)? en compte)\b"
             r"|\bnous avons (procédé|effectué|exécuté|validé|enregistré|modifié)\b|\bc'est fait\b"
             r"|\b(virement|rachat|arbitrage|versement|modification)s? (effectuée?s?|réalisée?s?|validée?s?)\b",
             "execution claim (nothing is done before the adviser decides)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
URL = re.compile(r"\b(https?://|www\.)", re.I)
QUOTED = re.compile(r"«[^»]*»")


def sections(text, level="##"):
    parts = re.split(rf"^{level}\s+(.*)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def section(secs, name):
    return next((body for head, body in secs if head.lower().startswith(name.lower())), None)


def bullets(body):
    return [l.strip() for l in body.splitlines() if re.match(r"\s*-\s+(?!\[)", l)]


def banner_line(lines, word):
    i = next((i for i, l in enumerate(lines[:5]) if l.lstrip("> *").strip().upper().startswith(word)), None)
    return i if i is not None and "aucun envoi" in lines[i].lower() else None


def wording(lines, skip, problems, where="", execution=False):
    for n, line in enumerate(lines, 1):
        if n - 1 in skip:
            continue
        if EMAIL.search(line):
            problems.append(f"{where}line {n}: e-mail address (no addressing, no client data)")
        bare = QUOTED.sub("« »", line)
        if re.match(r"\s*Objet\s*:", bare):
            continue
        for pat, label in FORBIDDEN + ([EXECUTION] if execution else []):
            if re.search(pat, bare, re.I):
                problems.append(f"{where}line {n}: {label}")


def check_table(secs, problems):
    body = section(secs, "Tri du courrier") or ""
    rows = [l for l in body.splitlines() if l.startswith("|") and not re.match(r"\|\s*-+", l)][1:]
    if not rows:
        problems.append("Tri du courrier: no row (one row per message, or '(aucun message trié)')")
    table = {}
    for r in rows:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        if len(cells) != 9:
            problems.append(f"Tri du courrier: row without 9 cells: {r[:50]}")
            continue
        ref, _, _, _, cat, _, urg, why, draft = cells
        if ref.startswith("("):
            continue
        if not re.fullmatch(r"M\d{2,3}", ref):
            problems.append(f"Tri du courrier: bad reference '{ref}'")
            continue
        if cat not in CATEGORIES:
            problems.append(f"Tri du courrier: {ref} has an unknown category '{cat}'")
        if urg not in URGENCIES:
            problems.append(f"Tri du courrier: {ref} has an unknown urgency '{urg}'")
        if not why:
            problems.append(f"Tri du courrier: {ref} gives no reason")
        if draft not in ("non", f"{ref}-reponse.md"):
            problems.append(f"Tri du courrier: {ref} draft cell must be 'non' or '{ref}-reponse.md'")
        if draft != "non" and (cat == "Information" or "vigilance" in why):
            problems.append(f"Tri du courrier: {ref} is {'vigilance' if 'vigilance' in why else 'Information'}, no draft allowed")
        if ref in table:
            problems.append(f"Tri du courrier: {ref} appears twice")
        table[ref] = (cat, urg, draft != "non")
    return table


def check_lists(secs, table, problems):
    seen = {}
    for name, with_draft in (("Réponses à préparer", True), ("Sans brouillon", False)):
        body = section(secs, name)
        if body is None:
            continue
        items = bullets(body)
        if not items and EMPTY[name] not in body.lower():
            problems.append(f"{name}: no message and no '{EMPTY[name]} ...' line")
        for b in items:
            m = re.match(r"-\s+\*\*(M\d{2,3})\*\*\s+—\s+([^,]+), urgence (\w+) ; (.*)", b)
            if not m:
                problems.append(f"{name}: item without '**Mnn** — catégorie, urgence ... ; ...': {b[:60]}")
                continue
            ref, cat, urg, rest = m.groups()
            seen.setdefault(ref, []).append(name)
            if ref not in table:
                problems.append(f"{name}: {ref} is not in the Tri du courrier table")
                continue
            if table[ref] != (cat, urg, with_draft):
                problems.append(f"{name}: {ref} differs from the table (category, urgency or draft)")
            if with_draft and f"{ref}-reponse.md" not in rest:
                problems.append(f"{name}: {ref} does not name its draft {ref}-reponse.md")
    for ref, where in seen.items():
        if len(where) > 1:
            problems.append(f"{ref} listed more than once ({', '.join(where)})")
    for ref in table:
        if ref not in seen:
            problems.append(f"Tri du courrier: {ref} is in no list")
    return [ref for ref, (_, _, d) in table.items() if d]


def check_draft(path, ref):
    problems = []
    where = f"{os.path.basename(path)}: "
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return [f"{where}not readable ({e})"]
    lines = text.splitlines()
    banner = banner_line(lines, "BROUILLON")
    if banner is None:
        problems.append(f"{where}missing BROUILLON banner (with 'Aucun envoi') in the first lines")
    if not re.search(rf"^- \*\*Message :\*\* {ref} — ", text, re.M):
        problems.append(f"{where}'- **Message :** {ref} — ...' line missing or for another message")
    if not re.search(r"^Objet\s*:", text, re.M) or not re.search(r"^Bonjour,\s*$", text, re.M):
        problems.append(f"{where}no 'Objet :' or 'Bonjour,' line")
    if "[Réponse à rédiger]" in text:
        problems.append(f"{where}reply not written ('[Réponse à rédiger]' left)")
    body = re.search(r"^Bonjour,\s*$(.*?)^(Bien cordialement|Cordialement|Bien à vous)", text, re.M | re.S)
    if not body or not body.group(1).strip():
        problems.append(f"{where}empty reply between 'Bonjour,' and the closing")
    if not re.search(r"^## Relecture", text, re.M):
        problems.append(f"{where}missing section: Relecture")
    for n, line in enumerate(lines, 1):
        if URL.search(QUOTED.sub("« »", line)):
            problems.append(f"{where}line {n}: link (no link in a reply draft)")
    wording(lines, {banner}, problems, where, execution=True)
    return problems


def check(text, structure_only=False, drafts_dir=None):
    problems = []
    lines = text.splitlines()
    banner = banner_line(lines, "BROUILLON")
    if banner is None:
        problems.append("missing BROUILLON banner (with 'Aucun envoi') in the first lines")
    secs = sections(text)
    for r in REQUIRED:
        if section(secs, r) is None:
            problems.append(f"missing section: {r}")
    limits = (section(secs, "Limites") or "").lower()
    for word in ("pas vérifiée", "aucun conseil", "aucun message n'est envoyé"):
        if word not in limits:
            problems.append(f"Limites: must contain '{word}'")
    if not structure_only:
        if "YYYY-MM-DD" in text:
            problems.append("unfilled template: 'YYYY-MM-DD' left")
        rule = section(secs, "Règle appliquée") or ""
        if "Boîte lue :" not in rule or "L'adresse affichée n'est pas vérifiée" not in rule:
            problems.append("Règle appliquée: must name the 'Boîte lue :' and say 'L'adresse affichée n'est pas vérifiée'")
        table = check_table(secs, problems)
        to_answer = check_lists(secs, table, problems)
        if drafts_dir is not None:
            if not os.path.isdir(drafts_dir):
                problems.append(f"drafts folder not found: {drafts_dir}")
            else:
                for ref in to_answer:
                    p = os.path.join(drafts_dir, f"{ref}-reponse.md")
                    if not os.path.isfile(p):
                        problems.append(f"draft missing for {ref}: {ref}-reponse.md")
                    else:
                        problems += check_draft(p, ref)
                for name in sorted(os.listdir(drafts_dir)):
                    m = re.fullmatch(r"(M\d{2,3})-reponse\.md", name)
                    if name.endswith(".md") and (not m or m.group(1) not in to_answer):
                        problems.append(f"draft {name} is not for a message to answer")
    wording(lines, {banner}, problems)
    return problems


def main(argv):
    args = argv[1:]
    structure_only = "--structure-only" in args
    args = [a for a in args if a != "--structure-only"]
    drafts_dir = None
    if "--brouillons" in args:
        i = args.index("--brouillons")
        if i + 1 >= len(args):
            print(__doc__, file=sys.stderr)
            return 2
        drafts_dir = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    problems = check(text, structure_only, drafts_dir)
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("OK: sections, lists, drafts and wording checks passed (not a review of the replies)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
