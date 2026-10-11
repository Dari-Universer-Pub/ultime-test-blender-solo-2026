# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M0 : corrections de Julien (2e vague) faites, contrôle SUCCES dans le clone neuf. EN ATTENTE de validation visuelle de Julien. Ne pas passer à M1.

## Dernier contrôle
(mis à jour après le contrôle dans le clone neuf, voir RAPPORT.md)

## Journal visuel
46 entrées : 36 gardées, 10 annulées. Images distinctes, SHA-256 vérifiés. Itérations Aseprite rejouées sur les images finales (planches boards/iterations/ it1 à it3).

## Corrections de la 2e vague (demande de Julien)
1. Nage illisible : FAIT. Bras sous le torse (brassée entre 0,5 et 1,5 rad), visibles, hors du corps. Jambes en trois tons oranges. Palmes turquoise-vert (teinte différente du pantalon).
2. Couleurs des membres : FAIT. Seuils des paliers remontés : le ton sombre n'occupe plus la majorité (combinaison : base 50 %, ombre 31 %, lumière 12 % en nage).
3. Casque : PARTIEL. Dôme de verre plus grand, cadre clair 1 px, reflets 2 px et 1 px. Le hublot cyan franc (tentative) est annulé ; le hublot reste la zone la plus faible du sprite à x1.
4. Références : FAIT avec 2 sources (la tentative Wikimedia répond encore 429 pour 2 autres images). Adresses dans art/references/SOURCES.md.
5. Export (à tester en M2) : voir section dédiée ci-dessous.
6. Animation : FAIT en partie. Nage avec une image de préparation (bras repliés) et deux images de glisse (bras allongés). Idle : respiration visible mais faible (1 px), sans bulles.

Acquis vérifiés à chaque changement (tools/mesure/mesurer.py) : taille 32-40 px sur chaque image (OK), amplitude nage >= 0,45 (0,590 : OK), amplitude idle >= 0,10 (0,304 : OK).

## Mesures finales (tools/mesure/mesurer.py)
```
## nage (8 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| nage_01.png | 37 | 22 | 37 |
| nage_02.png | 38 | 23 | 38 |
| nage_03.png | 40 | 24 | 40 |
| nage_04.png | 39 | 25 | 39 |
| nage_05.png | 39 | 24 | 39 |
| nage_06.png | 40 | 25 | 40 |
| nage_07.png | 40 | 25 | 40 |
| nage_08.png | 39 | 24 | 39 |
plus grande dimension : min 37, max 40
amplitude nage : 0.590

## idle (6 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| idle_01.png | 18 | 36 | 36 |
| idle_02.png | 19 | 37 | 37 |
| idle_03.png | 18 | 38 | 38 |
| idle_04.png | 16 | 37 | 37 |
| idle_05.png | 17 | 38 | 38 |
| idle_06.png | 17 | 37 | 37 |
plus grande dimension : min 36, max 38
amplitude idle : 0.304
```

## Tons de la combinaison (tools/mesure/tons.py)
```
## nage : pixels de combinaison 1128
  ton1   #5a2440 :   1.2 %
  ton2   #8f2f2e :  18.8 %
  ton3   #c95a2a :  26.8 %
  ton4   #f08a3a :  32.4 %
  ton5   #ffc070 :  20.7 %
  tons utilises : 5 ; le plus sombre utilise est majoritaire : non
## idle : pixels de combinaison 782
  ton1   #5a2440 :   0.4 %
  ton2   #8f2f2e :   4.2 %
  ton3   #c95a2a :  31.6 %
  ton4   #f08a3a :  51.8 %
  ton5   #ffc070 :  12.0 %
  tons utilises : 5 ; le plus sombre utilise est majoritaire : non
```

## Défauts visuels restants (honnêtes)
- Casque : hublot cyan peu contrasté à x1, reflets faibles (1 à 2 px).
- Bouteilles : pas de valve, reflet d'un pixel.
- Respiration idle faible (1 px) ; pas de bulles.
- Animation : pas d'anticipation travaillée au-delà d'une image de préparation.
- Palmes : turquoise, plus petites que les jambes.
- Niveau : loin de Dead Cells (silhouette encore générique).

## Blocage en cours
Aucun blocage ouvert. Hypothèses testées sur le casque (annulées) : cadre métallique à 0,6 px, 2 px, en avant du verre, métal sombre ; tuyau d'air sombre et clair ; verre clair (paliers 2-5) ; cyan franc (paliers 1-4). Cause commune : à 37 px, un détail de moins de 2 px se perd, et un contraste faible ne suffit pas.

## Export Windows (A TESTER EN M2)
`Image.load_from_file` sur `res://` : fonctionne dans l'éditeur et depuis un clone neuf (vérifié en M0), mais HYPOTHESE NON VERIFIEE dans l'export .exe : les PNG non importés ne sont pas forcément dans le PCK. A tester en M2, avec une solution qui marche aussi depuis un clone neuf.

## Besoin de Julien
- Valider M0 : planches `boards/plongeur_reference.png`, `boards/iterations/` et capture `shots/m0_plongeur_godot.png`.
- Le casque reste limité à 37 px : accepter (option a, décidée) ou revoir le niveau de détail.
- Les références sont inspiration seulement.

## Prochaine étape
Attendre la validation de Julien. Après « M0 validé » : M1.
