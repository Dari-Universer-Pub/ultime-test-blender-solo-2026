# STYLE.md — Réglages communs de la chaîne d'assets (M0)

Ces réglages servent à TOUS les assets. Un asset qui s'en écarte doit le dire dans son script.

## 1. Cadre et échelle
- Case d'un sprite vivant : **64 × 64 px**. Le plongeur mesure **40 px** de haut debout (28 à 48 px contrôlés).
- Rendu Blender : **512 × 512 px**, soit **8 × 8 px de rendu par pixel final** (FACTEUR = 8).
- Caméra : **orthographique**, de profil (regarde vers +Y depuis -Y), largeur du cadre **3,2 unités**
  (0,05 unité par pixel final). Le plongeur fait 2,0 unités de haut au repos.
- Le plongeur regarde vers la droite (+X). Z = haut.

## 2. Lumière
- Clef : soleil à **4,2 W** venant du **haut-gauche** (bord éclairé en haut à gauche).
- Contre-jour : soleil bleuté à **1,4 W**, bas-droite.
- Monde : fond bleu nuit (0,10 ; 0,16 ; 0,22 linéaire), intensité 0,6. Fond de rendu transparent.
- Gestion des couleurs : **Standard** (pas d'AgX/Filmic : les tons de la palette restent exacts).
- Moteur : EEVEE, **64 échantillons** pour le rendu final.

## 3. Couleurs (palette)
- `art/palette.json` : **13 rampes**, **70 couleurs**, 4 à 6 tons par rampe, du plus sombre au plus clair.
- Décalage de teinte : **≥ 15°** entre le premier et le dernier ton de chaque rampe (mesuré, rampes OK).
- Pas de noir pur (#000000). Contour : rampes `contour_sombre` (bord dans l'ombre) et `contour_chaud` (bord éclairé).

## 4. Pixelisation (tools/pixelisation/pixeliser.py)
1. Réduction par blocs de 8 × 8 (moyenne pré-multipliée).
2. Seuil d'alpha **0,5** : chaque pixel est soit opaque (255), soit transparent (0). Aucun semi-transparent.
3. Quantification au ton de palette le plus proche, **espace Lab**, sans les rampes de contour.
4. Contour **sélectif, 1 px** à l'extérieur : bord éclairé (haut-gauche) = `contour_chaud` ton 2 ;
   bord dans l'ombre (bas-droite) = `contour_sombre` ton 1. Jamais de trait noir uniforme.
5. Nettoyage : tout pixel opaque sans voisin opaque (haut, bas, gauche, droite) est retiré.

## 5. Animations (plongeur)
- `nage` : 8 images, boucle complète (bras en brasse, palmes qui battent, corps couché tête à droite).
- `idle` : 6 images, flottement debout (bascule lente, bras qui se balancent, palmes qui frissonnent).
- Os : la flexion se fait autour de l'axe Z local de chaque os (l'axe Y d'un os Blender est sa longueur).

## 6. Feuille et export (Aseprite)
- `art/source/aseprite/construire_plongeur.lua` assemble les images pixelisées en `.aseprite`
  (étiquettes `nage` 1-8 et `idle` 9-14), puis exporte la feuille horizontale et le JSON `json-array`.
- `art/source/aseprite/finition_plongeur.lua` applique les retouches de chaque itération, puis ré-exporte.
- Espacement 0, marge 0 : une case = 64 × 64 px dans la feuille.

## 7. Journal visuel
- Une entrée par changement regardé, avec sa planche (`tools/planches/comparer.py`).
- Les 7 critères : silhouette, couleurs, cadrage, taille, détails, cohérence, pixels parasites.
