# TABLE DE POSES — creusage (lot 2), version cible 3D (v7)

Règle appliquée : RÈGLE ANIMATION (AGENTS.md), A à E. Caméra, lumière et palette inchangées.
Convention : x = droite (+), y = avant (négatif = vers la caméra), z = haut. Angle du manche = angle
dans le plan x-z (0° = vers la droite, −90° = vers le bas). Inclinaison 3D = angle entre le manche
et la verticale. Deux mains sur la pioche sur toutes les images (règle de Julien).

| image | nom | angle x-z | inclinaison 3D | tête d'acier (x, y, z) | buste | main gauche L (x, y, z) | main droite R (x, y, z) | à lire en silhouette |
|---|---|---|---|---|---|---|---|---|
| 1 | ancre | — | — | — | repos | repos | repos | silhouette de l'ancre, pas d'outil |
| 2 | prête | −45° | 45° | (0.79, −0.50, 0.91) | droit | (0.00, −0.50, 1.70) | (0.40, −0.50, 1.30) | outil tenu bas, en diagonale vers la droite |
| 3 | anticipation | +59° | 31° | (0.58, −0.50, 2.27) | léger recul (+0.04) | (0.00, −0.50, 1.30) | (0.30, −0.50, 1.80) | outil levé au-dessus de l'épaule droite |
| 4 | frappe | −37° | 56° | (0.81, −0.90, 0.99) | penché avant (−0.03) | (0.00, −0.50, 1.60) | (0.40, −0.70, 1.30) | diagonale descendante vers la droite (manche qui passe devant la poitrine : À REVOIR) |
| 5 | impact | −63° | 28° | (0.64, −0.68, 0.41) | penché avant-droite (−0.12, +0.10, casque −0.10) | (0.10, −0.50, 1.50) | (0.40, −0.60, 0.90) | outil bas, mais manche à 28° seulement et tête à 0,41 du sol : ÉCHEC (cible 35 à 45°, tête au sol) |
| 6 | retour | +37° | 56° | (0.71, −0.30, 2.01) | léger avant (+0.02) | (−0.10, −0.70, 1.40) | (0.30, −0.50, 1.70) | outil remonté vers l'épaule droite |

## Contrôles automatiques (règle C), mesurés

| contrôle | image 2 | image 3 | image 4 | image 5 | image 6 | verdict |
|---|---|---|---|---|---|---|
| C1 mains sur l'outil (écart gant-manche, unités) | 0,109 / 0,024 | 0,045 / 0,076 | 0,023 / 0,085 | 0,117 / 0,102 | 0,088 / 0,003 | OK à 3 px près (tolérance à resserrer) |
| C2 outil relié au corps | OK (C1) | OK | OK | OK | OK | OK |
| C3 bras proche ≥ 45 % / lointain ≥ 40 % | 58 / 58 | 83 / 41 | 66 / 42 | 66 / 56 | 75 / 59 | OK (image 3 : marge de 1 point) |
| C4 écart d'angle ≥ 40° avec l'image précédente | — | 104° | 96° | 26° : ÉCHEC | 100° | ÉCHEC à l'impact |
| C5 hauteur 70 à 72 px | 72 | 72 | 72 | 69 : ÉCHEC | 72 | ÉCHEC à l'impact (69 px) |
| C6 pixels isolés, hash, contour | au pixel art seulement | | | | | non vérifié |

Tête d'acier, mesure à ×1 : non mesurable proprement sur les rendus bruts à 112 px (la tête est
petite et partiellement cachée). À mesurer sur les images nettoyées du pixel art.

## Ce que le calcul établit (recherche exhaustive sur grille de 0,1 unité)

- Frappe, anticipation, prête et retour : des poses à deux mains existent avec les mains visibles
  et hors du tronc.
- **Impact : aucune pose à deux mains ne réunit toutes les conditions** (tête au sol, devant et à
  droite des pieds, manche incliné de 35 à 45° en 3D, les deux mains visibles et hors du tronc).
  Le meilleur compromis trouvé reste à 28° et à 0,41 du sol. La main gauche ne peut pas atteindre la
  zone de prise basse à droite avec la portée des bras.
- Autoriser la main gauche devant la poitrine (non visible en silhouette) rend l'impact possible,
  mais ce n'est pas un bras visible.

## Décision demandée à Julien

Choisir entre :
1. Assouplir « deux mains partout » à l'impact (une main sur le manche, le bras gauche au repos) : l'impact
   redevient réalisable avec le manche incliné et la tête au sol.
2. Garder deux mains et accepter un impact au manche presque vertical (28°), à 69 px.
3. Modifier le modèle (épaule, longueur des bras) pour élargir la portée, ce qui change le corps du plongeur.
