#!/usr/bin/env bash
# Tests for annual-review (offline). Exit 0 = all pass.
set -u
D="$(cd "$(dirname "$0")/.." && pwd)"
C="$D/bin/check_revue.py"
R="$D/bin/due_reviews.py"
X="$D/examples/fictional-clients.csv"
E="$D/examples/fictional-revue.md"
T="$(mktemp -d)"; trap 'rm -r "$T"' EXIT
fail=0
ok() { echo "ok   $1"; }
ko() { echo "FAIL $1"; fail=1; }
expect() { # name expected_exit file [flags...]
  local n="$1" want="$2" f="$3"; shift 3
  python3 -I "$C" "$@" "$f" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$want" ]; then ok "$n"; else ko "$n (got $rc, want $want)"; fi
}
mutate() { # name sed_expr  -> example with one change must fail
  sed "$2" "$E" > "$T/m.md"
  if cmp -s "$E" "$T/m.md"; then ko "$1 (mutation did not apply)"; else expect "$1" 1 "$T/m.md"; fi
}
add() { # name line -> example plus one line must fail
  { cat "$E"; echo "$2"; } > "$T/a.md"; expect "$1" 1 "$T/a.md"
}
has() { # name pattern text
  if printf '%s\n' "$3" | grep -qF -- "$2"; then ok "$1"; else ko "$1: no '$2'"; fi
}
run() { python3 -I "$R" --aujourdhui 2026-10-28 --mois 2026-11 "$@"; }
# xlsx FILE date1904 -- rows as python literals; numbers stay numbers (Excel dates), strings go shared or inline
xlsx() {
  python3 -I - "$@" <<'PY'
import sys, zipfile
from xml.sax.saxutils import escape
out, d1904, rows = sys.argv[1], sys.argv[2] == "1", eval(sys.argv[3])
shared, xml = [], []
for i, row in enumerate(rows, 1):
    cells = []
    for j, v in enumerate(row):
        ref = chr(65 + j) + str(i)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            cells.append(f'<c r="{ref}"><v>{v}</v></c>')
        elif j == 0 and i > 1:
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(v)}</t></is></c>')
        else:
            shared.append(v)
            cells.append(f'<c r="{ref}" t="s"><v>{len(shared) - 1}</v></c>')
    xml.append(f'<row r="{i}">{"".join(cells)}</row>')
M = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
with zipfile.ZipFile(out, "w") as z:
    z.writestr("xl/workbook.xml", f'<workbook {M} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
               + ('<workbookPr date1904="1"/>' if d1904 else "")
               + '<sheets><sheet name="Notes" sheetId="1" r:id="rId1"/><sheet name="Clients" sheetId="2" r:id="rId2"/></sheets></workbook>')
    z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>')
    z.writestr("xl/worksheets/sheet1.xml", f'<worksheet {M}><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>notes</t></is></c></row></sheetData></worksheet>')
    z.writestr("xl/worksheets/sheet2.xml", f'<worksheet {M}><sheetData>{"".join(xml)}</sheetData></worksheet>')
    z.writestr("xl/sharedStrings.xml", f'<sst {M}>' + "".join(f"<si><t>{escape(s)}</t></si>" for s in shared) + "</sst>")
PY
}

# checker
expect "example draft passes" 0 "$E"
expect "template passes structure" 0 "$D/template.md" --structure-only
expect "unfilled template fails" 1 "$D/template.md"
expect "missing file errors" 2 "$T/nope.md"
mutate "missing banner fails" '1d'
has "banner uses the approved wording" "L'outil prépare, vous validez." "$(head -1 "$E")$(head -1 "$D/template.md")"
mutate "banner without 'Aucun envoi' fails" '1s/ Aucun envoi\.//'
mutate "missing section fails" '/^## Revues en retard/d'
mutate "rule not stated fails" 's/dernière revue + 12 mois tombe/date tombe/'
mutate "listed client dropped from lists fails" '/^- \*\*EX-001\*\*/d'
mutate "table row dropped fails (list without table)" '/^| EX-001 |/d'
mutate "to-check client moved to due fails" '/^| EX-004 |/s/à vérifier : date manquante/due en novembre 2026/'
mutate "date read differs between table and list fails" '/^- \*\*EX-001\*\*/s/« 14\/11\/2025 »/« 15\/11\/2025 »/'
mutate "due client without due date fails" '/^- \*\*EX-002\*\*/s/ ; échéance.*//'
mutate "due client with another rule fails" '/^- \*\*EX-002\*\*/s/+ 12 mois/+ 6 mois/'
mutate "to-check client without reason fails" '/^- \*\*EX-005\*\*/s/ ; date illisible//'
mutate "missing invitation fails" 's/^### EX-003$/### EX-0003/'
awk '/^Objet :/ && !done {done=1; next} {print}' "$E" > "$T/noobj.md"
expect "invitation without Objet fails" 1 "$T/noobj.md"
mutate "limits without 'aucun conseil' fails" 's/ne donne aucun conseil/ne donne pas de conseil/'
awk '/^## Limites/{print "### EX-005\n\nObjet : x\n\nBonjour,\n"} {print}' "$E" > "$T/inv.md"
expect "invitation for a to-check client fails" 1 "$T/inv.md"
add "advice wording fails" "Nous vous recommandons d'arbitrer vers le fonds X."
add "return wording fails" "Un rendement garanti de 4 %."
add "compliance wording fails" "Revue conforme."
add "exhaustive claim fails" "Cette liste est exhaustive."
add "send claim fails" "Les invitations ont été envoyées."
add "email address fails" "À : client@example.com"
add "english advice fails" "We recommend this fund."

