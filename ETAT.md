# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
PAUSE sur M4, demandée par Julien (« STOP sur M3 ») : refonte du héros (plongeur) d'abord.
Étape en cours : UNE pose fixe, idle_01, en 47 px dans une case de 80 px. ARRÊT en attente de la validation de Julien
sur cette pose. Les 41 animations ne sont PAS refaites tant que Julien n'a pas validé.

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
