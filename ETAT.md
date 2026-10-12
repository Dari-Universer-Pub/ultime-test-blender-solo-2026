# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante : NAGE (essai 1) — ÉCHEC DU TROIS QUARTS, ARRÊT POUR VALIDATION DE JULIEN
Julien a validé la pose idle v6 (`add270b`). L'ancre est verrouillée : `art/references/ancre_plongeur_v6.png` (+ rendus x6 eau claire et eau sombre). STYLE.md, DECISIONS.md et AGENTS.md sont à jour.

Essai de nage (pose dans le plan visible, bras qui se lèvent et s'abaissent, jambes en ciseaux) : mesuré, il ne tient pas.
- Bras lointain caché dans les 8 images : 12 à 59 % non cachés (seuil 60 %). Cause : la caméra est en trois quarts, le bras du côté opposé passe derrière le tronc quand il est sur le côté.
- Cycle en 5 poses distinctes sur 8 : images 2=8, 3=7, 4=6 identiques pixel pour pixel (phase symétrique).
- Lecture : figure debout de face, pas de glisse ni d'anticipation.
- Tenu : hauteur 71 à 72 px, amplitude 0,50, 0 pixel isolé, 23 couleurs.
- Écart de style à valider : la séparation par la valeur (bras proche 81 contre tronc 131 en luminance) vient d'un assombrissement des manches, que l'ancre idle n'a pas.

Planche : `boards/plongeur_v6_nage_essai1.png` (ancre idle et huit images, quatre fonds, x4, mesures image par image). Images : `art/pixel/plongeur_v6/nage_essai1/`. Code : `art/source/blender/plongeur_v6.py` (`pose_nage`, `rendre_nage_images`).

### Proposition (non réalisée, à valider)
- A (recommandée) : nage horizontale en crawl, corps incliné vers l'avant de 60 à 70° (tout le corps tourne d'un bloc), bras qui passent au-dessus de la tête dans le plan sagittal. Le bras proche passe devant le corps, le bras lointain reste au-dessus, donc visible en trois quarts. Risque : la hauteur du sprite doit rester entre 56 et 80 px. Un seul essai, puis mesure.
- B : bras en crawl dans le plan vertical de l'axe de nage, sans inclinaison : seul le bras qui avance est visible, à mesurer.
- À corriger dans tous les cas : la phase de l'animation n'est pas symétrique (images 2=8, 3=7, 4=6).

### Non fait (attend Julien)
- Idle (animation), creusage, attaque, saut, dégâts, mort, feuille, manifeste, jeu, tuiles 24 px, robot, `gate.py M3`.

## Ancienne phase : PLONGEUR V6 SANS CONTOUR (style peint doux) — ARRÊT POUR VALIDATION DE JULIEN
Julien a retiré le contour : trop lourd, « affreux ». Style peint, doux, SANS trait sombre sur le pourtour ni entre parties. La forme tient à la valeur et à l'ombrage. Plus aucun objectif de contour (épaisseur, blocs 2x2, part dans la silhouette).
Le contour est encore dans l'historique git (commit `cb8d19f`). Rien n'est téléchargé. `tools/gate.py` et `tools/outils.json` non touchés.

- Script : `art/source/blender/plongeur_v6.py`. Pipeline : rendu couleur (session persistante `tools/blender_session/`) -> `tools/pixelisation/nettoyage.py` (pixels isolés seulement) -> sprite. Le contour (`contour_dc.py`) est retiré du dépôt.
- Sprite final : `art/pixel/plongeur_v6/idle_01.png`. Archive de la version avec contour : `art/pixel/plongeur_v6/archive_contour/`.
- Journal : `art/journal/plongeur_v6.json` (20 entrées). Règle : 5 % minimum des pixels changés par passe ; sous le seuil, l'étape est annulée (sauf mention).
- Planche : `boards/plongeur_v6_sans_contour.png` (eau claire, eau sombre, damier, niveaux de gris, x6) + mesures et écarts.

### Retouches (une à la fois, planche avant/après x6)
| étape | changement | mesure | verdict |
|---|---|---|---|
| 15 | retrait du contour + 38 pixels isolés corrigés | 29,8 % | garde |
| 16 | vitre bleu-noir, reflet net 2 px | 9,3 % | garde |
| 17 | bras identiques (longueur, épaisseur), manchette sombre, gant en mitaine | 16,9 % | garde |
| 18 | ceinture seule à 3 px | 1,6 % | annulée (sous 5 %), reprise à 19 |
| 19 | ceinture 3 px avec boucle, quatre plis nets (tronc et manches) | 5,0 % | garde |
| 20 | bouteille arrondie derrière l'épaule, valve laiton, corde 3 px à torsion (6 faces), reliée à la valve | 5,5 % | garde |
| 21 | jambes plus longues, genou plus rond | 7,0 % | garde |

### Objectifs chiffrés (sprite final, mesurés)
| objectif | cible | mesure | verdict |
|---|---|---|---|
| hauteur | 70 à 74 px | 72 px | OK |
| couleurs | 24 à 32, rampes de 3 à 4 tons | 23 utilisées sur 26 de palette ; laiton 4, beige 4, cuir 3, violet 3, métal 3, verre 3, reflet 1, corde 3 | OK (23 utilisées : sous 24) |
| pixels isolés | 0 | 0 | OK |
| hors palette / noir pur / blanc pur | 0 | 0 / 0 / 0 | OK |
| membres visibles | >= 30 px, >= 60 % | bras proche 227 px / 97 %, bras lointain 165 px / 73 %, jambe proche 246 px / 98 %, jambe lointaine 183 px / 68 % | OK |
| tuyau (corde) | < 10 % | 6,1 % | OK |

### Écarts et trois points les plus faibles (planche)
1. Bras proche et tronc : même valeur (beige), séparés seulement par l'ombrage.
2. Plis du tronc : lus comme une coupure en deux tons, pas comme des plis nets.
3. Corde : torsion à peine lisible à x6 ; bouteille : bord gauche qui se fond dans l'eau sombre (à corriger par la valeur, pas par un trait : non fait, sous le seuil de 5 %).
- Genou : arrondi mais de même valeur que la cuisse.
- Lumière cyan : présente sur le bord droit (pixels clairs) ; silhouette haut-gauche lisible sur eau claire.

### Passes annulées ou non faites
- Retrait du pli du genou (test, 0,8 %) annulé ; passes de majorité 3x3 de la version précédente (0,5 à 1,2 %) annulées ; corde à 0,085 (3,1 %) annulée ; ceinture seule (1,6 %) annulée.
- La correction de la valeur du bord de la bouteille n'a pas été faite : elle changerait moins de 5 % des pixels.

### À faire après validation
- NAGE d'abord : huit images, quatre membres lisibles et mesurés à chaque image, hauteur 44 à 80 px, amplitude >= 0,45 ; planche de toutes les images x4 sur eau claire et eau sombre ; arrêt pour validation.
- Puis les autres animations, la feuille, le jeu, les tuiles 24 px, le robot, `python tools/gate.py M3` dans un clone neuf.

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
