# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M0 : contrôle SUCCES dans le clone neuf. En attente de validation visuelle de Julien. Ne pas passer à M1.

## Dernier contrôle
2026-10-11 11:42:46 M0 SUCCES erreurs=0 gate_sha256=55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb
(clone neuf, commit a886191)

## En cours
Corrections M0 demandées par Julien : taille 32-40 px, nage non raide, bras jamais verticaux, idle, casque et équipement, animation vivante, références, clone neuf.
Fait : clone neuf (défaut 1), taille (défaut 2), amplitude nage (défaut 3), bras (défaut 4), idle (défaut 5), palmes/sangles/dôme (défaut 6 partiel), ombrage 4 tons, contour sélectif, liseré clair, 3 itérations Aseprite.
Non fait : hublot avec cadre lisible, tuyau d'air lisible (voir blocages), bras de nage plus visibles, références 2 et 3.

## Défauts visuels restants (honnêtes)
- Casque : le cadre du hublot et les boulons ne se lisent pas à 37 px (4 tentatives annulées). Le hublot est une vitre cyan d'environ 4 px de large.
- Tuyau d'air : absent du rendu final (2 tentatives annulées, trop fin).
- Bras de nage : partiellement cachés derrière le torse ; la brassée reste peu lisible.
- Bouteilles : une barre sans valve ; reflet de 4 pixels seulement.
- Lampe : pas de lueur visible (tentative annulée).
- Jambes : rouge-prune foncé en nage (ombrage en 4 tons), à améliorer.
- Niveau : très loin d'un niveau Dead Cells (silhouette encore générique, animation de 8 images sans anticipation poussée).

## Blocage en cours
Limite de format : à 32-40 px de haut, tout élément plus fin que 2 px disparaît à la pixelisation.
- Cadre du hublot (tube 0,6 px, puis 2 px ; avant du verre ; métal sombre) : 4 tentatives, toutes annulées (entrées 15 à 18 du journal). Cause : le cadre est une barre fine vue de profil, son contraste ne suffit pas.
- Tuyau d'air (sombre puis clair, rayon 0,04) : 2 tentatives, annulées (entrées 26 et 27).
- Hublot clair (paliers 2 à 5) : annulé (entrée 24). Dôme plus grand : gardé (entrée 25).
- Lueur de la lampe (5 pixels) : annulée (entrée 31).
Prochaine hypothèse à tester seulement si Julien accepte un format plus grand (ex. 48 px) : cadre et valve visibles. Sinon, accepter la limite et le dire dans le RAPPORT.

## Tailles et amplitudes (tools/mesure/mesurer.py)
Avant M0 (entrée 1) : nage 44-45 px, idle 43-44 px, amplitude nage 0,402, idle 0,236.
Actuel (les 14 images) :
```
## nage (8 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| nage_01.png | 38 | 21 | 38 |
| nage_02.png | 37 | 22 | 37 |
| nage_03.png | 39 | 25 | 39 |
| nage_04.png | 39 | 25 | 39 |
| nage_05.png | 39 | 24 | 39 |
| nage_06.png | 38 | 26 | 38 |
| nage_07.png | 39 | 27 | 39 |
| nage_08.png | 39 | 25 | 39 |
plus grande dimension : min 37, max 39
amplitude nage : 0.533

## idle (6 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| idle_01.png | 17 | 37 | 37 |
| idle_02.png | 18 | 38 | 38 |
| idle_03.png | 17 | 38 | 38 |
| idle_04.png | 17 | 37 | 37 |
| idle_05.png | 17 | 37 | 37 |
| idle_06.png | 17 | 37 | 37 |
plus grande dimension : min 37, max 38
amplitude idle : 0.230
```
Cibles : taille 32-40 px sur chaque image (OK), amplitude nage >= 0,45 (0,533 : OK), amplitude idle >= 0,10 (0,230 : OK).

## Besoin de Julien
- Validation visuelle de M0 : planches `boards/plongeur_reference.png`, `boards/iterations/` et capture `shots/m0_plongeur_godot.png`.
- Références : une seule image libre (`ref_03_plongeur_stockholm_1951.jpg`). Wikimedia répond 429 aux autres tentatives (y compris celle de la session finale). Les adresses prévues sont dans `art/references/SOURCES.md`.
- Choix à valider : garder une image de référence téléchargée (BRIEF §5 autorise les références ; la consigne « rien de visuel ne se télécharge » vise les assets).
- Décision à prendre : accepter la limite de 2 px pour les détails fins (cadre, boulons, tuyau), ou autoriser une taille de sprite plus grande (48 px) pour les obtenir.

## Prochaine étape
Relancer le contrôle dans le clone neuf, mettre RAPPORT.md à jour, attendre la validation de Julien. Ne pas passer à M1.
