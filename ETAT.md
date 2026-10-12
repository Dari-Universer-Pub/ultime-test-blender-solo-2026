# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante : PLONGEUR V4 (refonte complète demandée par Julien), étape 1 = rendu haute résolution, EN ATTENTE DE VALIDATION
Julien trouve le héros v3 trop moche et demande de tout recommencer. Décisions :
- v3 est archivé : `art/source/blender/archive/plongeur_v3.py` (+ `.blend`), journal `art/journal/plongeur_v3.json` conservé ; ne pas le réutiliser.
- Nouveau script : `art/source/blender/plongeur_v4.py`, construit tout dans Blender (pas de téléchargement, pas de pixel par code).
- Méthode en deux temps : (1) rendu HAUTE RÉSOLUTION 768 px, sans pixelisation, trois quarts (azimut 35°, élévation 15°), clé haut-gauche, fond transparent : ARRÊT pour validation de Julien ; (2) seulement après validation : réduction à 46-48 px, quantification, contour sombre sélectif + contour interne, carte d'identité, mesure des quatre membres (>= 20 px et >= 60 %) : ARRÊT pour validation.
- Ensuite seulement : nage (44-48 px, amplitude >= 0,45), puis idle, creusage, attaque, saut, dégâts, mort, feuille, manifeste, jeu, captures, robot, `python tools/gate.py M3` dans un clone neuf, remise à l'échelle des créatures.

### v4 : pixelisation par matière (à valider) — les retouches 1 à 4 sont faites
- Julien a rejeté la première pixelisation (blob beige, laiton perdu, bruit violet) : refaite de zéro, pilotée par matière.
- Méthode : rendu 320 px (4 x 80, cadre 5,6), carte d'identité des matières (laiton, acier, verre, toile, cuir, caoutchouc, corde, bouteille) et des groupes (membres) ; réduction couleur par moyenne, matière et groupe par majorité ; quantification par matière sur la luminance seule ; contour sombre sélectif ; contour interne 1 px ; nettoyage des pixels isolés.
- Outils : `tools/pixelisation/pixeliser_matiere.py`, `tools/planches/pixel_quatre.py`, palette `art/palette_plongeur_v4_matiere.json` (30 tons).
- Mesures : 47 px de haut ; 0 pixel isolé après nettoyage (40 avant) ; 17 couleurs distinctes dans l'image ; aucun noir pur.
- Membres (critère >= 20 px et >= 60 % non cachés) : ÉCHEC pour le bras lointain (43 px, 51 %) et la jambe lointaine (49 px, 60 %). Cause : ils sont cachés par le tronc et la jambe proche dans cette pose. Corriger demande une décision de pose (écarter le bras et la jambe lointains) : je n'ai pas touché au modèle.
- Points que le modèle doit changer, à décider avec Julien : corde à 2-3 px (aujourd'hui ~5 px) ; reflet du hublot à 2 px (aujourd'hui 1 px) ; anneau gris du hublot plus épais.
- Palette : 30 tons par matière (demande de Julien) ; l'ancienne cible 64-96 couleurs n'est pas atteinte, à trancher.
- Planche finale : `boards/journal/plongeur_v4_pixel_final.png` (rendu haute résolution à gauche, pixel ×4 sur eau claire, eau sombre et damier).
- Journal : `art/journal/plongeur_v4.json`, entrées 21 à 28.

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
