# Cible 3D haute qualité : creusage (fiche)

| image | nom | phi (deg) | étirement G / D | hauteur (px, max 72) | tête (px, min 12) | manche (px) | épaisseur manche (px, min 3) | bras proche / lointain (%) | écart d'angle précédent | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prete | -50 | +24.4 % / +0.0 % | 72.0 | 13.4 | 35 | 3.2 | 69 / 52 | 110 | OK |
| 2 | armement | -10 | +18.7 % / +1.1 % | 72.0 | 13.4 | 35 | 3.2 | 47 / 56 | 40 | OK |
| 3 | sommet | +35 | +22.8 % / +20.7 % | 72.0 | 13.4 | 35 | 3.2 | 82 / 45 | 45 | OK |
| 4 | descente | +110 | +4.3 % / +0.0 % | 70.0 | 13.4 | 35 | 3.2 | 46 / 46 | 75 | OK |
| 5 | impact | +150 | +8.5 % / +0.0 % | 67.0 | 13.4 | 35 | 3.2 | 71 / 52 | 40 | OK |
| 6 | retour | +60 | +16.3 % / +0.0 % | 72.0 | 13.4 | 35 | 3.2 | 86 / 49 | 90 | OK |

## Conforme / écart, image par image

- **1. prete** — conforme : angle -50 deg (valide) ; tete d'acier et manche devant le casque, lisibles ; tete a 13,4 px ; manche a 35 px ; main droite sur le haut du manche, main gauche plus bas ; les deux bras visibles (proche 69 %, lointain 52 %) ; buste droit, pieds comme l'ancre ; hublot non traverse.
  - écart : (1) profondeur : le manche et la tete sont devant le casque, pas derriere (derriere, le manche disparaissait sous le dome). En 2D, la tete reste en arriere-haut comme sur la planche. (2) les deux mains sont a 7 px l'une de l'autre sur le manche : a l'ecran elles forment presque un seul gant. (3) main gauche au-dessus de l'epaule droite, pas devant la poitrine : consequence de -50 deg, accepte a la validation. (4) triche declaree : epaule gauche avancee de 0,25 m en profondeur (2D inchange) ; etirement du bras gauche +24 %, limite +25 %.
- **2. armement** — conforme : angle -10 deg ; outil au-dessus du casque, haut de la barre a 20,0 px ; les deux bras montent, main droite plus haute que la gauche ; buste recule de 2,5 px et casque de 1,5 px (2D) ; pieds fixes ; hublot non traverse ; bras proche 47 %, lointain 56 %.
  - écart : (1) tete d'acier descendue de 1 px (23,0 au lieu de 22,0) : la barre epaisse depassait le haut du sprite de 0,8 px (hauteur 72,8 px). (2) triche declaree : epaule gauche avancee de 0,25 m en profondeur pour que la main gauche soit a portee, 2D inchange. (3) coudes ecartes : visibles sur le rendu, non mesures en degres.
- **3. sommet** — conforme : angle +35 deg ; outil au-dessus du casque, penche vers l'avant, haut a 23,3 px ; bras tendus vers le haut et l'avant (etirement 3D : gauche +23 %, droit +21 %) ; buste revient a la verticale puis s'avance ; mains sur le manche, les deux visibles (proche 82 %, lointain 45 %).
  - écart : (1) triches declarees : epaule gauche avancee de 0,40 m et droite de 0,10 m en profondeur (2D inchange), pour que les deux mains soient devant le casque et a portee ; etirements proches de la limite de 25 %. (2) les deux mains sont a 3,5 px l'une de l'autre sur le manche.
- **4. descente** — conforme : angle +110 deg ; tete de pioche a hauteur des hanches, a droite du corps, un peu devant le corps (0,30 m devant le plan du corps) ; bras descendent cote droit ; buste incline vers l'avant (3 px en 2D, 0,08 m en profondeur) ; casque baisse de 2 px ; pieds fixes ; etirement G +4 %, D 0 %.
  - écart : (1) ordre des mains inverse : la main gauche tient le haut du manche, la droite est plus bas (meme raison que la planche : portee du bras gauche). (2) triche declaree : epaule gauche avancee de 0,25 m en profondeur. (3) inclinaison du buste : environ 10 deg, sans mesure precise en degres.
- **5. impact** — conforme : angle +150 deg (30 deg de la verticale) ; tete d'acier au sol, bas a 92 px (sol de l'ancre), a droite des pieds ; manche hors de la jambe gauche ; genoux fléchis (0,10 m vers l'avant, 0,03 m plus bas) ; buste penche (4 px et 0,16 m vers l'avant) ; casque baisse de 5 px ; main gauche sur le manche au ventre cote droit ; bras proche 71 %, lointain 52 % ; hublot non touche.
  - écart : (1) main droite a hauteur de la hanche, pas devant le ventre : le bras droit reste presque tendu (fiche : « si le bras le permet ») ; a hauteur du ventre, il faudrait le plier. (2) ordre des mains inverse (gauche au ventre, droite plus bas). (3) triche declaree : epaule gauche avancee de 0,25 m en profondeur.
- **6. retour** — conforme : angle +60 deg ; pioche qui se retire vers la droite, tete a 97,53 ; buste redresse ; main droite au-dessus de la gauche sur le manche ; pieds fixes ; hublot loin ; bras proche 86 %, lointain 49 %.
  - écart : (1) triche declaree : epaule gauche decalee de 2 px vers la droite et avancee de 0,20 m en profondeur ; sans cela le bras passait derriere le torse (lointain 24 %) et l'etirement depassait +25 %. Etirement du bras gauche +16 %. (2) main gauche au bout du manche, au flanc droit : point limite de la portee.

Contrôles qui restent au pixel art : pixels isolés, images distinctes (hash), contour (aucun).
