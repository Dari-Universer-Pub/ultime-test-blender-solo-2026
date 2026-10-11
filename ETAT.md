# ETAT.md — Où en est le projet (tenu à jour par l'agent à chaque étape importante)

## Phase courante
M0

## Dernier contrôle
2026-10-11 08:50:17 M0 SUCCES erreurs=0 gate_sha256=55d6fbef1065ba7afcaf4f11922e1f57d6f56ed22d0fea591e7ed6b4a6c8beeb

## En cours
M0 terminé, en attente de validation visuelle (Julien regarde les planches avant la suite). Rien d'autre n'est lancé.

## Défauts visuels connus
- Bras en idle : la pose part vers l'arrière, pas vers l'avant (journal, entrée 7).
- Reflet du hublot : 2 pixels sur les images idle, 1 pixel sur les images nage (journal, entrée 9).
- Palmes minces et pieds peu détaillés (journal, entrée 10).
- Silhouette de nage : bras et palmes à retravailler, lisibilité à ×1 correcte mais perfectible.

## Blocage en cours
(aucun) — voir la section « Besoin de Julien » pour les références.

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
