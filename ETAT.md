# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M0

## Dernier contrôle
2026-10-11 08:50:17 M0 SUCCES erreurs=0 gate_sha256=55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb

## En cours
M0 terminé, en attente de validation visuelle (Julien regarde les planches avant la suite). Rien d'autre n'est lancé.

## Défauts visuels connus
Etat après 23 entrées au journal (voir art/journal/plongeur.json) :
- Casque : cadre et boulons NON lisibles à 37 px (4 tentatives annulées, entrées 15 à 18). Hypothèses testées : tube 0,6 px (trop fin) ; cadre en avant du verre ; tube 2 px ; métal sombre. Le cadre est présent dans le rendu brut (vu de profil, c'est une barre fine), il disparaît à la pixelisation.
- Tuyau d'air : absent. Sangles : absentes. Bouteilles : une simple barre.
- Palmes : minces. Pieds : peu lisibles.
- Bras de nage : peu visibles, cachés derrière le torse.
- Hublot : reflet 2 pixels (itération Aseprite à refaire sur le nouveau rendu).

## Blocage en cours
Cadre du hublot illisible à 37 px : 4 hypothèses testées et annulées (entrées 15 à 18). Prochaine hypothèse : hublot plus clair (verre) avec bord sombre, plutôt qu'un cadre métallique.

## Tailles et amplitudes (mesurées par tools/mesure/mesurer.py)
- Avant M0 (entrée 1) : nage 44-45 px, idle 43-44 px, amplitude nage 0,402, idle 0,236.
- Actuel : nage 36-39 px, idle 37 px, amplitude nage 0,532 (cible >= 0,45 : OK), idle 0,223 (cible >= 0,10 : OK).

Clone neuf : `python tools/gate.py M0` donne ECHEC (Godot : « Failed loading resource ... .godot/imported/plongeur.png-....ctex »).
- H1 (confirmée par le message « Make sure resources have been imported ») : `.godot/` est ignoré par git, donc le cache d'import n'existe pas dans un clone.
- H2 (à tester) : le `.import` versionné ne sert à rien sans son cache. Test : les `.import` sont-ils nécessaires ?
- Solution retenue : `scripts/m0_plongeur.gd` charge le PNG avec `Image.load_from_file` (pas de `load()`), donc aucun cache n'est nécessaire.

Historique des blocages résolus pendant M0 (une ligne par hypothèse) :
- Plongeur qui reste debout en nage : les os Blender tournent autour de leur axe Y (longueur de l'os). Flexion sur l'axe Z local : résolu.
- Hublot invisible : il était enfoncé dans le casque. Déplacé puis agrandi : résolu.
- Godot « No loader found » sur le sprite : les dossiers art/, boards/, tools/ étaient importés et l'import ne finissait pas. `.gdignore` dans ces dossiers : résolu.
- Capture Godot uniforme (95 % d'une couleur) : fond d'eau en aplat. Dégradé de palette en shader : résolu.

## Besoin de Julien
- M0 terminé, en attente de validation visuelle : regarder `boards/plongeur_modifie.png`, `boards/iterations/`, `boards/plongeur_reference.png` et `shots/m0_plongeur_godot.png`. Dire « M0 validé, passe à M1 » pour continuer.
- Références : une seule référence libre est dans `art/references/` (`ref_03_plongeur_stockholm_1951.jpg`). Wikimedia répond 429 aux deux autres, elles sont notées dans `art/references/SOURCES.md` comme non obtenues. AGENTS.md en demande 2 ou 3 : à compléter quand la limite de débit sera levée, ou si Julien en fournit.
- Choix à valider : une image de référence est téléchargée pour s'inspirer (BRIEF §5 autorise les références, la consigne « rien de visuel ne se télécharge » vise les assets). Dire si Julien veut retirer cette exception.

## Prochaine étape
Attendre la validation visuelle de Julien. Après « M0 validé » : M1 (l'univers complet en données, `docs/DONNEES.md`).
