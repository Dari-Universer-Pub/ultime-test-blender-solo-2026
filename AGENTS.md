# AGENTS.md — Règles permanentes (à relire au début de CHAQUE session)

Projet : **LES CLOCHES DE VAREKH**, jeu 2D pixel art sous Godot 4 (GL Compatibility).
Tu travailles UNIQUEMENT dans ce dossier. Tu ne lis aucun autre projet.

## Les 4 fichiers qui commandent

| Fichier | Rôle |
|---|---|
| `docs/BRIEF.md` | **Quoi** : le jeu visé, la qualité exigée (niveau professionnel, référence Dead Cells). |
| `PLAN.md` | **Dans quel ordre** : les phases M0 → M6 d'un SEUL et même jeu. |
| `ETAT.md` | **Où tu en es** : phase courante, dernier résultat du contrôle, blocage en cours. Tu le tiens à jour. |
| `tools/gate.py` | **Quand c'est fini** : `python tools/gate.py <phase>`. Une phase est finie quand il affiche `SUCCES`, jamais avant. |

Le but n'est PAS un prototype : c'est le premier jet du jeu final. À la fin de M6, il existe un
échantillon jouable où tout est vraiment là (assets, nature, créatures, sons, lumière, sensations),
et tout le reste du jeu existe en données JSON riches et reliées.

## La boucle de travail (la seule autorisée)

