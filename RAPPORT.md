# RAPPORT.md — Phase M3 (biome 1 au niveau professionnel : radeau_surface et recif_peu_profond)

## Fait (vérifié)
- Créatures du biome 1 (poisson_volant, carangue_rayee, oursin_bombe, tortue_de_corail) : un script Blender chacune
  (`art/source/blender/<id>.py`), 18 images (nage 8, attaque 4, mort 6), pixelisées, feuille Aseprite à 3 étiquettes,
  3 itérations Aseprite avec planches (`boards/iterations/`). La tortue nage sur 8 images distinctes (vérifié sur pixels).
- Journal visuel des créatures : poisson_volant 20 entrées, carangue_rayee, oursin_bombe, tortue_de_corail (voir
  `art/journal/`). Entrée 15 du poisson réparée : son image pointait sur une copie de l'entrée 5 ; elle est remplacée
  par un rendu réel de l'état annulé (œil à l'ancienne position), empreinte unique (commit 05ff2aa).
- Combat dans le jeu : touche X, portée 26 px, 3 coups pour tuer le poisson volant ; étape robot `combattre` qui suit la
  créature à 18 px (distance réelle, relue à chaque pas). Robot : 13 étapes sur 13 (vérifié, commits 5d5409e et suivants).
- Fond d'eau et ciel en dégradé sur 300 m, teinte sous-marine plus claire. Mesure de la règle de capture (tools/mesure/
  captures.py) : couleur dominante de 6 à 16 % (seuil 40 %), pixels sous luminance 0,05 de 17 à 22 % (seuil 35 %), sur les
  18 captures. Planche avant/après : `boards/journal/captures_60m_descente_avant_apres.png` (entrée `art/journal/fond_eau.json`).
- Sons : 9 fichiers dans `assets/sons/`, sources et licences dans `CREDITS.md` (son_impact CC-BY-3.0, crédit obligatoire).
- Contrôle `python tools/gate.py M3` → SUCCES (commit c488e94, sortie complète ci-dessous).
- Clone neuf de la branche (commit c488e94, `git clone` dans un dossier vide) : `python tools/gate.py M3` → SUCCES, code de sortie 0.

## Non vérifié
- Les 9 sons n'ont été analysés que par leurs métadonnées (durée, niveau) : personne ne les a écoutés. Julien doit juger.
- Le crédit de son_impact n'est pas encore affiché dans le jeu (il est dans CREDITS.md seulement).
- L'autotile des tuilesets (47 cases) n'est pas branché dans `scripts/monde.gd` : les tuilesets sont générés, pas utilisés.
- Les fonds (8) sont des premières versions provisoires (`provisoire: true` dans le manifeste) ; les coques lointaines se lisent comme des boîtes.
- Captures de profondeur : le libellé « Vous êtes sur le radeau » reste affiché à 60 m (état HUD figé pendant la capture).
- Le .exe Windows n'est pas lancé (pas de Wine ici).

## Limites
- Les quatre changements du fond d'eau ont été faits ensemble, une seule planche avant/après : l'effet de chacun n'est pas
  isolé (les captures intermédiaires ont été écrasées). Noté dans le journal `fond_eau`.
- Le contrôle M3 ne juge pas la beauté : il vérifie des seuils (couleurs, tailles, journaux). Le niveau visuel reste en
  deçà de Dead Cells : silhouettes de créatures lisibles mais pas raffinées, fonds simples.
