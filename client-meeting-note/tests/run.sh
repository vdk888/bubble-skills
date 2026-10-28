#!/usr/bin/env bash
# Tests for client-meeting-note. Exit 0 = all pass.
set -u
D="$(cd "$(dirname "$0")/.." && pwd)"
C="$D/bin/check_note.py"
T="$(mktemp -d)"; trap 'rm -r "$T"' EXIT
fail=0
expect() { # name expected_exit file
  python3 -I "$C" "$3" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$2" ]; then echo "ok   $1"; else echo "FAIL $1 (got $rc, want $2)"; fail=1; fi
}
expect "example note passes" 0 "$D/examples/fictional-note.md"
expect "template passes structure" 0 "$D/template.md"
sed 1,2d "$D/examples/fictional-note.md" > "$T/nobanner.md"
expect "missing banner fails" 1 "$T/nobanner.md"
grep -v '^## Next steps' "$D/examples/fictional-note.md" > "$T/nosec.md"
expect "missing section fails" 1 "$T/nosec.md"
{ cat "$D/examples/fictional-note.md"; echo "We recommend buying fund X."; } > "$T/advice.md"
expect "advice wording fails" 1 "$T/advice.md"
{ cat "$D/examples/fictional-note.md"; echo "This note is fully compliant."; } > "$T/comp.md"
expect "compliance promise fails" 1 "$T/comp.md"
expect "missing file errors" 2 "$T/nope.md"
{ cat "$D/examples/fictional-note.md"; echo "> We recommend buying fund X."; } > "$T/quote.md"
expect "quoted advice fails" 1 "$T/quote.md"
{ cat "$D/examples/fictional-note.md"; echo "Nous vous conseillons de vendre."; } > "$T/fr.md"
expect "french advice fails" 1 "$T/fr.md"
sed '1s/ Not investment advice\.//' "$D/examples/fictional-note.md" > "$T/weak.md"
expect "banner without disclaimer fails" 1 "$T/weak.md"
# privacy: no network or send tooling in the skill code
if grep -rEi 'curl|wget|requests|urllib|socket|smtplib|http\.client|sendmail' "$D/bin" >/dev/null; then echo "FAIL network use in bin/"; fail=1; else echo "ok   no network code"; fi
exit $fail