0. **Au début de CHAQUE session, outils d'abord.** La sandbox peut avoir été réinitialisée : si
   `/opt/outils-varekh/bin/godot` n'existe pas, tu RÉINSTALLES les outils déjà compilés (1 minute) :
   `bash tools/pixelisation/outils_varekh/INSTALLER_OUTILS.sh` puis `bash /opt/outils-varekh/verifier.sh`
   (doit afficher `SUCCES`). Pour trouver le script : `find / -name INSTALLER_OUTILS.sh 2>/dev/null`
   (si le zip n'est pas décompressé : `find / -name "*outils*.zip" 2>/dev/null`, puis `unzip`).
   Tu ne recompiles JAMAIS Godot, Blender ni Aseprite, même si une réinstallation échoue : tu lis les
   `.log` du vérificateur. Si le zip des outils a disparu, écris dans `ETAT.md` (Besoin de Julien) :
   « redonner le zip des outils », et tu attends.
1. Lis `ETAT.md`. Tu travailles **uniquement sur la phase courante**. Rien d'une phase suivante.
2. Fais le travail de la phase (voir `PLAN.md`).
3. Lance `python tools/gate.py <phase courante>`.
4. **ÉCHEC** → tu corriges ce que le contrôle liste, tu relances, tu recommences. Tu ne fais RIEN
   d'autre tant que la phase n'est pas en `SUCCES` : pas de documentation, pas de code d'une autre
   phase, pas de « je reviendrai dessus plus tard ».
5. **SUCCES** → commit, colle la sortie complète du contrôle dans `RAPPORT.md`, passe `ETAT.md` à la
   phase suivante, et continue tout seul. Seule exception : une phase marquée **ARRÊT POUR
   VALIDATION** dans `PLAN.md` ; là tu t'arrêtes et tu attends Julien.

## Interdits absolus

- Modifier, renommer, copier, contourner ou affaiblir `tools/gate.py` ou `tools/outils.json`
  (sauf la clé `robot`, que tu crées en M2). L'empreinte de `gate.py` est vérifiée à chaque audit.
- Dessiner un asset par du code : Pillow, numpy, OpenCV, `ImageDraw`, `putpixel`, `draw_rect` pour
  un personnage… Pillow/numpy ne sont permis que dans `tools/mesure/` (mesurer),
  `tools/planches/` (assembler des planches), `tools/pixelisation/` (réduire et quantifier un RENDU Blender) et `tests/robot/` (captures du robot).
- Télécharger un modèle 3D, un rig ou une animation toute faite. **Tu construis TOUT toi-même dans Blender**,
  par tes propres scripts Python Blender (`bpy`) : modélisation, matériaux, squelette, poses et animations, caméra,
  lumière, rendu. Aucun outil d'assets fourni, aucune « usine » : c'est toi l'artiste 3D. Chaque asset construit a
  son script dans `art/source/blender/<id>.py`, qui refait le `.blend` et le rendu de zéro.
- Écrire « fait », « testé », « vérifié » sans la sortie d'une commande ou un fichier qui le prouve.
- Déclarer une phase ou le jeu « terminé » sans `SUCCES` du contrôle.

## Règle de l'œil (pour TOUT asset visible — la plus importante du projet)

Tu as la vision : sers-t'en à chaque pas. Un asset n'est pas bon parce que le script a tourné,
il est bon parce que tu l'as REGARDÉ et qu'il est beau.

1. **Un seul changement visuel à la fois** (un réglage de rendu, de cadrage, de pixelisation, une
   retouche Aseprite). Jamais deux changements sans regarder entre les deux.
2. **Après chaque changement**, fabrique la planche avant/après avec
   `python tools/planches/comparer.py AVANT.png APRES.png boards/journal/<id>_<n>.png [--case x,y,w,h]`.
3. **Ouvre et REGARDE l'image** (lis le fichier image, pas son nom). Puis juge-la avec ces 7 critères,
   chacun en une phrase précise : silhouette lisible à ×1 ? couleurs de la base conservées ?
   cadrage (personnage qui remplit sa case) ? taille finale (héros 70 à 74 px de haut, case 112 x 112) ?
   détails (casque, hublot, mains) lisibles ? cohérence avec l'ancre (`art/references/ancre_plongeur_v6.png`)
   et le reste du jeu ? pixels parasites ou bords sales ? Style peint doux, SANS contour : la forme tient à la
   valeur et à l'ombrage (on regarde aussi en niveaux de gris et sur eau sombre).
4. **Décide** : `garde` si c'est mieux, `annule` si ce n'est pas mieux (tu reviens en arrière).
5. **Écris l'entrée** dans `art/journal/<id>.json` : l'image, son SHA-256 (affiché par comparer.py), les 7 critères
   et le verdict (format dans `PLAN.md`). Une entrée laissée vide fait échouer le contrôle. Le contrôle vérifie ce journal : une entrée par changement, une image
   différente à chaque fois, les 7 critères remplis.
6. **Compare toujours aux références** : avant de construire, cherche 2 ou 3 images de référence libres (silhouette,
   proportions, couleurs), garde-les dans `art/references/` avec leur adresse, et pose-les à côté de ton rendu
   sur chaque planche. On s'inspire et on mesure, on ne copie jamais.

## Règle d'or des blocages (il n'existe AUCUNE limite d'essais)

Un blocage se résout. Il ne s'abandonne pas et ne se contourne pas en baissant la qualité.
1. Réduis le défaut au plus petit cas qui échoue (un modèle, un script, un appel).
2. Liste les causes possibles ; teste-les une par une en changeant UNE seule chose à la fois.
3. Avant chaque essai, SUPPRIME le fichier de sortie attendu, puis vérifie le code de retour, la date
   et la taille du NOUVEAU fichier. Ne mesure jamais un fichier périmé.
4. Regarde le résultat lui-même (l'image, le log complet), pas seulement une mesure.
5. Lis les erreurs en entier, la documentation officielle, essaie une autre version de l'outil
   (autres réglages de rendu Blender, Workbench ou EEVEE), un autre format (GLB, FBX, OBJ, Blend), un autre import, un autre modèle.
6. Note chaque hypothèse testée, une ligne, dans `ETAT.md` (section Blocage).
7. Si la cause dépend de quelque chose que tu ne peux pas obtenir seul (compte, téléchargement
   bloqué), écris exactement ce qu'il te faut dans `ETAT.md`, puis cherche un autre chemin vers
   le MÊME but (autre méthode dans Blender ou Aseprite). Jamais de dessin par code à la place.

## Outils (chemins exacts, ne les cherche pas dans le PATH)

Les outils sont DÉJÀ COMPILÉS (zip des outils donné par Julien, ou dépôt `kit-outil-v2` : dossier `outils/` + `INSTALLER_OUTILS.sh`). Tu ne compiles
JAMAIS Godot, Blender ni Aseprite. Si `/opt/outils-varekh/bin/godot` n'existe pas (sandbox neuve) :
`bash tools/pixelisation/outils_varekh/INSTALLER_OUTILS.sh` (1 minute, sans réseau), puis `bash /opt/outils-varekh/verifier.sh`
qui doit afficher `SUCCES`.

- Godot 4.4.1 : `/opt/outils-varekh/bin/godot` (export Windows prêt : `--export-release "Windows Desktop" builds/x.exe`)
- Blender 5.2.1 LTS : `/opt/outils-varekh/bin/blender` (`-b` pour le rendu sans écran, Workbench et EEVEE marchent)
- Aseprite 1.3.18.6 : `/opt/outils-varekh/bin/aseprite`
  (ligne de commande : `--batch`, `--script fichier.lua`, `--sheet`, `--data`, `--list-tags`, `--format json-array`).
- Python avec numpy si la sandbox n'en a pas : `/opt/outils-varekh/bin/python`
- **Assets** : Blender en ligne de commande, `/opt/outils-varekh/bin/blender -b --python <script.py>`. Tu écris
  toi-même toute la chaîne : construction du modèle, rig, animation, rendu (caméra orthographique fixe, mêmes réglages
  pour tous les assets), rendu DIRECT à la taille finale (pas de réduction après coup), quantification PAR MATIÈRE
  dans `tools/pixelisation/`, nettoyage des pixels isolés, et finition dans Aseprite. Garde un style commun : écris
  tes réglages (lumière, caméra, taille en px) une fois dans `STYLE.md` et réutilise-les pour tous les assets.
  Décision de Julien du 12/10 (voir `DECISIONS.md`) : héros 70 à 74 px de haut dans une case 112 x 112, trois quarts
  de face, style peint doux SANS contour, une seule lumière en haut à gauche. L'ancre est le sprite
  `art/references/ancre_plongeur_v6.png` (rendus x6 à côté) : chaque nouvel asset du héros doit la respecter.
- Vision : `bin/godot` ouvre tout seul un écran virtuel avec OpenGL, donc `get_viewport().get_texture().get_image().save_png()`
  marche. `bin/godot-capture <projet> <dossier> <nb_images> [scène]` filme le jeu image par image en PNG.
  `bin/capture-ecran sortie.png` capture tout l'écran pendant que le jeu tourne. Ensuite tu REGARDES le PNG.
- Un seul système de chemins (Linux) pour les trois outils : plus aucune conversion Windows/WSL.
- Ces chemins sont dans `tools/outils.json`, que `gate.py` utilise. Si l'installateur a dû se rabattre sur
  `~/outils-varekh` (pas de droit sur /opt), il affiche le `outils.json` exact à utiliser : c'est la
  seule modification permise de ce fichier, avec la clé `robot`. Ne conclus jamais « outil absent ».

## Si ta session s'interrompt

Une sandbox réinitialisée perd les outils installés, pas le travail commité : refais l'étape 0
(réinstallation en 1 minute), puis reprends.

Tout ce qu'il faut pour reprendre est dans `ETAT.md` et `git log`. Mets `ETAT.md` à jour à chaque
étape importante, pas seulement à la fin.

## RÈGLE ANIMATION (permanente, pour tout lot : creusage, attaque, saut, dégâts, mort)

Julien ne demande plus d'image pour appliquer cette règle : elle s'applique à chaque lot.

A. **Table de poses d'abord.** Avant de poser quoi que ce soit, une ligne par image dans
   `art/pixel/plongeur_v6/<lot>/TABLE_POSES.md` : nom, angle du manche ou de l'arme (plan x-z
   et inclinaison 3D par rapport à la verticale), point d'impact ou position de l'outil, inclinaison
   du buste, position des deux mains, ce qui doit se lire en silhouette.

B. **Cible 3D haute qualité.** Pose le modèle 3D d'après la table et rends chaque pose en haute
   qualité (plus grande que 112 px, même caméra, même modèle). C'est la planche « cible » du lot :
   Julien la valide EN PREMIER. Tant que la planche cible n'est pas validée, pas de pixel art.

C. **Contrôles automatiques sur chaque pose, dans la scène 3D, avant le rendu :**
   1. les deux mains touchent l'outil (distance main-manche proche de zéro, les deux mains) ;
   2. l'outil est relié au corps (jamais flottant) ;
   3. les deux bras visibles : bras proche au moins 45 %, bras lointain au moins 40 % (carte
      d'identité) ;
   4. angle de l'outil différent d'au moins 40 degrés de l'image précédente quand le geste l'exige ;
   5. hauteur du sprite finale dans la plage de l'ancre (70 à 72 px, outil compris) ;
   6. zéro pixel isolé, images distinctes (hash), aucun contour (au moment du pixel art).
   Si un contrôle échoue, change la pose (épaule, buste, position de l'outil). Ne jamais lâcher
   l'outil, ni cacher un bras, pour passer un test. Si aucune pose ne passe, dis-le à Julien avec
   les chiffres au lieu de rendre une pose qui triche.

D. **Outil (pioche ou autre)** : modélisé comme une vraie pièce. Manche 3 px minimum. Tête de
   pioche de mineur courbée, une pointe de chaque côté, 12 à 14 px de large quand elle est de profil
   (au moins 10 px à l'impact), mesurée à ×1 et notée dans le fichier de mesures.

E. **Présentation puis arrêt.** Planche cible 3D d'abord, puis planche pixel à côté de l'ancre
   (×4 et ×1), avec le tableau des contrôles (OK ou échec pour chaque image), les mesures de tête et
   de hauteur, les écarts annoncés tels quels. Arrêt pour validation après chaque lot.

A bis. **Planche d'intention (avant toute 3D).** Pour chaque lot, une planche en deux dimensions, en
   coordonnées écran : l'ancre estompée en fond, et par-dessus, pour chaque image, un squelette à plat
   (tête, buste, épaules, coudes, deux mains, hanches, pieds) et l'outil (manche et tête, avec ses deux
   extrémités). Images numérotées. Sous chaque image, une ligne : angle de l'outil (degrés depuis la
   verticale basse, sens horaire), inclinaison du buste, ce que la silhouette doit raconter. La table de
   l'intention est dans le JSON du lot. Julien valide ou corrige cette planche avant tout passage à la 3D.

B bis. **Triche caméra déclarée.** Pour atteindre les positions de la planche d'intention, pose par pose,
   tu peux : étirer un bras jusqu'à +40 % de sa longueur, décaler une épaule, tourner le buste, déplacer
   l'outil. Seule la silhouette à l'écran compte. Interdits : cacher un bras, laisser l'outil flotter sans
   main, faire traverser le torse par le manche, changer la caméra, la lumière ou le style de l'ancre.
   Chaque triche est notée dans `TABLE_POSES.md` (valeur par image).

C bis. **Contrôles.** Ils remplacent le contrôle 3 de C pour la portée des bras : deux mains sur le manche
   (distance en pixels écran proche de zéro, les deux mains) ; deux bras visibles (bras proche au moins 45 %,
   lointain au moins 40 %) ; hauteur 70 à 72 px outil compris ; tête d'acier 12 à 14 px (10 minimum à
   l'impact) ; angle entre images successives d'au moins 40 degrés ; zéro pixel isolé (au pixel art).
   La portée physique des bras n'est plus un contrôle : c'est la triche déclarée de B bis qui la remplace.

Ordre imposé : planche d'intention (A bis), validée par Julien → cible 3D (B) → pixel art.
