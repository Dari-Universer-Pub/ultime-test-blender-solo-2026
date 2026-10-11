# RAPPORT.md — Phase M0 (plongeur), deuxième vague de corrections

Statut : **M0 en attente de validation visuelle de Julien.** M0 n'est pas validée. Aucune phase suivante n'est lancée.

Contrôle : `python tools/gate.py M0` dans un **clone neuf** de la branche (dossier vide, sans `.godot/`), au commit `baa695f` : **SUCCES**. La sortie complète est ci-dessous.

## Corrections demandées (2e vague), état honnête

1. **Nage illisible** — corrigé. Les bras passent sous le torse (brassée entre 0,5 et 1,5 rad), hors du corps, en orange clair. Chaque jambe a trois tons oranges (ombre, base, lumière). Palmes en turquoise-vert, teinte différente du pantalon.
2. **Couleurs des membres** — corrigé. Les seuils des paliers ont été remontés : le ton sombre ne domine plus. Mesure (tools/mesure/tons.py) : base 50 %, ombre 31 %, lumière 12 % des pixels de combinaison en nage.
3. **Casque** — partiel. Dôme de verre plus grand, cadre clair de 1 px, reflet blanc de 2 pixels, reflet de 1 pixel sur la bouteille. **Le hublot reste la zone la plus faible du sprite à x1.** Le hublot cyan franc a été essayé puis annulé (entrée 35).
4. **Références** — deux sources libres, avec adresses et licences dans `art/references/SOURCES.md` : une photo de 1970 (CC BY 3.0, avec une incohérence de licence signalée) et une photo de 1951 (« no known copyright restrictions »). Les autres tentatives échouent (429 ou 403).
5. **Export Windows** — noté dans ETAT.md, à tester en M2 : `Image.load_from_file` sur `res://` n'est pas vérifié dans un export `.exe`.
6. **Animation** — nage avec une image de préparation (bras repliés) et deux images de glisse (bras allongés). Idle : respiration visible mais faible (1 px), sans bulles.

Acquis vérifiés à chaque changement : taille 32-40 px sur chaque image, amplitude nage >= 0,45, amplitude idle >= 0,10.

## Journal visuel

46 entrées : 36 gardées, 10 annulées. Chaque entrée a une image distincte et son SHA-256 vérifié. Les itérations Aseprite ont été rejouées sur les images finales (planches `boards/iterations/`).

## Mesures

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

## Fait (vérifié)

- Journal visuel `art/journal/plongeur.json` : 46 entrées, empreintes vérifiées.
- Planche finale : `boards/plongeur_reference.png` (deux références à gauche, idle et deux nages agrandis ×4 à droite).
- Capture Godot : `shots/m0_plongeur_godot.png` (nage en scène minimale).
- Clone neuf : contrôle SUCCES.

## Non vérifié

- La qualité « niveau professionnel » n'est pas démontrée. Les critères sont un jugement visuel de l'agent sur des planches.
- L'animation n'a pas été jouée : seulement des images fixes.
- Le hublot à x1 n'est pas assez contrasté pour être jugé lisible ; un test de lisibilité par Julien est nécessaire.

## Limites

- Format : à 32-40 px de haut, les détails de moins de 2 px ne se lisent pas. Le casque (cadre, boulons, tuyau) est limité par ce format. Décision prise : rester à 32-40 px.
- Références : deux sources seulement, dont une sous licence CC BY 3.0 avec une incohérence signalée. Inspiration seulement.
- Godot : `art/`, `boards/`, `shots/`, `tests/`, `tools/` ont un `.gdignore`. Le PNG est chargé à l'exécution : à tester en export (M2).

## Écarts vers Dead Cells (par impact)

1. Silhouette générique : le plongeur ne se distingue pas encore par une personnalité ni un équipement lisible à 37 px.
2. Hublot : contraste et reflet insuffisants à x1.
3. Animation : anticipation et temps de glisse à travailler au-delà d'une image.
4. Respiration idle : 1 px, pas de bulles.
5. Pixel art : finition minimale (trois itérations, à faible effet).

## Ce que Julien doit juger lui-même

- Le hublot : est-il lisible à x1 pour toi ?
- Le style général (planche finale et capture Godot).
- La nage en mouvement (à voir en jeu, pas sur des images).
- L'acceptation de la limite de 32-40 px pour les détails du casque.

## Sortie complète de `python tools/gate.py M0` (clone neuf, commit baa695f)

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