- Le robot dépend du timing (approche d'une créature qui bouge, remontées accidentelles) : deux corrections ont été
  nécessaires pendant M3 (approche par distance réelle, reprise après remontée au radeau).

## Écarts vers Dead Cells (par impact)
1. Fonds et décor : aplats et dégradés simples, pas de parallaxe travaillée ni de détail de récif.
2. Créatures : lisibles à x1, mais le poisson volant et la carangue manquent de finesse (nageoires, œil).
3. Son : 9 sons non écoutés, crédit en jeu absent.
4. Tuilesets : autotile non branché, donc pas de transitions de biome dans le jeu.

## Ce que Julien doit juger lui-même
- Les sons (écoute), le ressenti de l'eau sombre (teinte plus claire, est-ce le bon compromis ?), la lisibilité du poisson volant
  et de la carangue à x1.

gate.py SHA-256 : 55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb
Phase controlee : M3 (et toutes les precedentes)

Verifications reussies :
  [ok] outil godot : 4.4.1.stable.official.49a5bc7b6
  [ok] outil blender : Blender 5.2.1 LTS
  [ok] outil aseprite : Aseprite 1.3.18.6-dev
  [ok] recherche de dessin par code terminee
  [ok] provenance : 9 sources lues
  [ok] palette : 85 couleurs, 16 rampes
  [ok] Godot : projet charge sans erreur de script
  [ok] univers : 9 biomes, 66 objets, 45 recettes, 18 creatures, 3 boss, 21 quetes, 35 notes, 3 fins
  [ok] robot : 13 etapes exigees

==> M3 : SUCCES

# Archive — RAPPORT de la phase M2 (jeu jouable branché sur les données)

Commit testé dans le clone neuf : `15771fe` (branche `claude/cloches-varekh-dev-r716in`). Le commit suivant ne change que RAPPORT.md et ETAT.md.

## Fait (vérifié)
- `python tools/gate.py M2` : SUCCES dans le dépôt de travail et dans un clone neuf (sortie complète plus bas).
- Robot de test (tests/robot/robot.py) : 12 étapes sur 12, avec de VRAIES touches envoyées au serveur X (XTest) dans la fenêtre du jeu. Captures prises à chaque étape pendant le lancement (shots/robot/). Le rapport est tests/robot_rapport.json.
- Jeu : radeau de départ, plongée, nage, air (se vide sous l'eau, se remplit hors de l'eau), lampe, creusage d'une épave à l'aide de data/tuiles.json, ramassage, pose, fabrication depuis data/recipes.json (module de forge), sortie de l'eau sur le radeau, sauvegarde (F5) et chargement (F9).
- Aucun objet, recette, station, biome ni tuile n'est codé en dur : tout est lu dans data/*.json.
- Export (retouche 4) : tests/export/verifier_pck.sh → SUCCES. Le PCK est lancé avec le moteur (--main-pack), le radeau et les tuiles s'affichent, aucune erreur de script.
- Images provisoires (décor, radeau) : rendus Blender pixelisés, marqués PROVISOIRE dans art/manifest.json.

## Non vérifié
- Le fichier .exe Windows lui-même : non lancé (pas de Wine dans l'environnement). Seul le PCK est testé, avec le moteur Linux.
- Le plein écran, les touches configurables et les menus : prévus en M5.
- Le monde par chunks : la fenêtre d'affichage et les modifications par tuile existent, mais pas encore de chargement de chunks sur disque.

## Limites
- Décor provisoire (roche, récif, cuivre, sable, bois, tôle) et radeau : rendus Blender simples, à remplacer en M3.
- Pas de créatures, pas de combat (étape robot « combattre » : M3). La touche d'attaque n'a encore aucun effet.
- Les 12 étapes du robot sont des tests de fonctionnement, pas une partie complète.
- Les tuiles creusées dans l'épave sont les seules matières accessibles : la progression par palier n'est pas encore gardée dans le jeu (M3 et M4).
- Fenêtre de tuiles de 48 × 32 : l'affichage se recalcule quand le plongeur change de chunk de 16 tuiles.

## Sortie complète de `python tools/gate.py M2` (clone neuf, commit 15771fe)
```
gate.py SHA-256 : 55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb
Phase controlee : M2 (et toutes les precedentes)

Verifications reussies :
  [ok] outil godot : 4.4.1.stable.official.49a5bc7b6
  [ok] outil blender : Blender 5.2.1 LTS
  [ok] outil aseprite : Aseprite 1.3.18.6-dev
  [ok] recherche de dessin par code terminee
  [ok] provenance : 0 sources lues
  [ok] palette : 85 couleurs, 16 rampes
  [ok] Godot : projet charge sans erreur de script
  [ok] univers : 9 biomes, 66 objets, 45 recettes, 18 creatures, 3 boss, 21 quetes, 35 notes, 3 fins
  [ok] robot : 12 etapes exigees

==> M2 : SUCCES
```

---

# Archive — RAPPORT de la phase M1

## M1 (univers complet en données)

Commit testé dans le clone neuf : `0b9f456` (branche `claude/cloches-varekh-dev-r716in`). Le commit suivant ne change que RAPPORT.md et ETAT.md.

## Fait (vérifié)
- `python tools/gate.py M1` : SUCCES dans le dépôt de travail et dans un clone neuf (sortie complète plus bas).
- Univers en JSON : `data/lore.json`, `biomes.json` (9), `items.json` (66), `stations.json` (5), `recipes.json` (45), `creatures.json` (18), `bosses.json` (3), `quests.json` (21), `notes.json` (35), `endings.json` (3), `depart.json`.
- Progression simulée par le contrôle depuis le radeau : chaque objet est obtenable, chaque biome est accessible, chaque quête est faisable.
- Tranche verticale du jeu : radeau_surface et recif_peu_profond (tranche 1), fosse_sombre (tranche 2) avec le mini-boss gardien_cloche.
- `BIBLE.md` : concept, boucle, univers, progression (tableau des paliers 0 à 7), ton, références de qualité.
- Aucun code de jeu dans cette phase : Godot n'est pas modifié.

## Non vérifié
- La qualité d'écriture et la cohérence narrative : un contrôle humain ou un sous-agent relecteur est prévu en M6, il n'a pas été fait.
- L'équilibrage (quantités, coûts, durée de chaque palier) : non mesuré, seule la faisabilité est vérifiée.
- La lisibilité en jeu des noms et des descriptions : rien n'est encore affiché.

## Limites
- Les six biomes hors échantillon (foret_de_kelp, banc_de_verre, cheminee_thermale, plaine_abyssale, cite_engloutie, fond_du_signal) sont décrits en données mais ne sont pas construits en assets : leur construction est prévue en M3 et M4.
- Le champ `palier` des objets et des recettes est une indication : le contrôle ne vérifie que la simulation, et non la cohérence de chaque palier affiché avec `donne_palier`.
- Un seul mini-boss (gardien_cloche). Les deux autres boss sont des boss normaux.
- Les quêtes donnent des récompenses qui ouvrent parfois un outil avant son palier (par exemple le foret abyssal en récompense de la cité) : à rééquilibrer après les tests de jeu.

## Sortie complète de `python tools/gate.py M1` (clone neuf, commit 0b9f456)
```
gate.py SHA-256 : 55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb
Phase controlee : M1 (et toutes les precedentes)

Verifications reussies :
  [ok] outil godot : 4.4.1.stable.official.49a5bc7b6
  [ok] outil blender : Blender 5.2.1 LTS
  [ok] outil aseprite : Aseprite 1.3.18.6-dev
  [ok] recherche de dessin par code terminee
  [ok] provenance : 0 sources lues
  [ok] palette : 70 couleurs, 13 rampes
  [ok] Godot : projet charge sans erreur de script
  [ok] univers : 9 biomes, 66 objets, 45 recettes, 18 creatures, 3 boss, 21 quetes, 35 notes, 3 fins

==> M1 : SUCCES
```

---

# Archive — RAPPORT de la phase M0

## M0 (plongeur), troisième vague de corrections

Commit testé dans le clone neuf : `e9ec6c6` (branche `claude/cloches-varekh-dev-r716in`). Le commit suivant ne change que RAPPORT.md et ETAT.md.

## Fait (vérifié)
- Contrôle M0 dans un clone neuf du commit e9ec6c6 : SUCCES (sortie complète plus bas).
- Journal visuel : 64 entrées (47 gardées, 17 annulées), 64 images distinctes, 7 critères remplis par entrée (`art/journal/plongeur.json`).
- Taille : nage 37 à 39 px, idle 37 à 39 px (tools/mesure/mesurer.py) ; plage 32 à 40 respectée.
- Amplitudes : nage 0,591 (≥ 0,45), idle 0,366 (≥ 0,10).
- Nage : toutes les images à 39 px au plus (la vague précédente avait des images à 40 px ; corrigé par le cadrage 3,95).
- Respiration idle : le haut du casque varie de 2 px entre idle_01 (haut 13) et idle_05 (haut 11). Les bras suivent le buste.
- Bulle de respiration : sort de l'arrière du casque, monte de 0,18 unité pendant idle (journal 59, gardée).
- Silhouette de métier : lampe de casque agrandie (rayon 0,11 = 2 px), jaune sur l'eau bleue (journal 55, gardée).
- Retouches Aseprite gardées, chacune avec sa planche et son entrée, rejouées dans l'ordre sur les images finales :
  - it2 : vitre cyan franc, #9af0ea → #5cc8d0 (`boards/iterations/plongeur_it2.png`, journal 61) ;
  - it3 : reflet blanc ramené à 3 pixels en haut à gauche du hublot (`boards/iterations/plongeur_it3.png`, journal 62) ;
  - it4 : ombre sous le casque, 3 à 7 pixels par image passés à #8f2f2e (`boards/iterations/plongeur_it4.png`, journal 63).
- Planche finale : `boards/plongeur_reference.png` (références ref_03 et ref_05 à gauche, idle_01, idle_04, nage_01, nage_05 ×4 à droite, issus de la feuille finale).
- Capture Godot du jeu lancé : `shots/m0_plongeur_godot.png` (CAPTURE_OK).
- Manifeste `art/manifest.json` : les planches d'itération pointent vers it2, it3, it4.
- Export Windows : la note « à tester en M2 » reste dans ETAT.md ; le journal Godot affiche l'avertissement « this will not work on export » pour `Image.load_from_file` sur res://.

## Non vérifié
- Le hublot à x1 sur eau sombre : jugé sur les planches, pas validé par Julien.
- Le cadre du hublot (liseré) : non obtenu. Deux tentatives annulées (journal 60 et 64).
- Le tuyau d'air et les valves : annulés (journal 53 et 54), invisibles à x1.
- L'export Windows (`Image.load_from_file` dans un .exe) : à tester en M2.
- Les planches `boards/plongeur_base.png` et `boards/plongeur_modifie.png` datent de la première vague et ne sont pas à jour.

## Limites
- Le hublot fait environ 5 × 5 px sur les images idle et n'a pas de cadre continu : le critère « un inconnu doit dire un plongeur avec un hublot » n'est pas atteint de façon sûre sur eau sombre.
- La silhouette de métier repose sur la seule lampe.
- La bulle de respiration est petite (2 à 3 px) et monte peu (environ 3 px).
- Les palmes restent plus petites que les jambes.
- Les retouches Aseprite sont des pixels choisis sur les images (pas de dessin par code) ; elles sont à refaire si le rendu Blender change.

## Écarts vers Dead Cells (par impact)
1. Hublot et tête : un vrai dôme de verre avec cadre net et reflet, à x1. Actuellement un bloc cyan de 5 × 5 px.
2. Silhouette de métier : plusieurs détails (tuyau, valves, lampe) qui se lisent à x1. Actuellement la lampe seule.
3. Animation : anticipation plus travaillée ; la respiration est faible (2 px) et la bulle est petite.
4. Palmes : taille et forme plus marquées.
5. Ombrage : la combinaison reste en aplats ; peu de sensation de volume.

## Ce que Julien doit juger lui-même
- `boards/plongeur_reference.png` : le plongeur est-il reconnaissable comme plongeur avec un hublot, à ×4 et à x1 ?
- `boards/journal/plongeur_61.png`, `plongeur_62.png`, `plongeur_63.png` : les trois retouches gardées sont-elles visibles à x1 ?
- `shots/m0_plongeur_godot.png` : la capture dans le jeu lancé.
- Décision sur le hublot : accepter tel quel, ou demander une forme plus grosse dans Blender (autre passe).

## Sortie complète de `python tools/gate.py M0` (clone neuf, commit e9ec6c6)
```
gate.py SHA-256 : 55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb
Phase controlee : M0 (et toutes les precedentes)

Verifications reussies :
  [ok] outil godot : 4.4.1.stable.official.49a5bc7b6
  [ok] outil blender : Blender 5.2.1 LTS
  [ok] outil aseprite : Aseprite 1.3.18.6-dev
  [ok] recherche de dessin par code terminee
  [ok] provenance : 0 sources lues
  [ok] palette : 70 couleurs, 13 rampes
  [ok] Godot : projet charge sans erreur de script

==> M0 : SUCCES
```
