---
name: missing-documents
description: For a wealth-management firm (CGP), compare the file names in a client folder with the firm's own list of required documents, show which file matched which item, list what is present, what is uncertain and what is missing, and draft a reminder email in French for the missing items. Runs on the firm's machine, reads file names only, writes a local Markdown file, never sends anything. Use when an adviser wants to know which documents a client still has to send. Checks completeness by file name only, never identity or authenticity; not an LCB-FT / KYC control.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: true
allowed-tools:
  - Bash(python3 *match_documents.py*)
  - Bash(python3 *check_relance.py*)
  - Read
  - Write
---

# missing-documents — pièces manquantes du dossier client

> **Draft only. L'outil prépare, vous validez.** The skill compares file NAMES with the firm's list. It does not open the files, does not check the client's identity, nor that a document is authentic, readable, signed or still valid, and it never replaces the firm's LCB-FT / KYC control. It never gives a verdict on the folder: no « complet », no « conforme », no « dossier validé ». It always shows the list of what was found, what is to check and what is missing.

## What it does

1. Reads the firm's checklist, a plain text file the firm edits (`liste-pieces.txt`, one item per line: `libellé : mot-clé, mot-clé`).
2. Lists the file names in the client folder (or reads a file listing), without opening any file.
3. Matches names to items with `bin/match_documents.py`, deterministic and transparent: every file is shown with the item it matched and the keyword that matched. A match is « à vérifier » when a name fits several items, when the keyword is only found inside a word (`impot` in `impots`, `rib` in `attribution`), or when the file is empty.
4. Writes ONE local Markdown draft in French from `template.md`: the matching table, the found / to check / missing lists, the files not matched, a reminder email listing the missing items, the limits, and a review checklist for the adviser.

## Rules (non-negotiable)

- Everything stays on this machine. No upload, no web, no email, no messaging, no CRM write. Never send the reminder: it is a draft the adviser copies into their own mail tool after review.
- Never open, read, OCR or summarise the content of client files. File names and sizes only.
- No client name in the draft: the header uses the firm's internal reference, the email starts with « Bonjour, » and has no address. File names are shown as they are, because the adviser needs them; the draft stays local, next to (not inside) the client folder or where the adviser says. Do not commit it, copy it elsewhere, or keep client data in memory files or logs.
- Write in French. Paste the sections produced by `match_documents.py` unchanged: do not move an item from « À vérifier » or « Pièces manquantes » to « Pièces trouvées » on your own judgement. If the adviser has opened a file and decides, they edit the draft themselves (or tell you to, and you say it was their decision).
- Never write a verdict on the folder or on a document: no « complet », « conforme », « validé », « en règle », « rien ne manque », « identité vérifiée », « authentique ». When nothing is missing, keep the script's line: « Aucune pièce manquante d'après les noms de fichiers ; le contenu des fichiers reste à ouvrir et à contrôler. »
- The email lists only the « Pièces manquantes », with their exact labels. Items « À vérifier » go in only if the adviser decides so after opening the files.

## Steps

1. **Inputs.** Ask for the client folder path (or a file listing, one name per line), the firm's checklist (default: `${CLAUDE_SKILL_DIR}/liste-pieces.txt`, a starting point the firm should copy and adapt), and an internal reference for the folder (never the client's name).
2. **Match.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/match_documents.py --liste <liste.txt> --dossier <dossier>` (or `--fichiers <listing.txt>`). It prints the Markdown sections on stdout and a count on stderr. Exit 3 means the checklist has a malformed line: show it to the adviser, do not guess.
3. **Draft** with `${CLAUDE_SKILL_DIR}/template.md`: fill the header, paste the script's sections unchanged, write the reminder email (one line per missing item, polite, neutral, no deadline the adviser did not give, no name, no address), keep the « Limites » and « Relecture » sections.
4. **Check.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/check_relance.py --liste <liste.txt> <brouillon.md>`. It checks the banner, the sections, that every checklist item is in exactly one list, that found and to-check items name their file, that every missing item is in the email, the limits wording, and forbidden wording (verdicts, identity claims, send claims, e-mail addresses). Exit 0 = pass, 1 = fix and rerun. It is a mechanical aid, not a review and not a completeness verdict.
5. **Hand over.** Tell the adviser where the file is, how many items are found / to check / missing, which files are not matched, and that it is a draft: they open the files, decide the « À vérifier » points and send the email themselves if they choose. Stop.

## Files

- `liste-pieces.txt` — a starting checklist (French), for the firm to copy and adapt.
- `template.md` — the draft skeleton (French).
- `bin/match_documents.py` — file-name matching (Python 3 standard library, no network, never opens files).
- `bin/check_relance.py` — structure, lists and wording check (standard library, no network).
- `examples/` — a fictional file listing and the draft produced from it with `liste-pieces.txt`.
- `tests/run.sh` — test suite (offline).

## Limits

Matching works on names only: a well-named wrong document counts as « trouvée », a badly named right one shows as missing (and in « Fichiers non rattachés »). Validity periods (« de moins de 3 mois »), signatures and expiry dates are not checked. The skill checks completeness against the firm's list, not the client's identity or the authenticity of documents, and it is not the firm's LCB-FT / KYC control. It gives no assurance about regulatory compliance.
