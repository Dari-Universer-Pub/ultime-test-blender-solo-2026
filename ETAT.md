# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante : PLONGEUR V6 (cible décrite, dessin animé), POSE IDLE — ARRÊT POUR VALIDATION DE JULIEN
Julien a repris le héros avec une cible décrite (pas encore d'image cible). Pose idle seulement ; ensuite la nage, les autres animations, la feuille, le jeu, les tuiles 24 px, le robot et `gate.py M3` restent à faire.
Rien n'est téléchargé. Références : `art/references/` (1951 Stockholm, 1970 USF). `tools/gate.py` et `tools/outils.json` non touchés ; HAUTEUR_PLONGEUR = (56, 80).

- Script : `art/source/blender/plongeur_v6.py` (refait tout, corps en Skin lissé puis découpé, pièces rigides, détails peints par face, rampes CONSTANT par matière, contour froid cyan sur le bord droit).
- Session Blender persistante : `tools/blender_session/serveur.py` (lancé avec `blender -b`, lit des commandes dans un dossier) et `envoyer.py`. Aucun serveur MCP Blender n'est disponible dans cet environnement : c'est le seul moyen utilisé. Un rendu de contrôle prend 4 à 6 s, une carte d'identité 25 à 30 s.
- Essais rapides : 16 essais de forme (`essai0` à `essai16`), mesurés deux à deux (pourcentage de pixels changés). Détail dans le journal.
- Sprite final : `art/pixel/plongeur_v6/idle_01.png` (= contour, étape 14). Rendus : `art/rendu/plongeur_v6/`. Carte d'identité : matière et groupe, à 112 px.
- Journal : `art/journal/plongeur_v6.json`, 13 entrées, SHA-256 vérifiés. Annulations listées à part.
- Planche : `boards/plongeur_v6_planche.png` (références 1951 et 1970 | v6 eau claire | v6 eau sombre | v6 damier | v5 précédent, et le bloc de mesures et d'écarts).

### Objectifs chiffrés (mesurés sur le sprite final)
| objectif | cible | mesure | écart |
|---|---|---|---|
| hauteur | 70 à 74 px | 71 px | OK |
| couleurs | 24 à 32 | 24 utilisées sur 25 de palette | OK |
| rampes par matière | 3 ou 4 tons | laiton 4, beige 4, cuir 3, violet 3, métal 3, verre 3, corde 3, contour 2 | OK |
| pixels isolés | 0 | 0 (8 voisins) | OK |
| contour 1 px constant | 1 px partout | 3 blocs 2x2 restants | ÉCART (3 blocs) |
| contour dense | léger | 28 % de la silhouette | ÉCART |
| membres | >= 30 px, >= 60 % | bras proche 206 px / 89 %, bras lointain 184 px / 63 %, jambe proche 249 px / 94 %, jambe lointaine 211 px / 64 % | OK |
| tuyau (corde) | < 10 % | 6,1 % | OK |
| plis nets | 3 ou 4 | quasi absents (1 à 10 faces par pli) | ÉCART |
| reflets caoutchouc 1-2 px | présents | non peints | ÉCART |
| boulons visibles | présents | invisibles à x1 | ÉCART |
| torsion de corde | visible | corde à 3 px, torsion illisible | ÉCART |

### Écarts restants, numérotés (comparaison à la description)
1. Plis : les 3 ou 4 plis nets (épaule, coude, ceinture, genou) sont presque absents. Les réglages de plis sont sous le seuil de 5 %.
2. Jambes : ombres en plaques sombres (plis en bloc), visibles à x4 : bruit. Retirer le pli du genou ne change que 0,8 % : annulé.
3. Matières : reflets de caoutchouc (gants, bottes) non peints ; boulons du cadre et de la collerette invisibles ; arc de reflet du laiton trop large.
4. Corde : 3 px, torsion illisible ; cible « épaisse » non atteinte (la corde à 0,085 ne change que 3,1 % : annulée).
5. Bouteille : partiellement cachée derrière l'épaule gauche.
6. Ceinture : 2,4 % seulement pour l'élargir (conservée, voir ci-dessous).
7. Combinaison : ombres mauve-gris, beige encore froid.
8. Contour : 28 % de la silhouette, 3 blocs 2x2 restants.
9. Lumière : contour cyan présent sur le bord droit (58 px) ; lumière haut-gauche OK.
10. Proportions : tête environ 40 % de la hauteur, tronc court et rond, bras et jambes courts et épais : OK.

Les trois points les plus faibles : (1) plis et corde sans relief ; (2) contour trop dense, 3 blocs 2x2 ; (3) reflets caoutchouc et boulons absents.

### Règle des 5 %, appliquée et discutée (à trancher par Julien)
- ANNULÉS (sous 5 % des pixels, et sans réduire d'écart à mes yeux) : passes de finition majorité 3x3 casque (0,7 %), jambes (0,5 %), bras-gants-tronc-corde (1,2 %) ; retrait du pli du genou (0,8 %) ; corde à 0,085 (3,1 %). Les fichiers des passes sont dans `art/pixel/plongeur_v6/passes/annulees/`.
- CONSERVÉS SOUS LE SEUIL, marqués « NON COMPTÉ » dans le journal : ceinture élargie (2,4 %), plis (1,1 %, et 0,5 % pour le pli d'épaule), section ronde du Skin (4,8 %). Ce sont des corrections de forme demandées par la description ; annulées, la ceinture et le tronc rond disparaîtraient. Je ne les ai pas annulées sans votre accord.
- CONSÉQUENCE : aucune passe de finition Aseprite n'est appliquée. La consigne « au moins 3 passes visibles » et la règle « annule si < 5 % » ne peuvent pas être tenues ensemble avec du simple nettoyage. Options : (a) autoriser des repeintes de 5 % ou plus (une zone entière) ; (b) abaisser le seuil pour les passes de nettoyage ; (c) compter les détails à part.

### Ce qui n'est pas fait (à reprendre après validation)
- Nage (quatre membres lisibles à chaque image), autres animations, feuille, jeu (miroir, collisions, caméra), tuiles 24 px avec créatures et props agrandis ×1,5, robot, `python tools/gate.py M3` dans un clone neuf.
- Image cible : quand Julien la fournira, la comparer à la planche avant toute nouvelle passe.


Rien d'autre n'est fait : ni nage, ni autre animation, ni feuille, ni jeu, ni robot, ni `gate.py M3`.
Attendre la validation de Julien sur la pose idle (planche `boards/plongeur_v5_dc_planche.png`).

- Script : `art/source/blender/plongeur_v5_dc.py` (refait le `.blend` et les rendus de zéro). Rendu DIRECT à 112 px, héros de 70 px.
  Lumière plate par paliers (produit scalaire normale · lumière haut-gauche, rampe CONSTANT), émission seule, pas de spéculaire,
  filtre à 0, tramage à 0, alpha 0/255. Sorties : `art/rendu/plongeur_v5_dc/` (rendu couleur, cartes d'identité matière et groupes).
- Détails PEINTS par face (attribut DET = code de palette), plus en géométrie : grille de la vitre, reflet, six boulons du cadre avant,
  quatre du hublot latéral, douze de la collerette, fermeture et coutures du tronc.
- Contour et nettoyage : `tools/pixelisation/contour_dc.py` (silhouette côté ombre, bords internes entre matières ou groupes, amincissement des blocs 2 x 2).
  Puis passes Aseprite 1 à 8 (`tools/pixelisation/passe_aseprite.py`, listes de pixels dans `art/pixel/plongeur_v5_dc/passes/`).
  Sprite final : `art/pixel/plongeur_v5_dc/idle_01.png`.
- Journal : `art/journal/plongeur_v5_dc.json`, 12 entrées. COMPTÉES (au moins 5 % des pixels) : changement 1 (tramage, 18,5 %), 2 (détails peints, 7,6 %), 4 (contour, 32,7 %).
  NON COMPTÉES : 3 (tronc et fermeture, 3,2 %) et les passes Aseprite 1 à 8 (de 0,0 à 4,1 %).
- Mesures du sprite final (`idle_01.png`) :
  | mesure | valeur | cible | verdict |
  |---|---|---|---|
  | hauteur | 70 px | 70 à 74 | OK |
  | pixels isolés (8 voisins) | 0 | 0 | OK |
  | blocs 2 x 2 de contour | 0 (contour 1 px) | 1 px constant | OK |
  | couleurs | palette de 66 couleurs (8 tons x 8 familles + 2 contours) ; 33 utilisées dans le sprite, toutes de la palette | palette de 64 à 96 | OK |
  | tuyau (corde) | 5,5 % de la silhouette | < 10 % | OK |
  | bras proche (carte d'identité, 112 px) | 177 px / 87 % | >= 30 px, >= 60 % | OK |
  | bras lointain | 154 px / 74 % | idem | OK |
  | jambe proche | 180 px / 83 % | idem | OK |
  | jambe lointaine | 163 px / 75 % | idem | OK |
- Planche : `boards/plongeur_v5_dc_planche.png` (v4 haute résolution ; v4_px actuel x4 ; v5 x4 sur eau claire, eau sombre, damier).
- Les trois points les plus faibles, vus sur la planche :
  1. Gants et bottes en indigo : lus comme du violet, peu crédibles, sans volume.
  2. Tronc et jambes presque d'un seul ton beige : peu de volume ; la fermeture à glissière tient à peine sur 2 px.
  3. Bouteille cachée derrière le casque ; corde fine, sans torsion visible.
- Écarts avec le brief, à valider :
  - Passes Aseprite : aucune ne dépasse 5 %. Le nettoyage seul ne change pas assez de pixels pour passer le seuil ;
    elles sont comptées « non comptées » comme dans la série manuelle précédente. Julien décide si la règle s'applique au nettoyage.
  - Torsion de la corde et plis de toile : encore en géométrie (corde : courbe biseautée ; plis : déplacement), pas peints.
  - Couture de ceinture et boucle : encore en géométrie.
  - Les lumières de scène ne servent pas aux matières (émission seule) : elles ne changent rien au rendu.
  - Reproductibilité : `contour_dc.py` a produit `idle_01_contour.png` AVANT l'ajout de l'amincissement ; les passes 4 à 8 (listes de pixels générées puis appliquées dans Aseprite) complètent la chaîne. Le sprite final ne se refait donc pas en une seule commande.
- Gate : `tools/gate.py` et `tools/outils.json` non touchés.

## Ancienne phase (v5 Dead Cells, arrêt pour validation de la pose idle)
Voir `art/journal/plongeur_v5_dc.json`. Le sprite v5 sert de comparaison dans la planche v6.

## Ancienne phase (v4_px, finition manuelle, archivée) : PLONGEUR V4_PX, EN ATTENTE DE VALIDATION
- Julien a rejeté l'aspect « dessin d'enfant » : formes en boîtes et lignes droites. Refonte à la main, cartes de pixels explicites dans `art/pixel/plongeur_v4_px/main/dessin.py` (calques ; `carte_<passe>.txt`).
- Calque 'repère' = réduction automatique ; calque 'dessin' = la main, exporté seul (`assembler.py`, fichiers `plongeur_v4_px_passe<n>.aseprite/.png`).
- Passes comptées (au moins 10 % des pixels changés) : passe 1 (92,6 %), passe 7 (46,4 %). Journal : `art/journal/plongeur_v4_px_manuel.json`.
- Retouches 2 à 6 (0,7 à 3,4 %) : sous le seuil, non comptées.
- Planche finale : `boards/journal/plongeur_v4_px_manuel_final.png` (rendu v4 haute résolution à gauche, pixel ×4 sur eau claire, eau sombre et damier).
- Reste ouvert, dit honnêtement : jambes encore presque droites (deux colonnes) ; boucle de corde fine, lue comme un crochet ; gant lointain en pavé sombre ; pose encore trop droite (déséquilibre demandé non fait) ; proportions tête 40 / tronc 25 / jambes 35 à vérifier.
- Gate : `HAUTEUR_PLONGEUR = (56, 80)` toujours absent de la branche ; non touché.

## Ancienne phase (v3, archivée) : NOUVEAU MODÈLE DU HÉROS (vue de trois quarts), étape 1 = pose idle
Julien a demandé un modèle refait de zéro, pensé pour être lu de trois quarts : `art/source/blender/plongeur_v3.py`.
Ancien modèle (profil) archivé : `art/source/blender/archive/plongeur_profil_v2.py` (non réutilisé).
`art/source/blender/plongeur.py` est revenu à son état commité : aucune retouche d'angle n'y reste.

### Étape 1 faite (à valider par Julien) : pose idle_01 à 06
- Planche : `boards/journal/plongeur_v3_idle_base.png` (référence | idle 1 | idle 4, eau claire et eau sombre, x4).
- Journal : `art/journal/plongeur_v3.json`, entrée 1, verdict garde, SHA-256 `c9d55302e85b...`.
- Silhouette 48 px de haut (cible 46-48), largeur 42 px, case 80 px, caméra azimut 35°, élévation 15°.
- Mesure par carte d'identité (`tools/mesure/membres.py <dossier> --groupe idle --cote-proche d`) :

| image | bras proche | bras lointain | jambe proche | jambe lointaine | verdict |
|---|---|---|---|---|---|
| idle_01 | 119 px / 95 % | 110 px / 90 % | 83 px / 91 % | 83 px / 81 % | OK |
| idle_02 | 114 px / 93 % | 103 px / 89 % | 74 px / 85 % | 84 px / 81 % | OK |
| idle_03 | 114 px / 93 % | 103 px / 89 % | 74 px / 85 % | 84 px / 81 % | OK |
| idle_04 | 119 px / 95 % | 110 px / 90 % | 83 px / 91 % | 83 px / 81 % | OK |
| idle_05 | 117 px / 92 % | 114 px / 90 % | 82 px / 85 % | 81 px / 81 % | OK |
| idle_06 | 117 px / 92 % | 114 px / 90 % | 82 px / 85 % | 81 px / 81 % | OK |

- Conception : symétrique, tête grosse (casque 18 px), tronc plus étroit que les épaules (12 px contre 17 px),
  bras écartés en A, jambes écartées (au moins 3,6 px de vide entre elles), gants et bottes presque noirs, tuyau de corde
  devant (visible), bouteilles dans le dos. Couleurs : tronc kaki médian, manches kaki le plus clair, jambes kaki foncé.
- Défauts notés (journal) : bassin en bloc rectangulaire ; jambes un peu courtes ; contour interne entre parties pas encore
  fait (demandé : trait sombre de 1 px aux frontières, calculé sur la carte d'identité) ; boulons et cadre du hublot peu lisibles.

### Amélioration idle vers le héros de référence (un changement à la fois)
| étape | changement | essai | verdict | journal |
|---|---|---|---|---|
| 1 | collerette laiton + boulons | A : 2 px, boulons enfoncés | annulé (invisible) | entrée 2 |
| 1 | collerette | B : 3 px, dépasse le casque de 1 px | garde | entrée 3 |
| 1 | boulons | C : sur la surface, rayon 1,2 px | garde ; boulon gauche et centre à peine lisibles, droit caché par le tuyau (étape 6) | entrée 4 |

### Méthode de mesure (changée cette étape)
- `tools/mesure/membres.py` réduit désormais par BLOC MAJORITAIRE (8 x 8 px du rendu 640) au lieu d'une pixelisation moyenne.
  La pixelisation moyenne créait des parties fantômes sur les bords et faisait dépasser 100 % (corrigé).
- Options : `--groupe nage|idle`, `--cote-proche g|d` (modèle v3, noms bras_g, bras_d, ...).

### Essais d'angle sur l'ANCIEN modèle (profil) : résultats à lire avec précaution
- Premiers essais (azimut 30/40/50°) faits avec une caméra mal orientée (axe haut incliné de 45° à 30°) : mesures INVALIDES.
- Caméra corrigée (axe haut = Y), mesures valides sur idle, élévation 15° : bras lointain 42-54 % (30°), 27-52 % (40°),
  18-43 % (50°). Le bras lointain et la jambe lointaine restent cachés par le tronc, les bouteilles, le tuyau et le casque :
  c'est la raison du nouveau modèle, construit pour la face.
- Le bug de caméra est corrigé dans les deux scripts (`camera()` : `to_track_quat("-Z", "Y")`).

### Ce qui attend Julien
1. Valider ou corriger la pose idle du nouveau modèle (planche ci-dessus).
2. Référence cartoon : toujours ABSENTE de `art/references/` et de `origin` à cette étape. Comparé à ref_03 et ref_05.

### Ce qui n'est PAS fait (ordre demandé)
- Contour interne (1 px) calculé sur la carte d'identité ; nage (4 membres à chaque image) ; autres animations ;
  feuille, manifeste, jeu (miroir horizontal : le jeu le fait déjà, `scripts/plongeur.gd` ligne 112 `flip_h = direction < 0`),
  captures, robot, `gate.py M3` en clone neuf. Aucun de ces éléments n'est reconstruit pour le nouveau modèle.


Animations du plongeur : NAGE EN COURS, NON VALIDÉE. ARRÊT : décision de Julien demandée (voir ci-dessous).
Idle et creusage : code restauré à la version validée (HEAD) ; les tentatives faites avant validation sont annulées dans le journal.

## Nage : mesure par carte d'identité (état F, 8 images)
Mesure : `python3 tools/mesure/membres.py <dossier>` sur un rendu `PLONGEUR_IDENTITE=1` de `plongeur.py`.
Pour chaque image : pixels visibles d'un membre / part non cachée (visible ÷ surface du membre seul).
Un membre = son segment + son extrémité (gant du bras, botte de la jambe), du même côté (choix de mesure à valider).
Critère : visible >= 20 px ET non caché >= 60 %, sur chaque image.

| image | bras proche (vis / non caché) | bras lointain | jambe proche | jambe lointaine | verdict |
|---|---|---|---|---|---|
| nage_01 | 165 px / 86 % | 50 px / 33 % KO | 117 px / 81 % | 62 px / 54 % KO | ÉCHEC |
| nage_02 | 147 px / 87 % | 70 px / 44 % KO | 97 px / 72 % | 77 px / 65 % | ÉCHEC |
| nage_03 | 117 px / 84 % | 104 px / 61 % | 93 px / 74 % | 92 px / 72 % | OK |
| nage_04 | 93 px / 71 % | 127 px / 67 % | 92 px / 65 % | 88 px / 63 % | OK |
| nage_05 | 87 px / 65 % | 122 px / 64 % | 90 px / 67 % | 88 px / 62 % | OK |
| nage_06 | 112 px / 78 % | 121 px / 65 % | 96 px / 67 % | 56 px / 40 % KO | ÉCHEC |
| nage_07 | 146 px / 88 % | 92 px / 51 % KO | 108 px / 68 % | 44 px / 35 % KO | ÉCHEC |
| nage_08 | 164 px / 88 % | 57 px / 35 % KO | 112 px / 70 % | 57 px / 48 % KO | ÉCHEC |

Images en échec : nage_01, nage_02, nage_06, nage_07, nage_08 (5 sur 8). Membres proches : OK sur toutes les images.
Taille (rendu 640 px, 16 échantillons) : 51 à 53 px, cible 44 à 48 px : NON ATTEINTE.
Amplitude nage : 0,452 (seuil 0,45) : atteinte de justesse.

Cause mesurée (recouvrement par image) : les membres lointains sont derrière le corps en vue de profil.
- Bras lointain : caché par le tronc (24 à 32 px en certaines images), les bouteilles et le tuyau (zone au-dessus du tronc),
  et par le gant proche quand celui-ci descend au même endroit.
- Jambe lointaine : cachée par la jambe proche ou par le gant proche (image 7 et 8, jusqu'à 45 px).
- Tests essayés (une seule chose changée à la fois) : balayage du bras proche et du bras lointain sur plusieurs plages,
  opposition des bras, coude du bras lointain, jambes plus en arrière, épaules et hanches décalées de 2 px, tronc recentré,
  gants de 3,5 px. Aucun ne passe les 8 images : chaque réglage déplace l'occlusion d'un membre à l'autre.
  Le décalage des épaules et des hanches améliore les membres proches (bras proche 92 à 98 %) mais dégrade les lointains.

Options pour Julien (décision de design, pas de réglage de plus) :
1. Réduire la silhouette de nage à 44-48 px (casque et tronc plus petits, ou échelle propre à la nage ; l'idle validée
   est à 46 px et ne doit pas changer).
2. Dégager la zone au-dessus du tronc : bouteilles et tuyau plus bas ou plus fins (la zone bloque le bras lointain).
3. Assouplir le seuil pour les membres lointains (ex. 40 % au lieu de 60 %), puisqu'ils sont derrière le corps en vue de profil.
Je recommande 2 + 3 : le seuil de 60 % est atteint par les membres proches sur toutes les images.

Journal : nage annulée (entrée 93, première tentative), nage état F annulée pour validation (entrée 95, planche
`boards/journal/plongeur_nage_etape3_F.png`). Idle annulée (entrée 94, hors ordre).

## Refonte du héros : état exact (itération 2 : points 1 à 5 de Julien)
- Pose idle_01 : 46 px de haut dans une case de 80 px. Julien a validé la direction (casque laiton, kaki, gants sombres, 47 px).
- Étapes faites, UN changement à la fois, chacune avec planche avant/après (×4, eau claire et sombre) et entrée de journal
  (`art/journal/plongeur.json`, entrées 85 à 92) :
  1. Jambes en pas écarté (proche en avant, lointaine en arrière), bottes séparées : GARDÉ.
  2a. Kaki du côté lointain au ton médian (lisible seul) : GARDÉ.
  2b. Bras vers l'avant, gant sombre au poignet : GARDÉ.
  3. Tuyau d'air en corde beige-brun, 3 à 4 px, courbe arrière : GARDÉ.
  4a. Tronc éclairci (ton kaki intermédiaire ajouté, 96 couleurs) : GARDÉ.
  4b. Tronc arrondi : ANNULÉ (aucun changement lisible).
  5a. Anneau du hublot en bronze sombre : GARDÉ.
  5b. Deux barres de grille de 1 px : ANNULÉES (illisibles à x1).
- Planche finale : `boards/journal/plongeur_pose_idle_v3_avant_apres.png` (départ de session | final, référence à gauche).
- Points restés faibles (à juger par Julien) : genou peu lisible ; bras et jambe proches ont le même kaki clair ; tronc
  encore étroit (bouteilles et bras le couvrent à ce cadrage) ; bord gauche et bas du hublot se fond dans le casque.
- Palette : rampes `laiton` (4), `kaki` (4 : #3a3426, #8a7e58, #b8ad84, #d8cca0), `gant` (3). 19 rampes, 96 couleurs, sans noir pur.
- Référence cartoon de Julien : TOUJOURS ABSENTE de `art/references/` et de `origin` à cette itération. Comparaison faite avec
  ref_03 et ref_05 seulement. Quand elle arrive : la comparer sur la planche et l'ajouter à SOURCES.md avec son adresse.
- Assets du jeu : toujours l'ancien héros (37 px). Reconstruction après validation de la pose.

## Décision demandée à Julien
Valider (ou corriger) la pose idle_01 de `boards/journal/plongeur_pose_idle_v3_avant_apres.png`. Ensuite seulement :
les 41 animations (nage, idle, creusage, attaque, saut, dégâts, mort) avec bras et jambes qui bougent franchement
(amplitude nage >= 0,45, idle >= 0,10), puis reconstruction des assets, du jeu et des captures.

## Acquis de M3 (SUCCES, dépôt et clone neuf à c488e94)
- `python tools/gate.py M3` → SUCCES (dépôt, puis clone neuf). Robot 13/13. Sortie complète dans RAPPORT.md.
- Créatures du biome 1, fond d'eau sur 300 m, captures dans les seuils, journal poisson réparé.
- Dettes de M3 restantes : sons non écoutés, crédit son_impact non affiché en jeu, autotile non branché, fonds provisoires,
  libellé « radeau » figé dans les captures à 60 m.

## Créatures de la fosse (M4) : raie_lanterne en pause
- `art/source/blender/raie_lanterne.py` : 2 changements gardés (ventre fin, aile avant haussée), 1 en cours (aile arrière,
  planche `boards/journal/raie_lanterne_avant_apres_3.png` non jugée). Pas dans le manifeste. Julien a demandé de ne pas toucher
  aux créatures pendant la refonte du héros : elles seront remises à l'échelle du nouveau héros plus tard.

## Derniers résultats de contrôle
- `python tools/gate.py M3` (dépôt, commit c488e94) → SUCCES. Sortie complète dans RAPPORT.md (section M3).
- `python tools/gate.py M3` (clone neuf de la branche, commit c488e94) → SUCCES, code 0.
- Robot : 13 étapes sur 13 (`python3 tests/robot/robot.py`), étape `combattre` incluse.

## Ce qui a été fait pour réussir M3 (cette session)
- Robot : étape `combattre` (approche à distance réelle, 18 px, relue à chaque pas) ; reprise après remontée au radeau pendant la récolte.
- Journal `poisson_volant` : entrée 15 réparée (image dupliquée remplacée par un rendu réel de l'état annulé, empreinte unique).
- Fond d'eau : dégradé sur 300 m (au lieu de 260 px, qui saturait à 16 m) ; ciel en dégradé ; teinte sous-marine plus claire.
  Mesure par `tools/mesure/captures.py` : dominante 6 à 16 %, ombre 17 à 22 % sur les 18 captures. Planche : `boards/journal/captures_60m_descente_avant_apres.png`.

## Plan M4 (cases à cocher)
- [ ] fosse_sombre : 3 créatures vivantes (raie_lanterne, anguille_ombre, meduse_cloche), chacune : script Blender, 18 images, pixel, feuille, 3 itérations, journal (≥6 entrées)
- [ ] mini-boss gardien_cloche : sprite vivant, attaque, mort, au moins une animation `phase2…`
- [ ] tileset 47 cases pour fosse_sombre
- [ ] 4 fonds pour fosse_sombre
- [ ] 12 props pour fosse_sombre
- [ ] 3 variantes de scaphandre (data_id `plongeur_…`, vivant)
- [ ] 15 effets au total (8 en place : 7 à ajouter)
- [ ] 14 sons au total (9 en place : 5 à ajouter, téléchargés avec licence et crédités dans CREDITS.md)
- [ ] jeu : captures fosse_sombre (profondeurs 150 et 250 m, descente/remontée, lampe/sans), étape robot `mini_boss`
- [ ] `python tools/gate.py M4` → SUCCES (dépôt, puis clone neuf)

## Dettes de M3 (à traiter pendant M4 ou avant M6)
- Sons : 9 fichiers jamais écoutés (métadonnées seulement). Julien doit les juger.
- Crédit de son_impact (CC-BY-3.0) : présent dans CREDITS.md, PAS encore affiché dans le jeu.
- Autotile des tuilesets (47 cases) : généré, pas branché dans `scripts/monde.gd`.
- Fonds provisoires (8) ; coques lointaines lues comme des boîtes.
- Captures : libellé « Vous êtes sur le radeau » figé à 60 m (état HUD pendant la capture).

## Besoin de Julien
- Supprimer à la main le fichier vide `/cycle3.sh` à la racine (hors dépôt ; la suppression par l'agent a été bloquée).
- Écouter les 9 sons (`assets/sons/`) et dire lesquels sont inutilisables ; crédit son_impact à valider.
- Juger le ressenti de l'eau sombre (teinte plus claire) et la lisibilité du poisson volant et de la carangue à x1.
- Le .exe n'est pas lancé (pas de Wine) : à tester sur Windows.

## Blocage en cours
Aucun. Hypothèses à noter ici si M4 bloque (une ligne par hypothèse testée).

## Feuille de route (validée par Julien)
- M4 : biome 2 (fosse_sombre), mini-boss gardien_cloche, 3 variantes de scaphandre, 15 effets, 14 sons.
- M5 : menus, options, pause, icône, export Windows dans builds/, PLAYTEST.md et PLAYTEST_JOURNAL.md (≥ 2 parties).
- M6 : relecture par un sous-agent indépendant (RELECTURE.md), corrections, RAPPORT.md final (Fait / Non vérifié / Limites / Écarts vers Dead Cells).
