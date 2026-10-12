# TABLE D'INTENTION — creusage (planche d'intention, RÈGLE ANIMATION A bis)

Coordonnées écran du sprite 112 x 112, caméra de l'ancre (projection Blender de l'idle).
Données : `intention.json` ; planche : `planche_intention.png` ; contrôles : `planche_intention.txt`.
Angle phi = direction manche (butt -> tête), en degrés, sens horaire depuis la verticale haute
(0 = haut, 90 = droite, 180 = bas). Angle depuis la verticale basse = |phi − 180|.
Triche = allongement de bras nécessaire (B bis, plafond +40 %).

| n | nom | phi | depuis la verticale basse | manche (butt -> tête) | mains (gauche, droite) | buste (dx, dy) | triche bras G / D | à lire en silhouette |
|---|---|---|---|---|---|---|---|---|
| 1 | ancre (sans outil) | — | — | — | repos | 0, 0 | 0 / 0 % | silhouette de l'ancre |
| 2 | prête | 170 | 10° | (70, 40) -> (75.7, 72.5) | (71.7, 49.8), (73.1, 59.5) | 0, 0 | +32 % / 0 | outil sur le côté droit, tête vers le bas-droit, rien devant le ventre |
| 3 | anticipation | 35 | 145° | (70, 58) -> (88.9, 31) | (70.2, 57.3), (78.5, 45.9) | −1, 0 | +25 % / +7 % | pioche levée vers le haut-droit, au-dessus de l'épaule droite |
| 4 | frappe | 180 | 0° | (70, 56) -> (70, 89) | (70, 64.9), (70, 73.5) | 0, 0 | +26 % / 0 | manche vertical sur le côté droit, tête en bas à droite |
| 5 | impact | 140 | 40° | (34.8, 60.7) -> (56, 86) | (38.1, 67.6), (47.5, 75.9) | +3, +2 | 0 / +22 % | tête posée au sol entre les pieds, manche incliné de 40° vers le bas-droit, buste penché à droite |
| 6 | retour | 50 | 130° | (68, 72) -> (93.3, 50.8) | (69.3, 70.9), (78.1, 63.5) | 0, 0 | +36 % / 0 | pioche remontée vers l'épaule droite, rien ne dépasse à gauche |

Contrôles 2D (calculés) : écarts d'angle entre images successives 135°, 145°, 40° (limite), 90° ;
mains espacées de plus de 8 px sur les six images ; outil hors du torse sur les six images ;
bas de la tête de l'impact à 90,2 px (sol 91,5) ; triches toutes sous +40 %.

Points à juger par Julien dans cette planche :
1. Image 5 : le manche traverse la jambe gauche (devant), la tête est entre les pieds (à gauche du centre
   des pieds, x = 56 pour des pieds en 49 et 61). Le plan la place « devant et au milieu » ; à confirmer.
2. Image 4 : le manche descend exactement à la verticale (0°) sur le côté droit ; l'écart avec l'impact
   est de 40° pile, à la limite.
3. Images 2, 4, 5 : le bras gauche traverse le torse en diagonale pour tenir la pioche (triche +25 à +32 %).
   Cette traversée est visible sur la planche : c'est la triche déclarée, à valider ou refuser.
