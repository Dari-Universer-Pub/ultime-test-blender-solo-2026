# Table d'intention : creusage (fiche « creusage à la pioche, style Stardew »)

Angles : depuis la verticale haute, sens horaire ; le manche va du bout (butt) à la tête d'acier. Écart d'angle de l'image 1 : avec l'image 6 (la séquence boucle). Étirements : triche déclarée (bras allongé jusqu'à +25 % au plus). Décalages : buste et casque en px sprite. Mains : fraction du manche depuis le bout (0 = bout, 1 = tête).

| image | nom | durée | phi cible | phi obtenu | écart d'angle avec l'image précédente | buste dx ; dy | casque dx ; dy | étirement des bras | mains L / R | bout / tête (x, y) | contrôles calculés |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prete | longue | -50 | -50 | 110 | +0.0 ; +0.0 | +0.0 ; +0.0 | G +0 % / D +0 % | libre / 0.00 | (67.0, 54.0) / (40.2, 31.5) | outil a 5.1 px du hublot (cadre 7.5) |
| 2 | armement | longue | -10 | -10 | 40 | -2.5 ; +0.0 | -1.5 ; +0.0 | G +0 % / D +12 % | libre / 0.20 | (82.1, 56.5) / (76.0, 22.0) | OK |
| 3 | sommet | tres courte | +35 | +35 | 45 | +1.0 ; +0.0 | +1.0 ; +0.0 | G +0 % / D +0 % | libre / 0.40 | (61.9, 56.7) / (82.0, 28.0) | OK |
| 4 | descente | tres courte | +110 | +110 | 75 | +3.0 ; +0.5 | +3.0 ; +2.0 | G +0 % / D +0 % | 0.05 / 0.25 | (66.0, 60.0) / (98.9, 72.0) | manche dans le torse 1.2 px |
| 5 | impact | longue | +150 | +150 | 40 | +4.0 ; +1.5 | +4.0 ; +5.0 | G +4 % / D +0 % | 0.20 / 0.56 | (66.5, 58.4) / (84.0, 88.8) | manche dans le torse 1.0 px |
| 6 | retour | moyenne | +60 | +60 | 90 | +0.0 ; +0.0 | +0.0 ; +0.0 | G +24 % / D +0 % | 0.00 / 0.25 | (66.7, 70.5) / (97.0, 53.0) | manche dans le torse 0.5 px |

Écarts d'angle entre images successives (cible >= 40 deg) :

- 6 -> 1 : 110 deg
- 1 -> 2 : 40 deg
- 2 -> 3 : 45 deg
- 3 -> 4 : 75 deg
- 4 -> 5 : 40 deg
- 5 -> 6 : 90 deg