# reader on the fictional CSV: the example's sections are exactly the reader's output
out="$(run --fichier "$X" 2>"$T/err")"; rc=$?
[ "$rc" = 0 ] && ok "reader runs on the fictional CSV" || ko "reader runs on the fictional CSV (rc $rc)"
printf '%s\n' "$out" > "$T/out.md"
if [ "$(grep -cxFf "$T/out.md" "$E")" -ge "$(grep -c . "$T/out.md")" ]; then ok "example sections match the reader output"; else ko "example sections differ from the reader output"; fi
has "count line on stderr" "10 lignes client lues : 3 revues dues en novembre 2026, 1 revue en retard, 4 lignes à vérifier, 2 clients pas encore dus" "$(cat "$T/err")"
has "rule stated with month and columns" "Mois examiné : novembre 2026 (2026-11). Fichier : fictional-clients.csv ; colonnes lues : « Référence » (client) et « Dernière revue »" "$out"
has "due client shows date read and rule" "- **EX-001** — date lue « 14/11/2025 », comprise comme le 2025-11-14 ; échéance 2026-11-14 (dernière revue + 12 mois)" "$out"
has "late client listed" "| EX-003 | « 22/09/2025 » | 2025-09-22 | 2026-09-22 | en retard |" "$out"
has "empty date is à vérifier" "- **EX-004** — date lue (vide) ; date manquante" "$out"
has "unreadable date is à vérifier" "- **EX-005** — date lue « fin 2025 » ; date illisible" "$out"
has "two-digit year is à vérifier" "- **EX-006** — date lue « 05/11/25 » ; année sur deux chiffres" "$out"
has "future date is à vérifier" "- **EX-009** — date lue « 12/01/2027 », comprise comme le 2027-01-12 ; date postérieure à aujourd'hui" "$out"
if printf '%s\n' "$out" | grep -qE 'EX-007|EX-010'; then ko "clients not yet due are not listed"; else ok "clients not yet due are not listed"; fi
if printf '%s\n' "$out" | grep -q 'Client fictif'; then ko "name column never read"; else ok "name column never read"; fi
if printf '%s\n' "$out" | grep -E '^\| EX-' | cut -d'|' -f2 | sort | uniq -d | grep -q .; then ko "each client once in the table"; else ok "each client once in the table"; fi

# grammar: singular counts
printf 'Référence;Dernière revue\nA;10/11/2025\nB;01/01/2025\nC;\nD;01/06/2026\n' > "$T/one.csv"
run --fichier "$T/one.csv" >/dev/null 2>"$T/err1"
has "singular count line" "4 lignes client lues : 1 revue due en novembre 2026, 1 revue en retard, 1 ligne à vérifier, 1 client pas encore dû" "$(cat "$T/err1")"
if grep -qE '\b1 [a-z]+s\b' "$T/err1"; then ko "no '1 ...s' plural"; else ok "no '1 ...s' plural"; fi
printf 'Référence;Dernière revue\nA;01/06/2026\n' > "$T/none.csv"
out="$(run --fichier "$T/none.csv" 2>"$T/err0")"
has "zero takes the singular" "1 ligne client lue : 0 revue due en novembre 2026, 0 revue en retard, 0 ligne à vérifier, 1 client pas encore dû" "$(cat "$T/err0")"
has "no client gives the neutral lines" "Aucune revue due en novembre 2026 d'après le fichier." "$out"
has "empty table row" "| (aucun client retenu) | — | — | — | — |" "$out"

