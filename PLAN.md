# PLAN.md — Le premier jet de LES CLOCHES DE VAREKH, en 7 phases

Ce n'est pas une suite de petits projets : c'est UN seul jeu, construit couche par couche.
Chaque phase s'appuie sur la précédente et ne la casse pas (le contrôle de la phase N revérifie
toutes les phases avant N). Les identifiants définis en M1 (biomes, créatures, objets…) sont ceux
qu'utilisent le code (M2) et les assets (M3, M4) : un sprite de créature porte l'`id` de sa créature.

À la fin de M6 :
- **l'échantillon jouable** (radeau + surface, 2 biomes, 1 mini-boss) est au niveau professionnel :
  assets, nature, créatures, animations, lumière, effets, sons, sensations, tout est vraiment là ;
- **tout le reste du jeu** (8 à 10 biomes, paliers jusqu'au sous-marin géant, boss, quêtes, notes,
  fins) existe en données JSON riches, reliées et validées. Ajouter du contenu = ajouter des données.

Commande de contrôle : `python tools/gate.py M0` … `python tools/gate.py M6`.

---

## M0 — Outils, palette et chaîne d'assets prouvée sur le plongeur — ARRÊT POUR VALIDATION

Pourquoi en premier : tout le style du jeu sortira de cette chaîne. Si elle ne marche pas sur le
plongeur, rien ne marchera ensuite. C'est ici que tu montes ta propre chaîne Blender et que les blocages se règlent, une
fois pour toutes, avec la règle d'or des blocages (AGENTS.md).

1. `git init`, `.gitignore` (`.godot/`, `builds/`). Les archives de `assets/sources/` peuvent être
   ignorées par git mais doivent rester sur le disque (le contrôle vérifie leur SHA-256).
2. Contrôle des outils : `tools/outils.json` (déjà rempli) ; `gate.py` lance les `--version`.
3. Palette `art/palette.json` : rampes de 5 à 7 tons par matière, 64 à 96 couleurs au total,
   décalage de teinte d'au moins 15° le long de chaque rampe (ombres vers bleu-violet, lumières vers
   jaune chaud), pas de noir pur. Format : `{"rampes": {"peau": ["#..", ...], ...}}`. STYLE.md chiffré.
4. Assets : AUCUN outil d'assets n'est fourni et aucun modèle n'est téléchargé. Tu construis le plongeur toi-même
   dans Blender, par un script `art/source/blender/plongeur.py` (`blender -b --python ...`) qui refait tout de zéro :
   modèle, matériaux, squelette, animations, caméra, lumière, rendu.
