#!/usr/bin/env bash
# Tests for missing-documents (offline). Exit 0 = all pass.
set -u
D="$(cd "$(dirname "$0")/.." && pwd)"
C="$D/bin/check_relance.py"
M="$D/bin/match_documents.py"
L="$D/liste-pieces.txt"
E="$D/examples/fictional-relance.md"
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
  if cmp -s "$E" "$T/m.md"; then ko "$1 (mutation did not apply)"; else expect "$1" 1 "$T/m.md" --liste "$L"; fi
}
add() { # name line -> example plus one line must fail
  { cat "$E"; echo "$2"; } > "$T/a.md"; expect "$1" 1 "$T/a.md"
}
has() { # name pattern text
  if printf '%s\n' "$3" | grep -qF -- "$2"; then ok "$1"; else ko "$1: no '$2'"; fi
}

# checker
expect "example draft passes" 0 "$E" --liste "$L"
expect "example draft passes without list" 0 "$E"
expect "template passes structure" 0 "$D/template.md" --structure-only
expect "unfilled template fails" 1 "$D/template.md"
expect "missing file errors" 2 "$T/nope.md"
expect "missing checklist errors" 2 "$E" --liste "$T/nope.txt"
mutate "missing banner fails" '1d'
mutate "banner without 'Aucun envoi' fails" '1s/ Aucun envoi\.//'
mutate "missing section fails" '/^## Fichiers non rattachés/d'
mutate "missing 'manquantes' section fails" '/^## Pièces manquantes/d'
mutate "checklist item dropped fails (false complete)" '/^- \*\*Justificatif d.origine des fonds\*\*$/d'
mutate "missing item moved to found fails" 's/^- \*\*Questionnaire de connaissance client signé\*\*$/- **Questionnaire de connaissance client signé** — `questionnaire.pdf`/'
awk '/^- \*\*RIB\*\* — /{next} {print} /^- \*\*Lettre de mission signée\*\*/{print "- **RIB** — `facture_energie_aout2026_avec_RIB.pdf` (mot-clé « rib »)"}' "$E" > "$T/moved.md"
expect "to-check item moved to found fails" 1 "$T/moved.md" --liste "$L"
mutate "found item with another file fails" 's/`lettre_de_mission_signee.pdf` (mot-clé/`scan_0042.pdf` (mot-clé/'
mutate "found item without file name fails" 's/^- \*\*Lettre de mission signée\*\* — .*/- **Lettre de mission signée** — trouvée/'
mutate "invented item fails" 's/^- \*\*RIB\*\* —/- **RIB bis** —/'
mutate "missing item not in email fails" '/^- Justificatif d.origine des fonds$/d'
mutate "email without Objet fails" '/^Objet :/d'
mutate "limits without LCB-FT fails" 's/contrôle LCB-FT \/ connaissance client du cabinet/contrôle du cabinet/'
mutate "limits without identité fails" "s/l'identité du client, ni //"
mutate "empty correspondence table fails" '/^| `/d'
add "complet fails" "Le dossier est complet."
add "complète fails" "La liste est complète."
add "incomplet fails" "Votre dossier est incomplet."
add "conforme fails" "Dossier conforme."
add "dossier validé fails" "Dossier validé."
add "rien ne manque fails" "Rien ne manque."
add "identity claim fails" "Identité vérifiée."
add "authenticity claim fails" "Les pièces sont authentiques."
add "send claim fails" "Le mail a été envoyé au client."
add "email address fails" "À : client@example.com"
add "english verdict fails" "Folder complete, nothing missing."
{ cat "$E"; echo '- `dossier_complet_conforme.pdf` reste à ouvrir.'; } > "$T/name.md"
expect "verdict word inside a file name passes" 0 "$T/name.md"
{ cat "$E"; echo "Pour compléter votre dossier, merci de nous transmettre ces pièces."; } > "$T/neutral.md"
expect "neutral 'compléter' / 'transmettre' passes" 0 "$T/neutral.md"