# configurable columns, delay, separators, encodings, edge dates
printf 'Code client,Nom,Date dernier RDV\nK1,Fictif,2026-05-15\nK2,Fictif,2026-05-31 00:00:00\n' > "$T/comma.csv"
out="$(run --fichier "$T/comma.csv" --colonne-client "code CLIENT" --colonne-date "date dernier rdv" --delai-mois 6 2>/dev/null)"; rc=$?
[ "$rc" = 0 ] && ok "comma CSV with other column names" || ko "comma CSV with other column names (rc $rc)"
has "6-month rule" "échéance 2026-11-15 (dernière revue + 6 mois)" "$out"
has "time part ignored" "- **K2** — date lue « 2026-05-31 00:00:00 », comprise comme le 2026-05-31 ; échéance 2026-11-30" "$out"
printf 'R\xe9f\xe9rence;Derni\xe8re revue\nW1;29/11/2025\n' > "$T/cp1252.csv"
out="$(run --fichier "$T/cp1252.csv" 2>/dev/null)"
has "Windows-1252 CSV" "- **W1** — date lue « 29/11/2025 »" "$out"
printf 'Référence;Dernière revue\nL1;29/02/2024\nL2;31/02/2025\nL3;15.11.2025\nE1;12/11/2025\nE1;20/11/2025\n;10/11/2025\n' > "$T/edge.csv"
out="$(run --fichier "$T/edge.csv" --delai-mois 33 2>/dev/null)"
has "29 Feb + months clamps to month end" "- **L1** — date lue « 29/02/2024 », comprise comme le 2024-02-29 ; échéance 2026-11-29" "$out"
out="$(run --fichier "$T/edge.csv" 2>/dev/null)"
has "impossible date is à vérifier" "- **L2** — date lue « 31/02/2025 » ; date illisible" "$out"
has "dotted date read" "- **L3** — date lue « 15.11.2025 », comprise comme le 2025-11-15" "$out"
has "duplicate reference is à vérifier" "- **E1 (ligne 5)** — date lue « 12/11/2025 », comprise comme le 2025-11-12 ; référence présente sur plusieurs lignes" "$out"
has "empty reference is à vérifier" "- **ligne 7 (référence vide)** — date lue « 10/11/2025 », comprise comme le 2025-11-10 ; référence client vide" "$out"
{ sed -n '1,/^## Règle appliquée/p' "$E" | sed '$d'; printf '%s\n\n' "$out"; sed -n '/^## Ordre du jour/,/^### EX-002$/p' "$E" | sed '$d'
  for r in L3 L1; do printf '### %s\n\nObjet : Votre rendez-vous annuel de suivi\n\nBonjour,\n\n' "$r"; done; sed -n '/^## Limites/,$p' "$E"; } > "$T/edge.md"
expect "draft from the edge file passes" 0 "$T/edge.md"

# XLSX: same data as the fictional CSV, Excel date cells, shared and inline strings, second sheet
rows='[["Référence","Nom","Dernière revue"],["EX-001","Fictif",45975],["EX-002","Fictif","2025-11-03"],["EX-003","Fictif",45922],["EX-004","Fictif",None],["EX-005","Fictif","fin 2025"],[42,"Fictif",45991]]'
xlsx "$T/c.xlsx" 0 "$rows"
out="$(run --fichier "$T/c.xlsx" --feuille Clients 2>"$T/errx")"; rc=$?
[ "$rc" = 0 ] && ok "XLSX read with the standard library" || ko "XLSX read (rc $rc: $(cat "$T/errx"))"
has "XLSX Excel date cell" "- **EX-001** — date lue « 14/11/2025 (date Excel 45975) », comprise comme le 2025-11-14 ; échéance 2026-11-14 (dernière revue + 12 mois)" "$out"
has "XLSX text date" "- **EX-002** — date lue « 2025-11-03 »" "$out"
has "XLSX empty cell is à vérifier" "- **EX-004** — date lue (vide) ; date manquante" "$out"
has "XLSX numeric reference" "- **42** — date lue « 30/11/2025 (date Excel 45991) »" "$out"
has "XLSX late client" "- **EX-003** — date lue « 22/09/2025 (date Excel 45922) »" "$out"
has "XLSX sheet named in the rule" "Fichier : c.xlsx, feuille « Clients »" "$out"
xlsx "$T/d.xlsx" 1 '[["Référence","Dernière revue"],["M1",44513]]'
out="$(run --fichier "$T/d.xlsx" --feuille Clients 2>/dev/null)"
has "XLSX 1904 date system" "- **M1** — date lue « 14/11/2025 (date Excel 44513) »" "$out"
xlsx "$T/n.xlsx" 0 '[["Référence","Dernière revue"],["N1",2025],["N2",32874],["N3",32873]]'
out="$(run --fichier "$T/n.xlsx" --feuille Clients 2>/dev/null)"
has "XLSX plain number (2025) is à vérifier, not a 1905 date" "- **N1** — date lue « 2025 » ; nombre qui ne donne pas une date plausible (avant 1990)" "$out"
if printf '%s\n' "$out" | grep -q '1905'; then ko "no 1905 date in the draft"; else ok "no 1905 date in the draft"; fi
has "XLSX number giving 01/01/1990 is read as a date" "- **N2** — date lue « 01/01/1990 (date Excel 32874) »" "$out"
has "XLSX number giving 31/12/1989 is à vérifier" "- **N3** — date lue « 32873 » ; nombre qui ne donne pas une date plausible" "$out"
if printf '%s\n' "$out" | grep -A3 '^## Revues en retard' | grep -q 'N1'; then ko "plain number not listed late"; else ok "plain number not listed late"; fi
# bomb FILE kind: big (one part over the per-part cap), total (three parts under it, over the total), entity (DOCTYPE)
bomb() {
  python3 -I - "$@" <<'PY2'
import sys, zipfile
out, kind = sys.argv[1], sys.argv[2]
M = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
pad = lambda mb: " " * (mb * 1024 * 1024)
wb = f'<workbook {M} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="S" sheetId="1" r:id="rId1"/></sheets>{pad(40) if kind == "total" else ""}</workbook>'
sst = f'<sst {M}><si><t>Référence</t></si>{pad(40) if kind == "total" else ""}</sst>'
big = "9" * (60 * 1024 * 1024) if kind == "big" else "45975"
ws = f'<worksheet {M}><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row><row r="2"><c r="A2"><v>{big}</v></c></row>{pad(40) if kind == "total" else ""}</sheetData></worksheet>'
if kind == "entity":
    ws = '<?xml version="1.0"?><!DOCTYPE w [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">]>' + ws.replace("45975", "&b;")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("xl/workbook.xml", wb)
    z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
    z.writestr("xl/sharedStrings.xml", sst)
    z.writestr("xl/worksheets/sheet1.xml", ws)
PY2
}
for k in big total entity; do
  bomb "$T/b-$k.xlsx" "$k"
  run --fichier "$T/b-$k.xlsx" --colonne-date Référence >"$T/bo" 2>"$T/be"; rc=$?
  [ "$rc" = 3 ] && [ ! -s "$T/bo" ] && ok "XLSX $k bomb refused (exit 3, nothing printed)" || ko "XLSX $k bomb refused (rc $rc)"
