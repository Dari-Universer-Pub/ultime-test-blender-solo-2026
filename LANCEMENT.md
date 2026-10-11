# LANCEMENT.md — pour Julien (l'agent n'a pas besoin de ce fichier)

## 1. Installer (sandbox Linux, ex. arena.ai)
Décompresse ce dossier dans un dossier VIDE. Les outils (Godot, Blender, Aseprite) sont déjà compilés (dossier `outils/` du
dépôt kit-outil-v2) : à chaque nouvelle sandbox, `bash INSTALLER_OUTILS.sh` (1 minute) puis
`bash /opt/outils-varekh/verifier.sh` (doit afficher SUCCES). Il faut Pillow pour l'outil de comparaison :
`python3 -m pip install pillow`. Ne touche à rien d'autre. Lance ton agent dans ce dossier.

## 2. Premier message à l'agent (à coller tel quel)
```
Tu construis le jeu LES CLOCHES DE VAREKH dans ce dossier, et uniquement dans ce dossier.
Les outils sont déjà compilés : ne compile RIEN. Si /opt/outils-varekh/bin/godot n'existe pas, lance « bash <dossier du dépôt kit-outil-v2 (dossier outils/)>/INSTALLER_OUTILS.sh » puis « bash /opt/outils-varekh/verifier.sh », qui doit afficher SUCCES.
Avant toute chose, lis en entier, dans cet ordre : AGENTS.md, PLAN.md, ETAT.md, docs/BRIEF.md, docs/DONNEES.md, Pour les assets, aucun outil n'est fourni et rien ne se télécharge : tu construis tout toi-même dans Blender, par tes propres scripts, puis tu pixelises et tu finis dans Aseprite.
La règle la plus importante est la règle de l'œil (AGENTS.md) : un seul changement visuel à la fois, puis tu fabriques la planche avant/après, tu la REGARDES, tu juges les 7 critères et tu notes dans le journal visuel. Jamais deux changements sans regarder entre les deux.
Ce n'est pas un prototype : c'est le premier jet du jeu final, au niveau professionnel.
Tu suis la boucle de AGENTS.md : tu travailles uniquement sur la phase écrite dans ETAT.md, tu lances
« python3 tools/gate.py <phase> », et tu ne fais rien
d'autre tant qu'il n'affiche pas SUCCES. Aucune limite d'essais. Tu ne modifies jamais tools/gate.py.
Quand une phase est en SUCCES, tu commits, tu mets ETAT.md à jour et tu enchaînes la suivante, sauf
une phase marquée ARRÊT POUR VALIDATION. Commence par M0.
```

## 3. Si la session s'arrête ou que l'agent perd le fil
```
Relis AGENTS.md puis ETAT.md, et reprends exactement où tu en étais.
Si la sandbox a été réinitialisée (/opt/outils-varekh/bin/godot absent), fais d'abord l'étape 0 d'AGENTS.md :
réinstalle les outils déjà compilés avec INSTALLER_OUTILS.sh (1 minute), puis verifier.sh. Ne recompile rien. Phase courante : celle d'ETAT.md.
Lance d'abord « python tools/gate.py <phase> » pour voir ce qui reste à corriger.
```

## 4. Ce que tu fais, toi
- À la fin de M0, l'agent s'arrête : regarde (ou envoie-moi) `boards/plongeur_base.png`,
  `boards/plongeur_modifie.png`, `boards/iterations/` et `shots/m0_plongeur_godot.png`.
  Si le style te va, dis-lui : « M0 validé, passe à M1. »
- Quand tu veux un audit : dis-le-moi, je lis le dossier, je relance le contrôle et je vérifie
  que `tools/gate.py` n'a pas été modifié (son empreinte est dans `tests/gate_<phase>.txt`).
