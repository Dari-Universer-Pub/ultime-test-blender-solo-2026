# RAPPORT.md — Phase M0 (outils, palette, chaîne d'assets sur le plongeur)

Statut : **M0 en SUCCES au contrôle, en attente de validation visuelle de Julien** (PLAN.md, phase M0 ARRÊT POUR VALIDATION).

## Fait (vérifié par une commande ou un fichier)

- Outils : `bash /opt/outils-varekh/verifier.sh` affiche `SUCCES` (13 OK), Godot 4.4.1, Blender 5.2.1, Aseprite 1.3.18.6.
- Palette `art/palette.json` : 13 rampes, 70 couleurs, aucun noir pur, décalage de teinte d'au moins 15° sur chaque rampe.
- Plongeur construit dans Blender par `art/source/blender/plongeur.py` : modèle en un maillage, squelette à 13 os, poids par distance,
  caméra orthographique de profil, rendu 512 px. 14 images : `nage` (8) et `idle` (6), dans `art/rendu/plongeur/`.
- Pixelisation par `tools/pixelisation/pixeliser.py` : réduction 8×8, seuil d'alpha 0,5, quantification Lab aux tons de la palette,
  contour sélectif 1 px, nettoyage des pixels isolés. Images dans `art/pixel/plongeur/`.
- Finition Aseprite : `art/source/aseprite/construire_plongeur.lua` (assemblage et étiquettes), `art/source/aseprite/finition_plongeur.lua`
  (3 itérations). Source : `art/source/aseprite/plongeur.aseprite`. Feuille : `assets/sprites/plongeur/plongeur.png` (14 cases de 64 px),
  JSON `assets/sprites/plongeur/plongeur.json` avec les étiquettes `nage` (0 à 7) et `idle` (8 à 13).
- Journal visuel `art/journal/plongeur.json` : 10 entrées, chacune avec sa planche (`boards/journal/`), son SHA-256 et les 7 critères.
  Verdicts : 10 × `garde`, aucun `annule`.
  - Entrées 1 à 7 : modèle et pixelisation (quantification, contour, lissage, hublot déplacé puis agrandi, lampe, pose des bras).
  - Entrées 8 à 10 : itérations Aseprite (reflet du hublot en 2 pixels, puis remplacement des bruns de la combinaison par des tons de la rampe combinaison).
- Scène Godot minimale : `scenes/m0_plongeur.tscn` et `scripts/m0_plongeur.gd`. Les animations viennent du JSON Aseprite.
  Capture prise par Godot (`get_viewport().get_texture().get_image().save_png`) : `shots/m0_plongeur_godot.png`.
- Planches : `boards/plongeur_base.png` (premier rendu), `boards/plongeur_modifie.png` (version actuelle),
  `boards/iterations/plongeur_it1.png` à `plongeur_it3.png`, `boards/plongeur_reference.png` (référence + rendu).
- `art/manifest.json` : entrée `plongeur` (filière `construit`). `STYLE.md` : réglages chiffrés communs.
- `tools/gate.py M0` affiche `SUCCES` (sortie complète ci-dessous, dernier contrôle 2026-10-11 08:50:17).

## Non vérifié

- La qualité « niveau professionnel » n'est pas démontrée. Les 7 critères sont un jugement visuel de l'agent sur les planches, pas une mesure.
  Le plongeur reste un personnage de base : bras de nage raides, palmes minces, pieds peu détaillés.
- La boucle d'animation `nage` a été regardée sur des planches basse résolution puis sur les images finales de l'entrée 10 ; aucune vidéo complète n'a été jouée.
- La scène Godot est vérifiée en lancement avec écran virtuel et en capture ; elle n'a pas été exportée ni jouée au clavier (rien d'exigé en M0).
- Sons, musique et polices : aucun, rien n'est exigé en M0.

## Limites

- Références : **une seule** image libre est dans `art/references/` (Stockholm 1951, « No known copyright restrictions »).
  Les deux autres, prévues dans `art/references/SOURCES.md`, n'ont pas pu être téléchargées : Wikimedia répond 429 (limite de débit) à chaque tentative.
  AGENTS.md en demande 2 ou 3. Cette référence sert à s'inspirer, elle n'est pas utilisée dans le jeu.
- Rendu EEVEE logiciel (llvmpipe), 64 échantillons, sans passe de normales (prévue par BRIEF §6 pour plus tard).
- Dossiers `art/`, `boards/`, `shots/`, `tests/`, `tools/` marqués `.gdignore` : Godot ne les importe pas. Le jeu n'en a pas besoin.
- Une seule variante de scaphandre et aucune animation autre que `nage` et `idle` : les autres animations (creusage, attaque, saut, dégâts, mort) sont en M3.

## Écarts vers Dead Cells (à classer par impact pour la suite)

1. Animation : pose de nage et flottement seulement, sans anticipation ni écrasement/étirement (fort impact sur les sensations).
2. Personnage : silhouette encore générique, pas de détail d'équipement lisible (manomètres, tuyaux) (fort).
3. Pixel art : finition encore minimale, trois itérations seulement (moyen).
4. Lumière : pas de cartes de normales ni de Light2D sur le sprite (moyen).
5. Décor : la scène est un dégradé d'eau sans particules ni profondeur (moyen).

## Ce que Julien doit juger lui-même

- Le style du plongeur (planches `boards/plongeur_modifie.png`, `boards/iterations/`, `shots/m0_plongeur_godot.png`) : est-ce le ton visé ?
- La beauté de la palette (`art/palette.json`) et des couleurs de combinaison.
- Le ressenti de l'animation de nage (à regarder en jeu, pas sur des images).

## Sortie complète de `python3 tools/gate.py M0`

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
