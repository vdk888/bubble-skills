---
name: regulatory-watch
description: Draft a weekly regulatory watch in French for a wealth-management firm (CGP) — the new AMF and ACPR publications of the week that matter to advisers, each with date, source, title, official link and one line on why it matters. Public official sources only, local Markdown file, never sends anything. Use when a firm wants its weekly AMF/ACPR digest drafted for review. Not investment advice, not a compliance opinion.
version: 1.0.0
author: Bubble Invest
license: MIT
user-invocable: true
allowed-tools:
  - Bash(python3 *amf_feed.py*)
  - Bash(python3 *check_digest.py*)
  - WebFetch(domain:acpr.banque-france.fr)
  - WebFetch(domain:www.amf-france.org)
  - Read
  - Write
---

# regulatory-watch — veille réglementaire hebdomadaire AMF / ACPR

> **Draft only. Elle prépare, vous validez.** The skill lists and summarises public publications; the firm reads, checks the links and decides what applies to it. It gives no investment advice, no legal opinion, and never states that the firm, a document or a practice is compliant (never write « conforme »).

## What it does

For one week (Monday to Sunday, default: the last full week), reads the official AMF and ACPR sources below, keeps the publications useful to a CGP / CIF / IAS / IOBSP adviser, and writes ONE local Markdown file in French from `template.md`. The person in charge (dirigeant or RCCI) reads and validates it.

## Sources (public, official, verified 2026-10-28)

AMF — RSS feeds, read by `bin/amf_feed.py` (list: https://www.amf-france.org/fr/abonnements-flux-rss):
- `21` Toutes les actualités et publications — https://www.amf-france.org/fr/flux-rss/display/21
- `28` Alertes et mises en garde — https://www.amf-france.org/fr/flux-rss/display/28
- `31` Réglementation de l'AMF (RG, doctrine) — https://www.amf-france.org/fr/flux-rss/display/31

ACPR — no RSS feed exists (only e-mail alerts, which this skill does not use). Read these pages with WebFetch:
- Actualités — https://acpr.banque-france.fr/fr/actualites
- Communiqués de presse — https://acpr.banque-france.fr/fr/communiques-de-presse
- Registre officiel (instructions, recommandations, positions…) — https://acpr.banque-france.fr/fr/reglementation/registre-officiel

No other source. No search engine, no blog, no newsletter, no invented URL. Every link in the digest must come from one of these sources.

## Rules (non-negotiable)

- Public data only. No client name, no client file, nothing about the firm's clients goes in or out.
- Never send the digest. No e-mail, no messaging, no posting. Output is a local file the firm opens.
- Write in French. Keep official titles as published.
- Each item: date, source (AMF, ACPR or AMF et ACPR), title, official link, one line « Pourquoi c'est utile » for an adviser. If the date, the scope or the relevance is unsure, add `À vérifier :` with what to check. Do not guess.
- The « Pourquoi » line says what the publication is about and who it concerns (« concerne les CIF qui… », « à lire si le cabinet distribue… »). No recommendation to clients, no buy/sell/invest wording, no compliance verdict (« conforme », « vous êtes en règle »), no promise.
- Keep only publications dated inside the week. Skip pure institutional items (agenda, recruitment, speeches) unless they announce a rule or a warning.
- A source that could not be read is listed as « non lue » in **Sources consultées**, never silently dropped.

## Steps

1. **Week.** Ask for the week if not given; default is the last full Monday–Sunday week. Note start (lundi) and end (dimanche) as `YYYY-MM-DD`.
2. **AMF.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/amf_feed.py --du <lundi> --au <dimanche>`. It prints one tab-separated line per item (date, feed, title, link) and the status of each feed on stderr. It only contacts www.amf-france.org.
3. **ACPR.** WebFetch the three ACPR pages and list the items dated in the week, with their full `https://acpr.banque-france.fr/...` link. If a page shows no dated list, mark it « non lue » or « lue, rien dans la semaine » accordingly.
4. **Select and draft** with `${CLAUDE_SKILL_DIR}/template.md`. Merge duplicates (joint AMF–ACPR items: one entry, source « AMF et ACPR »). If needed, open an item's page (same domains) to write the « Pourquoi » line; otherwise base it on the title and mark `À vérifier`.
5. **Check.** Run `python3 ${CLAUDE_SKILL_DIR}/bin/check_digest.py <digest.md>`. It checks the banner, the sections, that every item has a date inside the period and an https link on amf-france.org or acpr.banque-france.fr, and flags forbidden wording. Exit 0 = pass, 1 = fix and rerun. It is a mechanical aid, not a review.
6. **Hand over.** Tell the firm where the file is, which sources were not read, and that it is a draft to validate. Stop. Do not send or publish it.

## Files

- `template.md` — the digest skeleton (French).
- `bin/amf_feed.py` — reads the AMF RSS feeds for a period (Python 3 standard library; network to www.amf-france.org only; `--fichier` for an offline file).
- `bin/check_digest.py` — structure, dates, links and wording check (standard library, no network).
- `examples/fictional-digest.md` — a fictional digest (invented titles and links, for illustration only).
- `tests/run.sh` — test suite (offline).

## Limits

Sites change: a feed or page may move or be unreadable — the digest says so in « Sources consultées ». The skill can miss a publication or misjudge its relevance; it does not cover ESMA, EIOPA, the Journal officiel or case law. It gives no assurance about regulatory compliance.
