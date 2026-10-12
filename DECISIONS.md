# DECISIONS.md — Décisions de Julien et du projet (journal des choix)

Chaque décision porte sa date. Les décisions anciennes sont remplacées ici, pas effacées dans l'historique git.

## 12/10 — Style du héros (ancre verrouillée)
- Héros de **70 à 74 px** de haut, case **112 × 112**, trois quarts de face (azimut 35°, élévation 15°).
- Style **peint doux, SANS contour** (ni trait sombre, ni contour interne). La forme tient à la valeur et à l'ombrage.
- Rendu **direct à la taille finale**, quantification **par matière**, **une seule lumière en haut à gauche**.
- Ancre validée : `art/references/ancre_plongeur_v6.png` (sprite), rendus x6 `ancre_plongeur_v6_x6_eau_claire.png`
  et `ancre_plongeur_v6_x6_eau_sombre.png`. Pose idle validée par Julien (commit `add270b`).
- Remplace : « plongeur 32 à 40 px », « contour sélectif 1 px », case 64 px, palette `art/palette.json` (M0).

## Avant le 12/10 (rappel, remplacé en partie)
- Méthode « Dead Cells » adoptée : rendu direct, paliers de lumière, détails peints par attribut (v5).
- Contour indigo 1 px : retiré le 12/10 (demande de Julien : « lourd et affreux »). Historique : commit `cb8d19f`.
- Le gate (`tools/gate.py`, `tools/outils.json`) n'est jamais modifié par l'agent. `HAUTEUR_PLONGEUR = (56, 80)`
  est voulu par Julien.
