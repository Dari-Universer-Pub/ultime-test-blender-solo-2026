# Table d'intention : creusage (fiche « creusage à la pioche, style Stardew »)

Angles : depuis la verticale haute, sens horaire ; le manche va du bout (butt) à la tête d'acier. Écart d'angle de l'image 1 : avec l'image 6 (la séquence boucle). Étirements : triche déclarée (bras allongé jusqu'à +25 % au plus). Décalages : buste et casque en px sprite. Mains : fraction du manche depuis le bout (0 = bout, 1 = tête).

| image | nom | durée | phi cible | phi obtenu | écart d'angle avec l'image précédente | buste dx ; dy | casque dx ; dy | étirement des bras | mains L / R | bout / tête (x, y) | contrôles calculés |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prete | longue | -30 | -30 | 90 | +0.0 ; +0.0 | +0.0 ; +0.0 | G +0 % / D +0 % | 0.15 / 0.35 | (67.0, 63.3) / (49.5, 33.0) | manche dans le torse 7.3 px |
| 2 | armement | longue | -10 | -10 | 20 | -2.5 ; +0.0 | -1.5 ; +0.0 | G +0 % / D +0 % | 0.30 / 0.45 | (62.1, 56.5) / (56.0, 22.0) | OK |
| 3 | sommet | tres courte | +35 | +35 | 45 | +1.0 ; +0.0 | +1.0 ; +0.0 | G +9 % / D +16 % | 0.55 / 0.65 | (49.9, 55.7) / (70.0, 27.0) | OK |
| 4 | descente | tres courte | +110 | +110 | 75 | +3.0 ; +0.5 | +3.0 ; +2.0 | G +0 % / D +0 % | 0.05 / 0.25 | (66.0, 60.0) / (98.9, 72.0) | manche dans le torse 1.2 px |
| 5 | impact | longue | +150 | +150 | 40 | +4.0 ; +1.5 | +4.0 ; +5.0 | G +4 % / D +0 % | 0.20 / 0.56 | (66.5, 58.4) / (84.0, 88.8) | manche dans le torse 1.0 px |
| 6 | retour | moyenne | +60 | +60 | 90 | +0.0 ; +0.0 | +0.0 ; +0.0 | G +24 % / D +0 % | 0.00 / 0.25 | (66.7, 70.5) / (97.0, 53.0) | manche dans le torse 0.5 px |

Écarts d'angle entre images successives (cible >= 40 deg) :

- 6 -> 1 : 90 deg
- 1 -> 2 : 20 deg : ÉCART
- 2 -> 3 : 45 deg
- 3 -> 4 : 75 deg
- 4 -> 5 : 40 deg
- 5 -> 6 : 90 deg