# matcher on the fictional listing: the example's sections are exactly the matcher's output
out="$(python3 -I "$M" --liste "$L" --fichiers "$D/examples/fictional-listing.txt" 2>"$T/err")"; rc=$?
[ "$rc" = 0 ] && ok "matcher runs on listing" || ko "matcher runs on listing (rc $rc)"
printf '%s\n' "$out" > "$T/out.md"
if grep -qxFf "$T/out.md" "$E" && [ "$(grep -cxFf "$T/out.md" "$E")" -ge "$(grep -c . "$T/out.md")" ]; then ok "example sections match the matcher output"; else ko "example sections differ from the matcher output"; fi
has "count on stderr" "7 pièces : 2 trouvées, 3 à vérifier, 2 manquantes ; 1 fichier(s) non rattaché(s)" "$(cat "$T/err")"
has "ambiguous name is à vérifier" "| \`facture_energie_aout2026_avec_RIB.pdf\` | Justificatif de domicile de moins de 3 mois ; RIB | à vérifier : le nom correspond à plusieurs pièces |" "$out"
has "keyword inside a word is à vérifier" "- **Dernier avis d'imposition** — \`avis_impots_2025.pdf\` : mot-clé trouvé seulement à l'intérieur d'un mot du nom" "$out"
has "unmatched file listed" "- \`scan_0042.pdf\`" "$out"
has "keyword shown for each match" "(mot-clé « lettre mission »)" "$out"

# matcher on a real folder: accents, case, subfolder, hidden and empty files
F="$T/dossier"; mkdir -p "$F/identite"
echo x > "$F/identite/Passeport.PDF"; echo x > "$F/Quittance_Loyer_Août.pdf"; echo x > "$F/rib.pdf"
echo x > "$F/Avis-d'Imposition 2025.pdf"; : > "$F/questionnaire.pdf"; echo x > "$F/.DS_Store"
out="$(python3 -I "$M" --liste "$L" --dossier "$F" 2>/dev/null)"
has "subfolder, case-insensitive match" "- **Pièce d'identité en cours de validité** — \`identite/Passeport.PDF\` (mot-clé « passeport »)" "$out"
has "accents and separators ignored" "- **Dernier avis d'imposition** — \`Avis-d'Imposition 2025.pdf\`" "$out"
has "empty file is à vérifier" "\`questionnaire.pdf\` : fichier vide (0 octet)" "$out"
if printf '%s\n' "$out" | grep -q DS_Store; then ko "hidden file skipped"; else ok "hidden file skipped"; fi
# everything matched: no verdict, the neutral line instead
printf 'RIB : rib\n' > "$T/one.txt"
out="$(python3 -I "$M" --liste "$T/one.txt" --dossier "$F" 2>/dev/null)"
has "nothing missing gives the neutral line" "Aucune pièce manquante d'après les noms de fichiers ; le contenu des fichiers reste à ouvrir et à contrôler." "$out"
if printf '%s\n' "$out" | grep -Eiq '\bcompl(et|ète)\b|conforme|validé'; then ko "matcher writes no verdict word"; else ok "matcher writes no verdict word"; fi
{ sed -n '1,/^## Correspondance/p' "$E" | sed '$d'; printf '%s\n\n' "$out"; sed -n '/^## Projet de mail/,$p' "$E" | sed '/^- Questionnaire/d; /^- Justificatif/d'; } > "$T/all.md"
expect "draft with nothing missing passes" 0 "$T/all.md" --liste "$T/one.txt"
# errors
printf 'RIB sans mots-clés\n' > "$T/bad.txt"
python3 -I "$M" --liste "$T/bad.txt" --dossier "$F" >/dev/null 2>&1; [ $? = 3 ] && ok "malformed checklist rejected" || ko "malformed checklist rejected"
printf 'RIB : rib\nrib : iban\n' > "$T/dup.txt"
python3 -I "$M" --liste "$T/dup.txt" --dossier "$F" >/dev/null 2>&1; [ $? = 3 ] && ok "duplicate item rejected" || ko "duplicate item rejected"
python3 -I "$M" --liste "$L" --dossier "$T/nope" >/dev/null 2>&1; [ $? = 2 ] && ok "missing folder errors" || ko "missing folder errors"
python3 -I "$M" --liste "$L" >/dev/null 2>&1; [ $? = 2 ] && ok "usage error" || ko "usage error"

# privacy: no network, no send, the matcher never opens client files
if grep -Ei 'urllib|socket|http\.client|requests|curl|wget|smtplib|sendmail|webhook|telegram|slack' "$D"/bin/*.py >/dev/null; then ko "network or send code in bin/"; else ok "no network or send code"; fi
opens="$(grep -c 'open(' "$M")"
[ "$opens" = 2 ] && ok "matcher opens only the checklist and the listing" || ko "matcher open() calls: $opens"
exit $fail
