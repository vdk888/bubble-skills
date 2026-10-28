#!/usr/bin/env python3
"""Compare the file names of a client folder with the firm's list of documents.

Usage:
  match_documents.py --liste <liste-pieces.txt> --dossier <dossier_client>
  match_documents.py --liste <liste-pieces.txt> --fichiers <listing.txt>

Prints, in French Markdown, the sections of the draft: which file matched which
item (and with which keyword), items found, items to check, items missing, files
not matched. Reads file NAMES and sizes only, never the content of a file.
Exit 0 = ok, 2 = usage/IO error, 3 = invalid checklist. Standard library only, no network.

Checklist format, one item per line: « libellé : mot-clé, mot-clé, ... ».
Lines starting with # are comments. A keyword matches when all its words appear
in the file name (accents, case and separators ignored).
"""
import os
import re
import sys
import unicodedata


def words(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).split()


def load_checklist(path):
    items, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            label, sep, kws = line.partition(":")
            label = label.strip()
            kws = [words(k) for k in kws.split(",")]
            kws = [k for k in kws if k]
            if not sep or not label or not kws:
                raise ValueError(f"line {n}: expected 'libellé : mot-clé, mot-clé'")
            if label.lower() in seen:
                raise ValueError(f"line {n}: duplicate item '{label}'")
            seen.add(label.lower())
            items.append((label, kws))
    if not items:
        raise ValueError("no item in the checklist")
    return items


def list_folder(root):
    files = []
    for d, dirs, names in os.walk(root):
        dirs[:] = sorted(x for x in dirs if not x.startswith("."))
        for name in sorted(names):
            if name.startswith("."):
                continue
            p = os.path.join(d, name)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            files.append((os.path.relpath(p, root), os.path.getsize(p)))
    return files


def list_file(path):
    with open(path, encoding="utf-8") as f:
        return [(l.strip(), None) for l in f if l.strip() and not l.lstrip().startswith("#")]


def match(items, files):
    """Return per-file rows and per-item results."""
    rows = []
    found = {label: [] for label, _ in items}
    doubt = {label: [] for label, _ in items}
    for name, size in files:
        toks = words(os.path.splitext(name)[0])
        joined = "".join(toks)
        sure, partial = [], []
        for label, kws in items:
            kw = next((k for k in kws if all(t in toks for t in k)), None)
            if kw:
                sure.append((label, kw))
                continue
            kw = next((k for k in kws if all(t in joined for t in k)), None)
            if kw:
                partial.append((label, kw))
        if len(sure) == 1 and size != 0:
            hits, reason = sure, None
            found[sure[0][0]].append((name, sure[0][1]))
        elif sure:
            hits = sure
            reason = "fichier vide (0 octet)" if len(sure) == 1 else "le nom correspond à plusieurs pièces"
        elif partial:
            hits, reason = partial, "mot-clé trouvé seulement à l'intérieur d'un mot du nom"
        else:
            hits, reason = [], None
        if reason:
            for label, kw in hits:
                doubt[label].append((name, kw, reason))
        rows.append((name, hits, reason))
    return rows, found, doubt


def code(name):
    return "`" + name.replace("`", "'") + "`"


def kwtext(kw):
    return "« " + " ".join(kw) + " »"


def render(items, rows, found, doubt):
    out = ["## Correspondance fichiers / pièces", "",
           "D'après les noms de fichiers uniquement : aucun fichier n'a été ouvert.", "",
           "| Fichier | Pièce de la liste | Correspondance | Mot-clé |",
           "|---------|-------------------|----------------|---------|"]
    for name, hits, reason in rows:
        cell = code(name).replace("|", "\\|")
        if not hits:
            out.append(f"| {cell} | — | aucune | — |")
        else:
            status = "à vérifier : " + reason if reason else "par le nom"
            out.append(f"| {cell} | {' ; '.join(l for l, _ in hits)} | {status} | "
                       f"{', '.join(kwtext(k) for _, k in hits)} |")
    if not rows:
        out.append("| (dossier vide) | — | — | — |")
    labels = [label for label, _ in items]
    present = [l for l in labels if found[l]]
    check = [l for l in labels if not found[l] and doubt[l]]
    missing = [l for l in labels if not found[l] and not doubt[l]]
    out += ["", "## Pièces trouvées (d'après le nom du fichier)", ""]
    for l in present:
        out.append(f"- **{l}** — " + ", ".join(f"{code(n)} (mot-clé {kwtext(k)})" for n, k in found[l]))
    if not present:
        out.append("Aucune.")
    out += ["", "## À vérifier", ""]
    for l in check:
        out.append(f"- **{l}** — " + " ; ".join(f"{code(n)} : {r} (mot-clé {kwtext(k)})" for n, k, r in doubt[l]))
    if not check:
        out.append("Aucune.")
    out += ["", "## Pièces manquantes", ""]
    for l in missing:
        out.append(f"- **{l}**")
    if not missing:
        out.append("Aucune pièce manquante d'après les noms de fichiers ; le contenu des fichiers reste à ouvrir et à contrôler.")
    loose = [name for name, hits, _ in rows if not hits]
    out += ["", "## Fichiers non rattachés", ""]
    out += [f"- {code(n)}" for n in loose] or ["Aucun."]
    summary = (f"{len(labels)} pièces : {len(present)} trouvées, {len(check)} à vérifier, "
               f"{len(missing)} manquantes ; {len(loose)} fichier(s) non rattaché(s)")
    return "\n".join(out) + "\n", summary


def main(argv):
    args = argv[1:]
    opts = dict(zip(args[::2], args[1::2]))
    if len(args) != 4 or "--liste" not in opts or len({"--dossier", "--fichiers"} & set(opts)) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        items = load_checklist(opts["--liste"])
    except ValueError as e:
        print(f"checklist error: {e}", file=sys.stderr)
        return 3
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    try:
        if "--dossier" in opts:
            if not os.path.isdir(opts["--dossier"]):
                raise OSError(f"not a folder: {opts['--dossier']}")
            files = list_folder(opts["--dossier"])
        else:
            files = list_file(opts["--fichiers"])
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    text, summary = render(items, *match(items, files))
    sys.stdout.write(text)
    print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
