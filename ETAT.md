# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M0 : troisième vague de corrections (casque, silhouette de métier, respiration, nage, retouches Aseprite) faite. Contrôle SUCCES dans le dépôt de travail ; contrôle dans le clone neuf : voir la section « Dernier contrôle ». EN ATTENTE de validation visuelle de Julien. Ne pas passer à M1.

## Dernier contrôle
- Dépôt de travail (avant commit) : `python tools/gate.py M0` → SUCCES (gate.py SHA-256 55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb).
- Clone neuf (commit e9ec6c6, branche claude/cloches-varekh-dev-r716in) : SUCCES. Sortie complète dans RAPPORT.md (section « Sortie complète »).

## Journal visuel
64 entrées : 47 gardées, 17 annulées. 64 images distinctes, SHA-256 vérifiés, 7 critères remplis par entrée.
Entrées de cette vague : 54 (valves, annulé), 55 (lampe agrandie, gardé), 56 (cadrage, gardé), 57 (respiration, gardé), 58 (bulle sur la visière, annulé), 59 (bulle à l'arrière du casque, gardé), 60 (liseré, tentative 1, annulé), 61 (cyan franc, gardé), 62 (reflet franc, gardé), 63 (ombre sous le casque, gardé), 64 (liseré, tentative 2, annulé).

## Corrections de la 3e vague (demande de Julien)
1. Casque, hublot : FAIT EN PARTIE. Le verre est cyan franc (#5cc8d0, Aseprite it2, entrée 61) ; le reflet blanc est ramené à 3 pixels en haut à gauche (it3, entrée 62) ; l'ombre sous le casque est faite (it4, entrée 63). Le hublot mesure environ 5 × 5 px sur les images idle, mais le cadre clair ou sombre n'est PAS continu : le liseré est annulé (entrées 60 et 64). Le hublot n'atteint donc pas encore la demande « un inconnu doit dire un plongeur avec un hublot » à x1 sur eau sombre.
2. Silhouette de métier : FAIT PAR LA LAMPE (entrée 55), lampe jaune de rayon 0,11 (2 px) sur l'eau bleue : contraste fort, lisible à x1. Les valves (entrée 54) et le tuyau d'air (entrée 53) sont annulés : invisibles à x1.
3. Respiration idle : FAIT. Le haut du casque varie de 2 px entre idle_01 (haut 13) et idle_05 (haut 11) ; le buste bouge de 0,16 rad ; les bras suivent (enfants du buste). Bulle de respiration : sort de l'arrière du casque, montée de 0,18 unité (entrée 59). La bulle est petite (2 à 3 px).
4. Nage : FAIT. Toutes les images de nage font 37 à 39 px (vague précédente : 37 à 40 px).
5. Retouches Aseprite : 3 retouches gardées, chacune avec sa planche et son entrée (it2 cyan franc, it3 reflet franc, it4 ombre sous le casque), rejouées sur les images finales (feuille exportée après it1 à it4 dans l'ordre). Le liseré du hublot n'est pas gardé (deux tentatives annulées).
6. Export Windows : NOTE CONSERVÉE (voir section dédiée). Le journal du lancement Godot affiche : « Loaded resource as image file, this will not work on export » pour res://assets/sprites/plongeur/plongeur.png. À tester en M2.
7. Références : inchangées (2 sources, adresses dans art/references/SOURCES.md).

Acquis vérifiés à chaque changement (tools/mesure/mesurer.py) : taille 32-40 px (OK : nage 37-39, idle 37-39) ; amplitude nage >= 0,45 (0,591 : OK) ; amplitude idle >= 0,10 (0,366 : OK).

## Mesures finales (tools/mesure/mesurer.py sur art/pixel/plongeur)
```
## nage (8 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| nage_01.png | 37 | 21 | 37 |
| nage_02.png | 38 | 22 | 38 |
| nage_03.png | 39 | 22 | 39 |
| nage_04.png | 39 | 24 | 39 |
| nage_05.png | 38 | 24 | 38 |
| nage_06.png | 39 | 24 | 39 |
| nage_07.png | 38 | 23 | 38 |
| nage_08.png | 38 | 23 | 38 |
plus grande dimension : min 37, max 39
amplitude nage : 0.591

## idle (6 images)
| image | largeur | hauteur | plus grande dimension |
|---|---|---|---|
| idle_01.png | 19 | 37 | 37 |
| idle_02.png | 20 | 37 | 37 |
| idle_03.png | 18 | 38 | 38 |
| idle_04.png | 17 | 38 | 38 |
| idle_05.png | 17 | 39 | 39 |
| idle_06.png | 17 | 39 | 39 |
plus grande dimension : min 37, max 39
amplitude idle : 0.366
```

## Tons de la combinaison (tools/mesure/tons.py)
```
## nage : pixels de combinaison 1075
  ton1 #5a2440 : 1.0 %   ton2 #8f2f2e : 17.5 %   ton3 #c95a2a : 30.4 %   ton4 #f08a3a : 31.3 %   ton5 #ffc070 : 19.8 %
  tons utilises : 5 ; le plus sombre utilise est majoritaire : non
## idle : pixels de combinaison 745
  ton1 #5a2440 : 0.1 %   ton2 #8f2f2e : 3.8 %   ton3 #c95a2a : 33.2 %   ton4 #f08a3a : 50.5 %   ton5 #ffc070 : 12.5 %
  tons utilises : 5 ; le plus sombre utilise est majoritaire : non
```

## Défauts visuels restants (honnêtes)
- Casque : hublot ~5 × 5 px sur idle, cyan franc mais sans cadre continu ; le liseré n'est pas réussi. Pas assez de contraste sur eau sombre pour « un inconnu doit dire un plongeur avec un hublot » : jugement à faire par Julien.
- Silhouette de métier : seulement la lampe. Pas de tuyau ni de valve lisible.
- Bulle de respiration : petite (2 à 3 px), elle monte peu (environ 3 px).
- Palmes : turquoise, plus petites que les jambes.
- Planches `boards/plongeur_base.png` et `boards/plongeur_modifie.png` : de la première vague, PAS mises à jour. Ne pas les prendre pour l'état actuel ; la planche finale est `boards/plongeur_reference.png`.
- Niveau : loin de Dead Cells (silhouette encore générique).

## Blocage en cours
Aucun blocage ouvert. Hypothèses testées sur le liseré du hublot (annulées, entrées 60 et 64) : cadre sombre 2 px (trop court), cadre sombre sur les pixels clairs du bord (1 à 3 px par image, discontinu). Cause : le bord du hublot touche le casque et le liseré clair sur un très petit nombre de pixels ; un cadre continu demande de changer la forme du hublot dans Blender, pas seulement sa couleur. Hypothèses testées sur la silhouette de métier (annulées) : tuyau d'air clair (entrée 53), valves de métal (entrée 54).

## Export Windows (A TESTER EN M2)
`Image.load_from_file` sur `res://` : fonctionne dans l'éditeur et depuis un clone neuf (vérifié en M0), mais HYPOTHÈSE NON VÉRIFIÉE dans l'export .exe : les PNG non importés ne sont pas forcément dans le PCK. Le journal Godot affiche déjà l'avertissement « this will not work on export ». À tester en M2, avec une solution qui marche aussi depuis un clone neuf.

## Besoin de Julien
- Valider M0 : `boards/plongeur_reference.png` (références + rendu final), `boards/iterations/` (it2, it3, it4), capture `shots/m0_plongeur_godot.png`.
- Décider du hublot : le cadre clair ou sombre continu ne tient pas à x1 avec la forme actuelle. Accepter tel quel, ou demander une forme de hublot plus grosse dans Blender (autre passe).
- Les références sont inspiration seulement.

## Prochaine étape
Attendre la validation de Julien. Après « M0 validé » : M1.