5. Références : cherche 2 ou 3 images libres de scaphandrier (silhouette, proportions, couleurs), range-les dans
   `art/references/` avec leur adresse. On s'inspire, on ne copie jamais. Pose-les à côté de ton rendu sur
   `boards/plongeur_reference.png` (le contrôle l'exige).
6. Le plongeur : un corps continu (pas un assemblage visible de cubes et de sphères), casque à hublot cerclé, bague de
   col, bouteilles, lampe ; animations **`nage` (8 images)** et **`idle` (6 images)** par os. Rendu à la caméra
   orthographique de profil, puis pixelisation par TON script dans `tools/pixelisation/` : réduction, quantification
   aux rampes de `art/palette.json`, contour. Le plongeur fait **32 à 40 px** et remplit sa case ; aucun pixel hors
   palette. Planches : `boards/plongeur_base.png` (premier rendu), `boards/plongeur_modifie.png` (version actuelle).
7. Une seule modification à la fois (forme, couleur, rendu, pixelisation), puis rendu et planche, et tu REGARDES
   (règle de l'œil). Feuille de sprites dans `assets/sprites/plongeur/`, finition Aseprite.
8. Journal visuel `art/journal/plongeur.json` : une entrée par changement regardé, avec la planche
   (`tools/planches/comparer.py`), les 7 critères remplis par une phrase précise, puis `garde` ou `annule`.
   Il faut au moins 6 entrées. Ton sprite doit tenir la comparaison avec les références.
9. Godot : une scène minimale montre le plongeur animé dans l'eau ; capture prise PAR GODOT
   (`get_viewport().get_texture().get_image().save_png`) dans `shots/m0_plongeur_godot.png`.
10. Tiens à jour `art/manifest.json` et `PROVENANCE.json` toi-même (format plus bas).
11. `python tools/gate.py M0` → `SUCCES` → commit → **tu t'arrêtes** et tu écris dans `ETAT.md` :
    « M0 terminé, en attente de validation visuelle ». Julien regarde les planches avant la suite.

## M1 — L'univers complet en données (aucun code de jeu dans cette phase)

C'est une phase à part entière, aussi importante que les assets. Tu conçois TOUT l'univers du jeu
final, pas un squelette. Schéma exact et exigences : `docs/DONNEES.md`. Ordre :

1. Lore : la civilisation disparue, sa chute, le signal, une chronologie, les factions, un glossaire.
2. Biomes (8 à 10) du radeau aux abysses : profondeurs, palier d'équipement requis, identité de
   couleur, ressources, créatures, points d'intérêt. Marque `tranche: 1` (surface + peu profond) et
   `tranche: 2` (le biome plus sombre de l'échantillon).
3. Progression : paliers 0 → 7 au moins, du scaphandre de toile au sous-marin géant ; chaque
   équipement qui ouvre une profondeur porte `donne_palier`.
4. Objets, stations de fabrication, recettes (avec ingrédients réels), véhicules.
5. Créatures (silhouette, comportement, taille, danger, butin) et boss (phases, butin), dont le
   mini-boss de l'échantillon.
6. Quêtes (prérequis, objets requis, récompenses), notes cachées (lore, indices de fin), 3 fins.
7. `BIBLE.md` complète : concept, boucle de jeu, univers, progression, ton, références de qualité.
8. `python tools/gate.py M1` → `SUCCES`. Le contrôle simule la progression : en partant du radeau,
   chaque objet doit être obtenable, chaque biome atteignable, chaque quête faisable.

## M2 — Le jeu jouable, branché sur les données

1. Code Godot qui LIT les JSON de M1 (aucun objet, recette ou créature codé en dur).
2. Contrôles complets (BRIEF §8), monde en tuiles modifiables par chunks, radeau, plongée,
   oxygène, lampe, creuser, poser, ramasser, inventaire, fabrication depuis `recipes.json`,
   sauvegarde et rechargement. Le plongeur est celui de M0.
3. Ce qui n'est pas encore poli utilise de VRAIS sprites dans le style (rendu Blender simple ou
   Aseprite simple), marqués PROVISOIRE dans `art/manifest.json` ; jamais de rectangle.
4. Robot de test avec de vraies touches dans une vraie fenêtre, dans `tests/robot/`. Ajoute sa
   commande dans `tools/outils.json` sous la clé `robot`. Il écrit `tests/robot_rapport.json` :
   `{"etapes": [{"nom": "plonger", "ok": true, "capture": "shots/robot/plonger.png", "detail": ""}, …]}`.
   Étapes exigées en M2 : `demarrer_radeau, plonger, nager, oxygene, lampe, creuser, poser,
   ramasser, fabriquer, sortir_eau_radeau, sauvegarder, recharger`. Le contrôle lance le robot
   lui-même et refuse tout rapport ou capture qui ne vient pas de ce lancement.
5. `python tools/gate.py M2` → `SUCCES`.

## M3 — Biome 1 au niveau professionnel (surface + radeau + peu profond)

Pour chaque biome `tranche: 1` : tuiles autotile 47 + variantes (`type: tuileset`), au moins
4 plans de fond en parallaxe (`fond`), au moins 12 props (`prop`), chaque créature du biome en
sprite vivant CONSTRUIT par toi dans Blender (nage 8, attaque 4 avec geste d'avertissement, mort 6), combat
(étape robot `combattre`), au moins 8 effets (`effet`), 8 sons et 1 musique dans `PROVENANCE.json`,
lumière continue de profondeur (BRIEF §7). Plongeur complet : creusage 6, attaque 6, saut 4,
dégâts 3, mort 8. Captures prises par Godot :
`shots/profondeur/<p>m_<descente|remontee>_<lampe|sans>.png` pour p = 0, 30, 60, 100, 150, 250, 400
jusqu'à la profondeur max de la tranche, et `shots/biomes/<id>.png`. Le contrôle les mesure
(pas de noir pur, couleur dominante < 40 %, moins de 35 % de pixels très sombres hors la plus profonde).

## M4 — Biome 2 et mini-boss

Même exigence pour les biomes `tranche: 2`, plus le mini-boss (sprite vivant construit dans Blender, attaque, mort,
au moins une animation `phase2…`), étape robot `mini_boss`, 3 variantes de scaphandre du
plongeur (`data_id` commençant par `plongeur`), 15 effets, 14 sons.

## M5 — Menus, options, sauvegarde, icône, export

Menu complet, options (volumes, touches, plein écran, résolution, langue), pause Échap partout,
`icon.ico` (tête du plongeur, 16 à 256 px), export Windows dans `builds/`, `PLAYTEST.md`,
au moins deux parties jouées dans `PLAYTEST_JOURNAL.md` (`## Partie 1`, `## Partie 2`). Étapes robot :
`menu_jouer, menu_continuer, menu_options, pause_echap, plein_ecran, touches`.

## M6 — Finition et relecture indépendante

Un sous-agent qui n'a pas fait le travail lance le jeu, regarde les captures et les planches,
cherche les défauts et écrit `RELECTURE.md`. Tu corriges. `RAPPORT.md` final avec les sections
Fait / Non vérifié / Limites / Écarts vers Dead Cells (classés par impact) et la liste de ce que
Julien doit juger lui-même (sons, ressenti, beauté).

---

## Formats communs

`PROVENANCE.json` :
```json
{"sources": [{"id": "<id_source>", "type": "modele3d", "url": "<adresse exacte de la page>",
  "licence": "CC0", "auteur": "<auteur>", "fichier": "assets/sources/<id_source>/<archive>",
  "sha256": "…", "page_licence": "assets/sources/<id_source>/licence.html"}]}
```
`type` : `modele3d`, `pack2d`, `son`, `musique`, `police`. Licences : CC0, CC-BY (3.0/4.0), OFL.

`art/manifest.json` (un objet par sprite du jeu) :
```json
{"sprites": [{"id": "plongeur", "data_id": "plongeur", "type": "vivant", "filiere": "construit", "script": "art/source/blender/plongeur.py",
  "biome": null, "provisoire": false, "sources": ["<id_source>"],
  "blend": "art/source/blender/plongeur.blend", "aseprite": "art/source/aseprite/plongeur.aseprite",
  "sheet": "assets/sprites/plongeur/plongeur.png", "data": "assets/sprites/plongeur/plongeur.json",
  "planches": {"base": "boards/plongeur_base.png", "modifie": "boards/plongeur_modifie.png",
               "iterations": ["boards/iterations/plongeur_it1.png", "…it2.png", "…it3.png"]}}]}
```
`type` : `vivant`, `objet`, `prop`, `tuileset`, `fond`, `effet`, `icone`, `interface`.

`art/journal/<id du sprite>.json` (règle de l'œil, une entrée par changement regardé ;
6 minimum pour un être vivant, 3 pour le reste) :
```json
{"entrees": [{"changement": "couleurs : color_type passe de SINGLE a TEXTURE",
  "image": "boards/journal/plongeur_02.png", "image_sha256": "…(affiché par comparer.py)…",
  "controle": {"silhouette": "…", "couleurs": "…", "cadrage": "…", "taille": "…",
               "details": "…", "coherence_base": "…", "pixels_parasites": "…"},
  "verdict": "garde", "defauts_restants": ["…"]}]}
```
Le contrôle mesure aussi chaque sprite vivant : le personnage remplit au moins 55 % de la hauteur
de sa case, le plongeur fait 28 à 48 px de haut, saturation moyenne au moins 0,12 (pas de rendu
gris), au moins 8 couleurs, images d'animation différentes, numéros d'images valides.
`filiere` : `construit` (construit par toi dans Blender, avec son script ; obligatoire pour `vivant`) ou `aseprite` (simple, rigide, de profil). Les filières `3d` (modèle téléchargé) et `pack2d` (pack téléchargé) sont refusées.
`data_id` : l'`id` de l'élément dans les données (créature, boss, objet), ou `plongeur`.
