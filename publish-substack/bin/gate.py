#!/usr/bin/env python3
"""Offline gates for publish-substack. Standard library only. No network, no browser.

  gate.py request FILE.json            validate the approved request (exit 0 ok, 1 refused)
  gate.py attempt --ledger F --id ID --kind note|post [--now ISO]
                                       count one attempt BEFORE touching the browser; refuses
                                       duplicate ids and a reached daily cap (failed runs count)
  gate.py label --audience A "BUTTON"  final button text must match the audience
  gate.py readback --approved FILE.txt --page FILE.txt
                                       text read back from the editor must equal the approved text
"""
import argparse, json, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path

CAPS = {"note": 5, "post": 1}            # per day, attempts included (our numbers, not Substack's)
AUDIENCES = {"everyone", "paid", "founding"}
FORBIDDEN_ACTIONS = {"like", "comment", "reply", "restack", "follow", "message", "delete", "read_feed"}
MAX_WORDS = {"note": 600, "post": 4000}
# final-button wording per audience, English and French (matched lower-case, accents folded)
LABELS = {
    "everyone": ["send to everyone", "publish", "envoyer a tous", "publier"],  # + exact Note buttons below
    "paid": ["send to paid subscribers", "envoyer aux abonnes payants"],
    "founding": ["send to founding members", "envoyer aux membres fondateurs"],
}
WRONG = {  # a label of another audience is always a mismatch
    a: [l for b, ls in LABELS.items() if b != a for l in ls] for a in LABELS
}


NOTE_BUTTONS = {"post", "publier"}  # Note composer final button (EN, FR); exact match only


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def words(s):
    return len(s.split())


def check_request(r):
    errs = []
    if not isinstance(r, dict):
        return ["request must be a JSON object"]
    if r.get("kind") not in CAPS:
        errs.append("kind must be 'note' or 'post'")
    if not r.get("id"):
        errs.append("id is required (one id per item, used for the duplicate check)")
    if "items" in r or isinstance(r.get("text"), list):
        errs.append("one item per run: no batches")
    if not isinstance(r.get("text"), str) or not r.get("text", "").strip():
        errs.append("text is required")
    if r.get("audience") not in AUDIENCES:
        errs.append("audience is required: one of %s" % sorted(AUDIENCES))
    if r.get("approved") is not True:
        errs.append("approved must be true (the person confirmed this exact item in this session)")
    bad = FORBIDDEN_ACTIONS & {str(a).lower() for a in r.get("actions", [])}
    if bad:
        errs.append("publishing only, refused actions: %s" % sorted(bad))
    if r.get("kind") == "post" and not r.get("title"):
        errs.append("a post needs a title")
    k = r.get("kind")
    if k in MAX_WORDS and isinstance(r.get("text"), str) and words(r["text"]) > MAX_WORDS[k]:
        errs.append("text too long for a %s (max %d words)" % (k, MAX_WORDS[k]))
    if r.get("schedule") is not None:
        s = str(r["schedule"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}[+-]\d{2}:\d{2}", s):
            errs.append("schedule needs date, time and zone, e.g. 2026-11-03T10:00+01:00")
        elif not r.get("timezone"):
            errs.append("timezone name is required with a schedule (e.g. Europe/Paris)")
    for img in r.get("images", []):
        if not Path(img).is_file():
            errs.append("image missing: %s (a missing image stops the run)" % img)
    return errs


def attempt(ledger, id_, kind, now=None):
    now = now or datetime.now(timezone.utc)
    day = now.astimezone().date().isoformat() if now.tzinfo else now.date().isoformat()
    p = Path(ledger)
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
    if kind not in CAPS:
        return "unknown kind"
    if any(r["id"] == id_ for r in rows):
        return "duplicate id %s: already attempted, check your profile before anything else" % id_
    n = sum(1 for r in rows if r["day"] == day and r["kind"] == kind)
    if n >= CAPS[kind]:
        return "daily cap reached: %d %s attempt(s) today (cap %d)" % (n, kind, CAPS[kind])
    with p.open("a") as f:
        f.write(json.dumps({"id": id_, "kind": kind, "day": day}) + "\n")
    return None


def label_ok(audience, button):
    b = fold(button)
    if audience not in LABELS:
        return False
    if any(w in b for w in WRONG[audience]) and not any(w in b for w in LABELS[audience]):
        return False
    # "send to everyone" is a substring-safe check only for its own audience
    if audience == "everyone" and b in NOTE_BUTTONS:  # the Note composer's own button
        return True
    return any(b.startswith(w) for w in LABELS[audience])


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("request"); a.add_argument("file")
    t = sub.add_parser("attempt"); t.add_argument("--ledger", required=True)
    t.add_argument("--id", required=True); t.add_argument("--kind", required=True)
    t.add_argument("--now")
    l = sub.add_parser("label"); l.add_argument("--audience", required=True); l.add_argument("button")
    b = sub.add_parser("readback"); b.add_argument("--approved", required=True); b.add_argument("--page", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "request":
            errs = check_request(json.loads(Path(args.file).read_text()))
        elif args.cmd == "attempt":
            now = datetime.fromisoformat(args.now) if args.now else None
            e = attempt(args.ledger, args.id, args.kind, now)
            errs = [e] if e else []
        elif args.cmd == "label":
            errs = [] if label_ok(args.audience, args.button) else [
                "button '%s' does not match audience '%s': stop" % (args.button, args.audience)]
        else:
            x = Path(args.approved).read_text(); y = Path(args.page).read_text()
            norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()
            errs = [] if norm(x) == norm(y) else ["text read back differs from the approved text: stop"]
    except (OSError, ValueError) as e:
        print("ERROR: %s" % e); return 2
    for e in errs:
        print("REFUSED: %s" % e)
    if not errs:
        print("ok")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
