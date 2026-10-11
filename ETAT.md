# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M3 (biome 1 au niveau professionnel : radeau_surface et recif_peu_profond). M2 SUCCES (clone neuf, 15771fe) ; retouches 1 à 3 et 5 faites (169f712). Sons et musique : sous-agent en cours (assets/sources/, PROVENANCE.json : ne pas toucher à ces fichiers pendant ce temps).

### Plan M3 (cases à cocher, mises à jour au fil du travail)
- [x] plongeur : tags creusage 6, attaque 6, saut 4, degats 3, mort 8 (commit dbca5b1 ; feuille à 41 images, 7 étiquettes, nage 37-39 px, amplitude 0,569). Défauts notés au journal (entrée 79) : creusage et dégâts trop semblables d'une image à l'autre, saut 3 à revoir.
- [ ] créatures du biome 1 (poisson_volant, carangue_rayee, oursin_bombe, tortue_de_corail) : nage 8, attaque 4 (geste d'avertissement), mort 6 ; chacune : script Blender, 6 entrées de journal, 3 planches d'itération. État : poisson_volant (2 entrées, rendu complet à faire), carangue_rayee (4 entrées, rendu complet à faire), oursin_bombe (1 entrée, rendu complet en cours), tortue_de_corail (pas commencée)
- [ ] tuilesets 47 cases : radeau_surface, recif_peu_profond
- [ ] fonds (parallaxe) : 4 par biome
- [ ] props : 12 par biome
- [ ] effets : 8 au moins (type effet)
- [~] sons : 9 fichiers téléchargés et vérifiés (PROVENANCE.json, SHA-256 OK, commit 235c6ff). Intégration dans le jeu pas encore faite ; son_impact est CC-BY-3.0 et doit être crédité.
- [ ] jeu : créatures lues depuis data/creatures.json, combat (touche attaque), autotile, captures de profondeur (0, 30, 60, 100 m ; descente/remontée ; lampe/sans) et de biome
- [ ] robot : étape « combattre » ajoutée
- [ ] python3 tools/gate.py M3 → SUCCES, clone neuf, RAPPORT, commit, push

## Feuille de route (validée par Julien)
- M2 : jeu jouable branché sur data/*.json, robot en vraies touches (tests/robot/), export PCK testé.
- Retouches obligatoires (avant M3) : hublot, tuyau/valves, relief du corps, planches périmées.
- M3 : biome 1 (radeau_surface, recif_peu_profond) au niveau pro : tuilesets, fonds, props, créatures, effets, sons, captures.
- M4 : biome 2 (fosse_sombre), mini-boss gardien_cloche, 3 variantes de scaphandre, 15 effets, 14 sons.
- M5 : menus, options, pause, icône, export Windows dans builds/, PLAYTEST.md et PLAYTEST_JOURNAL.md.
- M6 : relecture par un sous-agent indépendant (RELECTURE.md), corrections, RAPPORT.md final.

## Dernier contrôle
- M2, dépôt de travail : `python tools/gate.py M2` → SUCCES (robot : 12 étapes sur 12, captures prises pendant ce lancement).
- M2, clone neuf (commit 15771fe, branche claude/cloches-varekh-dev-r716in) : SUCCES. Sortie complète dans RAPPORT.md (section M2).
- Test d'export (retouche 4) : `bash tests/export/verifier_pck.sh` → SUCCES (PCK lancé avec le moteur, radeau et tuiles affichés, 0 erreur de script). Le .exe Windows n'est pas lancé (pas de Wine ici).

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

## Retouches obligatoires (à traiter AVANT la phase M3)
Demandées par Julien à la validation de M0. Statut à tenir à jour (journal : art/journal/plongeur.json, entrées 65 à 78).
1. Hublot : FAIT EN PARTIE. Vitre agrandie (rayon 0,19 -> 0,24 ; entrée 65) et anneau métallique continu, 2 px, posé devant le casque (entrées 66 et 67). Le cadre est continu sur tout le pourtour. Limite : le bleu acier se perd un peu sur eau sombre (à juger par Julien). Les deux tentatives de liseré Aseprite restent annulées (entrées 60, 64) : le cadre est maintenant géométrique, dans Blender.
2. Silhouette de métier : FAIT (entrée 73, gardée). Tuyau d'air crème de 2 à 3 px, du bas du casque à la taille, devant le torse. Quatre tentatives annulées avant (entrées 68 à 72) : anse au-dessus du casque, trajet caché par les bouteilles en nage, manomètre caché par le bras. Possiblement lu comme une bretelle : à confirmer par Julien. La lampe (entrée 55) reste en détail complémentaire.
3. Relief du corps : PARTIEL. Combinaison à quatre tons (2 à 5) et seuils de lumière répartis (entrées 74 à 75). Casque et bulle gagnent du volume ; torse et jambes restent faiblement marqués. À reprendre si Julien le juge insuffisant.
4. Export : FAIT en M2. Constat : `Image.load_from_file` ne marche PAS dans l'export (les PNG bruts ne sont pas exportés). Solution : images importées par Godot et chargées avec `load()`, cache d'import versionné pour la clone neuve, données JSON lues par FileAccess. Test : tests/export/verifier_pck.sh (SUCCES). Le .exe Windows lui-même reste à lancer sur Windows.
5. Planches périmées : FAIT. `boards/plongeur_base.png` = pixelisation brute du rendu Blender (avant retouches Aseprite) ; `boards/plongeur_modifie.png` = version actuelle (feuille finale). La toute première planche de M0 n'existe plus : la base est donc la pixelisation brute actuelle.
Retouches Aseprite rejouées sur les images finales : itération 2 (vitre cyan, entrée 76), 3 (reflet, entrée 77), 4 (ombre sous le casque, entrée 78). Itération 1 remplacée par le cadre dans Blender.
Acquis vérifiés après ces retouches : nage 37 à 39 px, idle 37 à 39 px ; amplitude nage 0,575 (>= 0,45) ; amplitude idle 0,371 (>= 0,10) ; contrôle M2 SUCCES dans le dépôt (robot 12/12).

## Besoin de Julien
Rien pour M1 (M0 validée par Julien). Les retouches obligatoires ci-dessus restent à faire avant M3.

## Prochaine étape
Rien à lancer : M1 terminée, Julien décide de la suite. Les retouches obligatoires ci-dessus restent à faire avant M3.