done
[ "$(stat -f %z "$T/b-big.xlsx" 2>/dev/null || stat -c %s "$T/b-big.xlsx")" -lt 1000000 ] && ok "big bomb is a small file" || ko "big bomb is a small file"
has "per-part cap message" "too large once uncompressed (cap 50 MB per part, 100 MB in total)" "$(run --fichier "$T/b-big.xlsx" 2>&1)"
has "total cap message" "XLSX part xl/worksheets/sheet1.xml too large" "$(run --fichier "$T/b-total.xlsx" 2>&1)"
has "DOCTYPE message" "declares a DOCTYPE" "$(run --fichier "$T/b-entity.xlsx" 2>&1)"
python3 -I "$R" --fichier "$T/c.xlsx" --aujourdhui 2026-10-28 --mois 2026-11 >/dev/null 2>"$T/e3"; [ $? = 3 ] && ok "first sheet by default, missing column exit 3" || ko "first sheet by default, missing column exit 3"
has "missing column lists the columns found" "columns: « notes »" "$(cat "$T/e3")"

# errors
run --fichier "$X" --colonne-date "Date" >/dev/null 2>&1; [ $? = 3 ] && ok "unknown column rejected" || ko "unknown column rejected"
run --fichier "$T/c.xlsx" --feuille Nope >/dev/null 2>&1; [ $? = 3 ] && ok "unknown sheet rejected" || ko "unknown sheet rejected"
echo "pas un zip" > "$T/bad.xlsx"; run --fichier "$T/bad.xlsx" >/dev/null 2>&1; [ $? = 3 ] && ok "broken XLSX rejected" || ko "broken XLSX rejected"
echo x > "$T/old.xls"; run --fichier "$T/old.xls" >/dev/null 2>&1; [ $? = 3 ] && ok ".xls asks for xlsx or csv" || ko ".xls asks for xlsx or csv"
run --fichier "$T/nope.csv" >/dev/null 2>&1; [ $? = 2 ] && ok "missing file errors" || ko "missing file errors"
run --fichier "$X" --delai-mois zero >/dev/null 2>&1; [ $? = 2 ] && ok "bad delay rejected" || ko "bad delay rejected"
python3 -I "$R" --fichier "$X" --mois 2026-13 >/dev/null 2>&1; [ $? = 2 ] && ok "bad month rejected" || ko "bad month rejected"
python3 -I "$R" >/dev/null 2>&1; [ $? = 2 ] && ok "usage error" || ko "usage error"

# privacy: no network, no send
if grep -Ei 'urllib|socket|http\.client|requests|curl|wget|smtplib|sendmail|webhook|telegram|slack' "$D"/bin/*.py >/dev/null; then ko "network or send code in bin/"; else ok "no network or send code"; fi
exit $fail
