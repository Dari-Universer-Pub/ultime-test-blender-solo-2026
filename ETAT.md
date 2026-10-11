# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
PAUSE sur M4, demandée par Julien (« STOP sur M3 ») : refonte du héros (plongeur) d'abord.
Étape en cours : UNE pose fixe, idle_01, en 47 px dans une case de 80 px. ARRÊT en attente de la validation de Julien
sur cette pose. Les 41 animations ne sont PAS refaites tant que Julien n'a pas validé.

## Refonte du héros : état exact
- Modèle : `art/source/blender/plongeur.py` réécrit en proportions de dessin animé (grosse tête laiton, tronc court,
  bras et jambes courts et épais, gros gants et bottes bleu-violet très sombre, bouteilles de dos, tuyau d'air clair).
  Dimensions écrites en pixels du rendu final (1 px = 0,0466 unité). Caméra : 80 px, `LARGEUR_CADRE = 4.12`, rendu 640 px.
- Palette : rampes `laiton` (4 tons), `kaki` (3), `gant` (4) ajoutées à `art/palette.json` : 19 rampes, 96 couleurs, pas de noir pur.
- Mesure de la pose idle_01 : hauteur de contenu 47 px dans une case de 80 px (59 %). Cible : 46 à 48 px.
- Planches (référence | avant | après, ×4, eau claire et eau sombre) :
  - `boards/journal/plongeur_pose_idle_v2b_laiton_avant_apres.png` (A, gardé)
  - `boards/journal/plongeur_pose_idle_v2c_membres_avant_apres.png` (B, gardé)
  - `boards/journal/plongeur_pose_idle_v2d_hublot_avant_apres.png` (C, gardé)
  - `boards/journal/plongeur_pose_idle_v2e_tuyau_avant_apres.png` (D, annulé : tuyau fondu dans le bras clair)
  - `boards/journal/plongeur_pose_idle_v2f_tuyau_arriere_avant_apres.png` (D2, gardé)
  - Journal : `art/journal/plongeur.json`, 5 entrées ajoutées (entrées 80 à 84).
- Outil de planche : `tools/planches/heros_pose.py` (assemblage seulement, Pillow).

## Ce qui n'est PAS fait sur le héros (à juger par Julien)
- Assets du jeu (`assets/sprites/plongeur/`) : toujours l'ancien héros de 37 px. Ils ne seront reconstruits qu'après validation.
- Référence de Julien (« plongeur de dessin animé, casque en laiton ») : ANNONCÉE mais ABSENTE du dépôt et de `origin`
  (`art/references/` ne contient que ref_03 et ref_05). Comparaison faite avec les deux photos seulement.
- Tuyau d'air : lisible à l'arrière, mais son liseré clair se confond avec le contour pixelisé (journal entrée 84).
- Cadre laiton du hublot peu contrasté avec le casque doré ; boulons non visibles à 47 px.
- Membres du côté lointain trop sombres pour se lire seuls.
- Tronc plus sombre que la référence (kaki médian ; la photo de 1951 a une combinaison plus claire).
- Gate : le contrôle M3 était SUCCES avant cette refonte ; il n'a pas été relancé sur les nouveaux assets (ils ne sont pas construits).

## Décisions attendues de Julien
1. Valider ou corriger la pose idle_01 (planche v2f ci-dessus) : proportions, couleurs, hublot, tuyau.
2. Fournir la référence cartoon (fichier dans `art/references/` et adresse dans SOURCES.md) ou confirmer de comparer avec ref_03 et ref_05.
3. Après validation : les 41 animations (nage, idle, creusage, attaque, saut, dégâts, mort) avec bras et jambes qui bougent franchement.

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
