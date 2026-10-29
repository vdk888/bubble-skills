> **BROUILLON — préparé par un assistant, à relire par le cabinet. L'outil prépare, vous validez. Tri établi d'après les expéditeurs et des mots-clés, à contrôler. Aucun envoi.**

<!-- EXEMPLE FICTIF : boîte mail, expéditeurs, contacts et messages inventés pour illustrer le format. -->

# Tri de la boîte mail du cabinet

- **Boîte lue :** fictional-boite.mbox (boîte fictive)
- **Liste des contacts :** fictional-contacts.csv (fictive)
- **Préparé le :** 2026-10-29
- **Brouillons de réponse :** brouillons/ (6 fichiers)

## Règle appliquée

Boîte lue : fictional-boite.mbox (mbox). Chaque message reçoit une catégorie d'après son expéditeur : Clients, Partenaires ou Administratif si l'adresse ou son domaine figure dans la liste des contacts du cabinet (fictional-contacts.csv) ou si le domaine est celui d'une administration connue ; Information pour les listes de diffusion, les réponses automatiques et les adresses sans réponse ; À classer sinon. L'adresse affichée n'est pas vérifiée. Urgence haute : réclamation, demande d'opération sur un contrat, mot d'urgence ou de délai, vigilance ; basse : Information ; normale sinon. Brouillon de réponse seulement pour un expéditeur de la liste des contacts, jamais pour un expéditeur inconnu, une information ou un message « vigilance ». Les pièces jointes ne sont pas ouvertes.

## Tri du courrier

| Réf. | Reçu le | Expéditeur | Objet | Catégorie | Type d'expéditeur | Urgence | Raison | Brouillon |
|------|---------|------------|-------|-----------|-------------------|---------|--------|-----------|
| M02 | 2026-10-27 | @messagerie.example | « Rachat partiel sur mon contrat » | Clients | client (liste) | haute | adresse dans la liste des contacts ; motif : opération (« rachat ») | M02-reponse.md |
| M03 | 2026-10-28 | @messagerie.example | « Réclamation : frais prélevés sur mon relevé » | Clients | client (liste) | haute | adresse dans la liste des contacts ; motif : réclamation (« reclamation ») | M03-reponse.md |
| M06 | 2026-10-29 | @association-pro.example | « Appel de cotisation 2027 à régler avant le 30/11/2026 » | Administratif | administratif (liste) | haute | domaine @association-pro.example dans la liste des contacts ; motif : administratif (« cotisation ») ; mot « avant le » | M06-reponse.md |
| M07 | 2026-10-29 | @banque-fictive.example | « Changement de RIB urgent » | À classer | inconnu | haute | expéditeur absent de la liste des contacts ; motif : vigilance (« coordonnées bancaires + changement ») ; vigilance : demande de coordonnées bancaires, de virement ou de code, à vérifier par téléphone à un numéro connu, pas de brouillon ; mot « urgent » ; adresse de réponse sur un autre domaine (@autre-domaine.example) | non |
| M01 | 2026-10-26 | @messagerie.example | « Demande de rendez-vous » | Clients | client (liste) | normale | adresse dans la liste des contacts ; motif : rendez-vous (« rendez-vous ») | M01-reponse.md |
| M04 | 2026-10-28 | @assureur-fictif.example | « Bordereau de commissions du troisième trimestre » | Partenaires | partenaire (liste) | normale | domaine @assureur-fictif.example dans la liste des contacts ; motif : autre ; 1 pièce jointe non ouverte | M04-reponse.md |
| M08 | 2026-10-29 | @messagerie.example | « Premier contact : rendez-vous ? » | À classer | inconnu | normale | expéditeur absent de la liste des contacts ; motif : rendez-vous (« rendez-vous ») ; expéditeur hors liste des contacts, pas de brouillon | non |
| M09 | 2026-10-29 | @messagerie.example | « Pièces demandées » | Clients | client (liste) | normale | adresse dans la liste des contacts ; motif : documents (« pieces demandees ») ; 1 pièce jointe non ouverte | M09-reponse.md |
| M05 | 2026-10-28 | @plateforme-fictive.example | « La lettre de la plateforme, novembre 2026 » | Information | envoi automatique | basse | liste de diffusion, réponse automatique ou adresse sans réponse ; motif : autre | non |
| M10 | 2026-10-29 | @plateforme-fictive.example | « Votre relevé de situation est disponible » | Information | envoi automatique | basse | liste de diffusion, réponse automatique ou adresse sans réponse ; motif : documents (« releve ») | non |

## Réponses à préparer

- **M02** — Clients, urgence haute ; brouillon M02-reponse.md
- **M03** — Clients, urgence haute ; brouillon M03-reponse.md
- **M06** — Administratif, urgence haute ; brouillon M06-reponse.md
- **M01** — Clients, urgence normale ; brouillon M01-reponse.md
- **M04** — Partenaires, urgence normale ; brouillon M04-reponse.md
- **M09** — Clients, urgence normale ; brouillon M09-reponse.md

## Sans brouillon

- **M07** — À classer, urgence haute ; vigilance, à vérifier par téléphone
- **M08** — À classer, urgence normale ; expéditeur hors liste des contacts, pas de réponse proposée
- **M05** — Information, urgence basse ; information, pas de réponse proposée
- **M10** — Information, urgence basse ; information, pas de réponse proposée

## À vérifier

Aucun message à vérifier.

## Limites

Ce tri est établi d'après l'adresse de l'expéditeur, la liste des contacts du cabinet et des mots-clés de l'objet et du début du message. L'adresse affichée d'un expéditeur n'est pas vérifiée : elle peut être imitée. Un message peut être mal classé ou son urgence mal estimée : le cabinet relit chaque message dans sa messagerie. Le repérage « vigilance » repose lui aussi sur des mots-clés et reste incomplet : son absence ne signifie pas qu'un message est sûr, et toute demande touchant des coordonnées bancaires, un virement ou un code se vérifie par téléphone à un numéro connu. Aucun brouillon n'est préparé pour un expéditeur absent de la liste des contacts. Les pièces jointes ne sont pas ouvertes. Les réponses sont des brouillons : aucun message n'est envoyé par l'outil, rien n'est confirmé ni exécuté. Ce brouillon ne donne aucun conseil en investissement.

## Relecture (cabinet)
- [ ] Messages d'urgence haute relus en premier dans la messagerie
- [ ] Messages « vigilance » : expéditeur rappelé à un numéro connu, aucune coordonnée bancaire modifiée sur la foi d'un e-mail
- [ ] Messages « À classer » et « À vérifier » ouverts et classés par le cabinet
- [ ] Brouillons de réponse relus, complétés et envoyés par le conseiller seulement
