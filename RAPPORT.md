# RAPPORT.md — Phase M0 (plongeur, corrections demandées par Julien)

Statut : **M0 en attente de validation visuelle de Julien.** M0 n'est pas validée. Aucune phase suivante n'est lancée.

Contrôle : `python tools/gate.py M0` lancé dans un **clone neuf** de la branche (dossier vide, sans `.godot/`) : SUCCES (commit a886191).

## Corrections demandées : état honnête

1. **Clone neuf** — corrigé et vérifié. Cause : le cache d'import `.godot/` n'est pas versionné ; Godot tentait de charger une texture jamais importée (message « Make sure resources have been imported »). Hypothèse H2 (les `.import` versionnés) non testée séparément. Solution : `scripts/m0_plongeur.gd` charge le PNG avec `Image.load_from_file`, sans cache.
2. **Taille 32-40 px sur chaque image** — corrigé. Mesures par image ci-dessous (nage 37-39 px, idle 37-38 px).
3. **Nage raide** — corrigé en partie. Amplitude nage 0,533 (cible ≥ 0,45). Battement de jambes et ondulation du buste plus amples ; bras balayant le plan de profondeur.
4. **Bras verticaux en nage** — corrigé visuellement (planches 12, 13). **Non mesuré par angle** : l'angle des os n'a pas été contrôlé dans Blender.
5. **Idle : bras devant le corps** — corrigé (planche 14). Amplitude idle 0,230 (cible ≥ 0,10, et ne baisse pas).
6. **Casque et équipement** — partiellement.
   - Fait : hublot en dôme de verre plus grand, sangles de harnais, palmes épaisses, liseré clair de lumière sous-marine, ombrage en 4 tons, contour sélectif (ombre seulement).
   - Non fait : cadre du hublot, boulons, tuyau d'air. Quatre tentatives de cadre et deux de tuyau sont annulées (journal 15 à 18, 26, 27) : à 32-40 px, un élément de moins de 2 px disparaît à la pixelisation.
   - Bouteilles : pas de valve ; reflet très faible (itération 3).
7. **Animation vivante** — partiellement. Amplitude et ondulation ajoutées ; anticipation et effets d'arrondi ne sont pas réellement implémentés.
8. **Références** — une seule image libre sur 2 ou 3 demandées. Wikimedia répond 429 à chaque tentative, y compris dans la session finale. Adresses prévues dans `art/references/SOURCES.md`.

## Mesures (tools/mesure/mesurer.py)

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

## Fait (vérifié)

- Journal visuel `art/journal/plongeur.json` : 32 entrées, 24 gardées, 8 annulées. Images distinctes, empreintes SHA-256 vérifiées.
- Planches d'itération : `boards/iterations/plongeur_it1.png` (gardée), `plongeur_it2.png` (tentative annulée), `plongeur_it3.png` (gardée, effet faible).
- Planche finale : `boards/plongeur_reference.png` (référence et rendu idle + nage agrandis ×4).
- Capture Godot : `shots/m0_plongeur_godot.png` (scène minimale, animation nage).

## Non vérifié

- Qualité « niveau professionnel » : non démontrée. Les critères sont un jugement visuel de l'agent.
- Angle des bras en nage : non mesuré.
- Animation complète : seulement des images, pas de vidéo jouée.

## Limites

- Format : à 32-40 px de haut, les détails de moins de 2 px ne se lisent pas (cadre, boulons, tuyau).
- Références : une seule image téléchargée (`ref_03_plongeur_stockholm_1951.jpg`, « no known copyright restrictions »), pour s'inspirer seulement.
- Godot : les dossiers `art/`, `boards/`, `shots/`, `tests/`, `tools/` ont un `.gdignore` (l'import ne se terminait pas). Le PNG est chargé à l'exécution : à vérifier à l'export (M5).

## Écarts vers Dead Cells (par impact)

1. Silhouette générique : pas encore de personnalité ni d'équipement lisible à cette taille.
2. Animation : pas d'anticipation ni d'écrasement/étirement réels.
3. Bras de nage peu visibles : la brassée ne se lit pas bien.
4. Détails du casque : hublot seulement, pas de cadre ni de reflet suffisant.
5. Pixel art : finition minimale (3 itérations, dont une annulée).

## Ce que Julien doit juger lui-même

- Si la limite de 2 px est acceptable, ou si la taille du sprite doit passer à 48 px pour les détails fins (décision de design).
- Le style général (planche `boards/plongeur_reference.png`, capture `shots/m0_plongeur_godot.png`).
- Le ressenti de la nage (à regarder en jeu).
- Accepter ou non l'image de référence téléchargée.

## Sortie complète de `python tools/gate.py M0` (clone neuf, commit a886191)

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
