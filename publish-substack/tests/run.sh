#!/usr/bin/env bash
# Tests for publish-substack (offline, fakes only, never touches Substack). Exit 0 = all pass.
set -u
G="$(cd "$(dirname "$0")/.." && pwd)/bin/gate.py"
T="$(mktemp -d)"; trap 'rm -r "$T"' EXIT
fail=0
ok() { echo "ok   $1"; }
ko() { echo "FAIL $1"; fail=1; }
want() { # name expected_exit cmd...
  local n="$1" w="$2"; shift 2
  "$@" >/dev/null 2>&1; local rc=$?
  if [ "$rc" = "$w" ]; then ok "$n"; else ko "$n (got $rc, want $w)"; fi
}
req() { printf '%s' "$2" > "$T/$1.json"; }
good='{"kind":"note","id":"n1","text":"Un texte court.","audience":"everyone","approved":true}'
req good "$good";                                     want "valid note" 0 python3 -I "$G" request "$T/good.json"
req noaud '{"kind":"note","id":"n1","text":"x","approved":true}'
want "audience required" 1 python3 -I "$G" request "$T/noaud.json"
req badaud '{"kind":"note","id":"n1","text":"x","audience":"all","approved":true}'
want "unknown audience refused" 1 python3 -I "$G" request "$T/badaud.json"
req noappr '{"kind":"note","id":"n1","text":"x","audience":"everyone"}'
want "no approval refused" 1 python3 -I "$G" request "$T/noappr.json"
req like '{"kind":"note","id":"n1","text":"x","audience":"everyone","approved":true,"actions":["like"]}'
want "like refused (D217)" 1 python3 -I "$G" request "$T/like.json"
req del '{"kind":"post","id":"p1","title":"t","text":"x","audience":"paid","approved":true,"actions":["delete"]}'
want "delete refused" 1 python3 -I "$G" request "$T/del.json"
req batch '{"kind":"note","id":"n1","text":["a","b"],"audience":"everyone","approved":true}'
want "batch refused" 1 python3 -I "$G" request "$T/batch.json"
req notitle '{"kind":"post","id":"p1","text":"x","audience":"everyone","approved":true}'
want "post needs title" 1 python3 -I "$G" request "$T/notitle.json"
long=$(python3 -c "print('mot '*601)")
req long "{\"kind\":\"note\",\"id\":\"n1\",\"text\":\"$long\",\"audience\":\"everyone\",\"approved\":true}"
want "601-word note refused" 1 python3 -I "$G" request "$T/long.json"
req sched1 '{"kind":"note","id":"n1","text":"x","audience":"everyone","approved":true,"schedule":"2026-11-03T10:00"}'
want "schedule without zone refused" 1 python3 -I "$G" request "$T/sched1.json"
req sched2 '{"kind":"note","id":"n1","text":"x","audience":"everyone","approved":true,"schedule":"2026-11-03T10:00+01:00"}'
want "schedule without timezone name refused" 1 python3 -I "$G" request "$T/sched2.json"
req sched3 '{"kind":"note","id":"n1","text":"x","audience":"everyone","approved":true,"schedule":"2026-11-03T10:00+01:00","timezone":"Europe/Paris"}'
want "schedule with zone ok" 0 python3 -I "$G" request "$T/sched3.json"
req img '{"kind":"note","id":"n1","text":"x","audience":"everyone","approved":true,"images":["/nonexistent/a.jpg"]}'
want "missing image refused" 1 python3 -I "$G" request "$T/img.json"
want "unreadable request errors" 2 python3 -I "$G" request "$T/nope.json"

# ledger: duplicate + daily cap (attempts count, failed ones included)
L="$T/ledger.jsonl"; N="2026-11-03T12:00:00+00:00"
for i in 1 2 3 4 5; do want "note $i accepted" 0 python3 -I "$G" attempt --ledger "$L" --id "n$i" --kind note --now "$N"; done
want "6th note refused (cap 5)" 1 python3 -I "$G" attempt --ledger "$L" --id n6 --kind note --now "$N"
want "duplicate id refused" 1 python3 -I "$G" attempt --ledger "$L" --id n1 --kind note --now "$N"
want "1st post accepted" 0 python3 -I "$G" attempt --ledger "$L" --id p1 --kind post --now "$N"
want "2nd post refused (cap 1)" 1 python3 -I "$G" attempt --ledger "$L" --id p2 --kind post --now "$N"
want "next day resets cap" 0 python3 -I "$G" attempt --ledger "$L" --id n7 --kind note --now "2026-11-05T12:00:00+00:00"

# audience vs final button
want "everyone EN" 0 python3 -I "$G" label --audience everyone "Send to everyone now"
want "everyone FR" 0 python3 -I "$G" label --audience everyone "Envoyer à tous"
want "paid label for paid" 0 python3 -I "$G" label --audience paid "Send to paid subscribers"
want "paid FR" 0 python3 -I "$G" label --audience paid "Envoyer aux abonnés payants"
want "everyone button on paid item stops" 1 python3 -I "$G" label --audience paid "Send to everyone"
want "paid button on everyone item stops" 1 python3 -I "$G" label --audience everyone "Send to paid subscribers"
want "unknown button stops" 1 python3 -I "$G" label --audience everyone "Do something"

# read-back
printf 'Café déjà vu.\n' > "$T/a.txt"; printf 'Café  déjà vu.' > "$T/b.txt"; printf 'Cafe deja vu.' > "$T/c.txt"
want "readback same (whitespace only)" 0 python3 -I "$G" readback --approved "$T/a.txt" --page "$T/b.txt"
want "readback accent drift stops" 1 python3 -I "$G" readback --approved "$T/a.txt" --page "$T/c.txt"

# static: no credentials, no engagement or delete steps, no tool-switch advice in the skill
S="$(dirname "$G")/../SKILL.md"
if grep -Eiq '(password|token|cookie)[[:space:]]*[=:][[:space:]]*[A-Za-z0-9]{8,}|sk-[A-Za-z0-9]{10,}' "$S" "$G"; then ko "credential-like string in skill"; else ok "no credential-like string"; fi
if grep -Eq '[—–]' "$S"; then ko "em/en dash in SKILL.md"; else ok "no em dash in SKILL.md"; fi
if grep -Eiq 'Playwright' "$S" && grep -Eiq 'instead|switch to' <(grep -i playwright "$S"); then ko "tool-switch advice"; else ok "no tool-switch advice"; fi
[ -f "$(dirname "$G")/../../publish-substack-note/SKILL.md" ] && ko "old note skill still present" || ok "old note skill removed"
exit $fail
