---
name: annual-review
description: For a wealth-management firm (CGP), read the firm's client list file (CSV or XLSX, local) and list the clients due for their annual review in a given month (last review date + 12 months, configurable), the late ones and the lines whose date is missing or unreadable, showing for each the date read and the rule; then draft a meeting agenda and one invitation email in French per client due. Runs on the firm's machine, writes a local Markdown file, never sends anything. Use when an adviser prepares the month's annual reviews. Not investment advice.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: true
allowed-tools:
  - Bash(python3 *due_reviews.py*)
  - Bash(python3 *check_revue.py*)
  - Read
  - Write
---

# annual-review — préparation des revues annuelles

> **Draft only. Not investment advice. L'outil prépare, vous validez.** The skill reads two columns of the firm's client file (client reference, last review date) and applies one stated rule. A wrong date in the file gives a wrong list, so the draft shows, for every client listed, the date it read and the rule it applied, and puts every missing or unreadable date in « À vérifier ». It never says the list is exhaustive, recommends nothing to the client, and sends nothing.

## What it does

1. Reads the firm's client file, CSV (`;`, `,` or tab, UTF-8 or Windows encoding) or XLSX (read with the Python standard library, no extra package), and only two columns: the client reference and the last review date. Column names are configurable; other columns (names, addresses, amounts) are never read into the draft.
2. Applies the rule with `bin/due_reviews.py`: a review is due when last review + 12 months (`--delai-mois` to change) falls in the month examined (default: the current month). Due in an earlier month = « en retard ». Empty, unreadable, two-digit-year or future dates, empty references and references on several lines go to « À vérifier », with the value read and the reason. Dates are read as `JJ/MM/AAAA` (French order), `AAAA-MM-JJ`, or Excel date cells. An Excel number that gives a date before 1990 (for example a year typed as `2025`) is not taken as a date: it goes to « À vérifier ». An XLSX part larger than 50 MB once uncompressed (100 MB for all parts read), or one declaring a DOCTYPE, is refused with a message (export the sheet as CSV).
3. Writes ONE local Markdown draft in French from `template.md`: the rule, the table of clients listed, the three lists, a proposed agenda, one invitation per client due or late, the limits, and a review checklist for the adviser.

## Rules (non-negotiable)

- Everything stays on this machine. No upload, no web, no email, no calendar, no messaging, no CRM write. Never send an invitation: they are drafts the adviser copies into their own mail tool after review.
- Read only the two configured columns. Use the firm's internal reference as the client column, not the client's name; if the firm's file only has names, say that the draft will contain them and that it must stay local. The invitations start with « Bonjour, » and have no name and no address. Write the draft where the adviser says, not inside a shared folder; do not commit it, copy it elsewhere, or keep client data in memory files or logs.
- Write in French. Paste the sections produced by `due_reviews.py` unchanged: never move a client from « À vérifier » to another list, never guess a date. If the adviser corrects a date, they fix the file and you run the script again.
- No advice and no verdict: the agenda and invitations propose a meeting to review the client's situation and objectives; they never suggest a product, an allocation, an arbitrage or a return. Never write that the list is complete or exhaustive, nor « conforme ».
- One invitation per client of « Revues dues » and « Revues en retard », none for « À vérifier ».

## Steps

1. **Inputs.** Ask for the client file path (CSV or XLSX; for an old `.xls`, ask the adviser to save it as `.xlsx` or `.csv`), the sheet name if not the first one, the two column names (defaults « Référence » and « Dernière revue »), the month to prepare (default: current month) and the rule if it is not 12 months.
2. **List.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/due_reviews.py --fichier <fichier> [--mois AAAA-MM] [--delai-mois 12] [--colonne-client "Référence"] [--colonne-date "Dernière revue"] [--feuille <nom>]`. It prints the Markdown sections on stdout and a count on stderr. Exit 3 means a column was not found or the file is not a readable table: show the message (it lists the columns found) and ask, do not guess.
3. **Draft** with `${CLAUDE_SKILL_DIR}/template.md`: fill the header, paste the script's sections unchanged, keep the proposed agenda (adapt it only if the adviser asks), write one invitation block « ### référence » per due or late client, keep the « Limites » and « Relecture » sections. Leave `[créneaux proposés par le conseiller]` and `[Signature du conseiller]` for the adviser.
4. **Check.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/check_revue.py <brouillon.md>`. It checks the banner, the sections, the stated rule, that every client of the table is in exactly one list with the same date read (and the reverse), that due and late clients show their due date and the rule, that each of them has exactly one invitation and nobody else does, the limits, and forbidden wording (advice, compliance, « exhaustive », send claims, e-mail addresses). Exit 0 = pass, 1 = fix and rerun. It is a mechanical aid, not a check of the dates.
5. **Hand over.** Tell the adviser where the file is, the count line (due, late, to check), and that it is a draft: they check the dates, fix the « À vérifier » lines in their file, complete and send the invitations themselves if they choose. Stop.

## Files

- `template.md` — the draft skeleton (French), with the proposed agenda and invitation.
- `bin/due_reviews.py` — reads the CSV/XLSX file and applies the rule (Python 3 standard library, no network).
- `bin/check_revue.py` — structure, lists, invitations and wording check (standard library, no network).
- `examples/` — a fictional client file (`fictional-clients.csv`) and the draft produced from it for November 2026.
- `tests/run.sh` — test suite (offline; builds its XLSX test files on the fly).

## Limits

The list is only as good as the dates in the firm's file: a wrong date puts the wrong client on the list or leaves one out, which is why every date read is shown. `05/11/2025` is read as 5 November (French order). Formulas in XLSX are read from their last saved value; a date stored as text in an unusual format goes to « À vérifier ». The skill does not know whether a meeting is already booked, does not read the CRM, and gives no investment advice and no assurance about regulatory compliance.
