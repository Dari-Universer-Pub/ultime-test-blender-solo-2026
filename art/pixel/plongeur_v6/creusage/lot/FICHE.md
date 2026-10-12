# Fiche d'animation : creusage à la pioche (plongeur v6)

Données : `fiche.json`. Rôle : creuser, arc vers la droite, l'outil est gros et lisible, le corps accompagne le coup.
Canevas 112 x 112, sol à 92 px, hauteur 72 px au plus outil compris. Caméra, lumière, palette et style de l'ancre inchangés, sans contour.

| n | pose | durée (images) | angle de la pioche |
|---|---|---|---|
| 1 | prête (pioche sur l'épaule droite) | 4 | -50 |
| 2 | armement (pioche levée) — POSE CLÉ | 4 | -10 |
| 3 | sommet | 2 | +35 |
| 4 | frappe en pleine descente — POSE CLÉ | 2 | +110 |
| 5 | impact (tête au sol) — POSE CLÉ | 4 | +150 |
| 6 | retour — POSE CLÉ | 3 | +60 |

Points de prise : main droite sur le manche (bloc main + pioche = une seule pièce, rendue en rotation autour de la
poignée) ; main gauche libre. Pointe : tête d'acier, image 5 (contact au sol). Cible de l'impact : sol, devant et à
droite des pieds (x 84 px pour un pied droit à 66 px).

Ordre des calques : fond vers l'avant, par image dans `fiche.json`. Chevauchements : voir `politique_paires`.
Moment d'impact : image 5. Arc de mouvement : effet séparé (3 à 4 images, sans contour), voir AGENTS.md.
