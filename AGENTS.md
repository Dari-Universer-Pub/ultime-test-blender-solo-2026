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

Méthode actuelle, dans cet ordre. Aucune validation humaine intermédiaire : l'arrêt humain est uniquement
la fin de la phase indiquée dans `PLAN.md`.

1. **Fiche d'animation écrite** (`art/pixel/<perso>/<lot>/FICHE.md` + `fiche.json`) : rôle du lot, pose de
   chaque image, durée (en images), points de prise de l'outil, pointe de l'outil, cible (ce que la pointe
   touche), ordre des calques par image, chevauchements autorisés ou interdits par paire de parties, moment
   d'impact, visibilité déclarée de chaque bras par image.
2. **Pièces plates** rendues à la taille finale (112 px) par la même chaîne que l'ancre, une pièce seule
   par rendu (`tools/` et `art/source/blender/`). Les pièces articulées ont des extrémités fermées ou une
   pièce de recouvrement à chaque articulation. Le bloc main + outil est UNE seule pièce : le gant tient le
   manche, il n'est jamais animé à part.
3. **Assemblage par fichier de pose** : chaque image est un fichier de pose (pièce, variante d'angle,
   pivot entier, ORDRE D'AFFICHAGE EXPLICITE de bas en haut). La profondeur par pixel ne sert qu'au test de
   remontage de l'ancre ; pour les poses, c'est l'ordre écrit qui décide (un gant peut passer devant ou
   derrière le casque, jamais le mélanger avec lui).
4. **Quatre poses clés d'abord** (armement, frappe en pleine descente, impact, retour). Boucle rapide :
   une dizaine d'essais par pose, chaque essai rendu et contrôlé. Puis les images intermédiaires.
5. **Arc de mouvement** : traînée claire dessinée, effet séparé (3 à 4 images, sans contour), qui suggère la
   trajectoire sans que la pioche contourne le casque.
6. **Images dessinées** : pour les poses qui résistent à l'assemblage, remplacer la pièce par une image
   dédiée (torse et bras ensemble à l'impact, gant avec sa prise). Retouche Aseprite autorisée, annoncée
   dans le journal.
7. **Export de la feuille** avec tags (nom de l'animation) et durées (en images).

Contrôles (sur les masques de pixels visibles à la taille finale, masques par partie rendus avec la couleur ;
un échec = on corrige et on recommence ; on ne modifie jamais un contrôle ni une tolérance pour passer) :
- politique par paire de parties déclarée dans la fiche : interdit (pioche et casque, tolérance 1 à 2 px) ;
  contact requis (main et pioche, au moins 6 px de recouvrement) ; légal si passage derrière déclaré ;
  la visibilité d'un bras est déclarée image par image (ce n'est plus un seuil de pourcentage) ;
- prise gant-poignée à 1 px au plus ; pointe de la pioche à 1 px au plus de la cible sur l'image de contact ;
  0 pixel d'outil dans le hublot ; aucun trou transparent aux articulations ;
- confinement du mouvement : les pixels qui changent entre deux images restent dans la zone attendue ;
- zéro pixel isolé ; images toutes différentes ; palette respectée ; canevas 112 x 112 fixe ; pivots entiers ;
  hauteur 72 px au plus, outil compris ; tête d'acier d'au moins 12 px de large et 4 px de haut ;
  boucle fermée (première et dernière pose proches de l'ancre).

Contrôle visuel : pour chaque pose clé puis pour la séquence, regarde en ×4 et ×1, juge les 7 critères de la
règle de l'œil, plus « la silhouette seule raconte-t-elle le geste de la fiche ? ». Verdict garde ou annule,
écrit dans le journal. Quand la séquence est complète, un sous-agent relecteur indépendant reçoit la planche
de contrôle ; les défauts qu'il liste sont corrigés et il est relancé jusqu'à ce qu'il n'en reste aucun.

Si une pose te paraît impossible, ne dis jamais « impossible » sans rapport chiffré : quelle contrainte est
violée, de combien de pixels.

Fin de lot : planche finale à côté de l'ancre (×4 et ×1), tableau des contrôles (OK ou échec par image), liste
honnête des écarts restants et des exceptions dessinées, commit, ETAT.md. Puis le lot suivant avec la même
méthode.
