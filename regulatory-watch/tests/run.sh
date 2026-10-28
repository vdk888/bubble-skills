#!/usr/bin/env bash
# Tests for regulatory-watch (offline). Exit 0 = all pass.
set -u
D="$(cd "$(dirname "$0")/.." && pwd)"
C="$D/bin/check_digest.py"
F="$D/bin/amf_feed.py"
E="$D/examples/fictional-digest.md"
T="$(mktemp -d)"; trap 'rm -r "$T"' EXIT
fail=0
ok() { echo "ok   $1"; }
ko() { echo "FAIL $1"; fail=1; }
expect() { # name expected_exit file [flag]
  python3 -I "$C" ${4:-} "$3" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$2" ]; then ok "$1"; else ko "$1 (got $rc, want $2)"; fi
}
mutate() { # name sed_expr  -> example with one change must fail
  sed "$2" "$E" > "$T/m.md"
  if cmp -s "$E" "$T/m.md"; then ko "$1 (mutation did not apply)"; else expect "$1" 1 "$T/m.md"; fi
}
add() { # name line -> example plus one line must fail
  { cat "$E"; echo "$2"; } > "$T/a.md"; expect "$1" 1 "$T/a.md"
}

# checker
expect "example digest passes" 0 "$E"
expect "template passes structure" 0 "$D/template.md" --structure-only
expect "unfilled template fails" 1 "$D/template.md"
expect "missing file errors" 2 "$T/nope.md"
mutate "missing banner fails" '1d'
mutate "banner without disclaimer fails" '1s/ Pas un conseil en investissement\.//'
mutate "missing section fails" '/^## Sources consultées/d'
mutate "missing period fails" '/Période/d'
mutate "period longer than a week fails" 's/au 2026-10-25/au 2026-10-31/'
mutate "date outside the week fails" 's/Date :\*\* 2026-10-21/Date :** 2026-10-27/'
mutate "unreadable date fails" 's/Date :\*\* 2026-10-21/Date :** la semaine dernière/'
sed 's/Date :\*\* 2026-10-21/Date :** 21\/10\/2026/' "$E" > "$T/fr.md"
expect "french date format passes" 0 "$T/fr.md"
mutate "link off official sites fails" 's#https://www.amf-france.org/fr/exemple-fictif/doctrine-information-frais#https://www.example.com/doctrine#'
mutate "http link fails" 's#https://www.amf-france.org/fr/exemple-fictif/doctrine#http://www.amf-france.org/fr/exemple-fictif/doctrine#'
mutate "lookalike domain fails" 's#https://acpr.banque-france.fr/fr/exemple-fictif#https://acpr.banque-france.fr.evil.com/fr/exemple-fictif#'
mutate "source/link mismatch fails" 's/Source :\*\* ACPR$/Source :** AMF/'
mutate "unknown source fails" 's/Source :\*\* AMF$/Source :** un blog/'
mutate "missing link fails" '/exemple-fictif\/doctrine/d'
mutate "missing why line fails" '/concerne les CIF/d'
awk '/^### /{skip=1} /^## Sources/{skip=0} !skip' "$E" > "$T/empty.md"
expect "empty week without notice fails" 1 "$T/empty.md"
awk '/^## Sources/{print "Aucune publication retenue cette semaine."; print ""} 1' "$T/empty.md" > "$T/empty2.md"
expect "empty week with notice passes" 0 "$T/empty2.md"
add "conforme fails" "Le cabinet est conforme."
add "conformes fails" "Vos documents sont conformes à la doctrine."
add "en règle fails" "Vous êtes en règle avec cette recommandation."
add "advice wording fails" "Nous vous conseillons de vendre ces fonds."
add "buy wording fails" "Il faut acheter avant la fin du mois."
add "return promise fails" "Rendement garanti de 5 %."
add "quoted advice fails" "> Nous recommandons ce placement."
{ cat "$E"; echo "En règle générale, la doctrine s'applique aux CIF."; } > "$T/neutral.md"
expect "neutral 'en règle générale' passes" 0 "$T/neutral.md"

# feed reader (offline, local fixture)
out="$(python3 -I "$F" --du 2026-10-19 --au 2026-10-25 --fichier "$D/tests/fixtures/amf-sample.xml" 2>/dev/null)"; rc=$?
[ "$rc" = 0 ] && ok "feed reader runs offline" || ko "feed reader runs offline (rc $rc)"
[ "$(printf '%s\n' "$out" | grep -c .)" = 2 ] && ok "feed keeps 2 in-week items (period, domain, dedupe)" || ko "feed item count: $out"
printf '%s\n' "$out" | head -1 | grep -q $'^2026-10-22\t.*\thttps://www.amf-france.org/fr/exemple-fictif/mise-en-garde$' \
  && ok "feed sorted, tracking fragment stripped" || ko "feed first line: $(printf '%s\n' "$out" | head -1)"
python3 -I "$F" --du 2026-10-25 --au 2026-10-19 --fichier "$D/tests/fixtures/amf-sample.xml" >/dev/null 2>&1
[ $? = 2 ] && ok "feed rejects reversed period" || ko "feed rejects reversed period"
python3 -I "$F" --fichier "$T/nope.xml" >/dev/null 2>&1
[ $? = 3 ] && ok "feed reports unreadable source" || ko "feed reports unreadable source"

# privacy: checker has no network; feed reader only knows amf-france.org; nothing can send
if grep -Ei 'urllib\.request|socket|http\.client|requests|curl|wget' "$C" >/dev/null; then ko "network use in checker"; else ok "checker has no network code"; fi
hosts="$(grep -oE 'https?://[A-Za-z0-9.-]*[A-Za-z0-9]' "$F" | sort -u | tr '\n' ' ')"
[ "$hosts" = "https://www.amf-france.org " ] && ok "feed reader only contacts www.amf-france.org" || ko "feed reader hosts: $hosts"
if grep -rEi 'smtplib|sendmail|webhook|telegram|slack|urlopen\(.*data=' "$D/bin" >/dev/null; then ko "send code in bin/"; else ok "no send code"; fi
exit $fail
