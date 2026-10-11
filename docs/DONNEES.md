# DONNEES.md — L'univers complet en JSON (phase M1)

Les données ne sont pas un squelette : c'est la conception de tout le jeu final. Elles doivent
permettre à quelqu'un qui n'a jamais vu le jeu d'en comprendre l'univers, la progression complète
du radeau au sous-marin géant, et les liens entre chaque élément. Tout est original.

`tools/gate.py M1` vérifie les minimums ci-dessous, les liens, l'absence de doublons et de textes
provisoires (TODO, lorem, « à compléter », « ... ») et **simule la progression** : en partant de
`depart.json`, chaque objet doit être obtenable, chaque biome atteignable, chaque quête faisable.
Les minimums sont des planchers, pas des cibles : vise plus riche.

Tous les `id` sont en minuscules sans accents ni espaces (`recif_corallien`). Les textes sont en français.

## data/lore.json
```json
{"civilisation": {"nom": "…", "description": "≥ 800 caractères", "chute": "≥ 300 caractères"},
 "signal": {"description": "≥ 300 caractères : ce qu'est le signal, d'où il vient, ce qu'il veut"},
 "chronologie": [{"epoque": "…", "evenement": "≥ 80 caractères"}],
 "factions": [{"id": "gardiens_cloche", "nom": "…", "description": "≥ 150 caractères"}],
 "glossaire": [{"terme": "…", "definition": "…"}]}
```
Minimums : 8 événements de chronologie, 3 factions, 10 termes de glossaire.

## data/biomes.json — `{"biomes": [...]}`, 8 minimum
```json
{"id": "recif_peu_profond", "nom": "…", "profondeur_min": 10, "profondeur_max": 120,
 "palier_requis": 0, "tranche": 1,
 "description": "≥ 200 caractères", "ambiance": "≥ 80 caractères (son, lumière, sensation)",
 "couleurs": ["#..", "#..", "#.."], "ressources": ["id_objet", "…"], "creatures": ["id_creature"],
 "points_interet": ["épave du …", "…"]}
```
`tranche` : 1 = surface + peu profond (échantillon), 2 = le biome sombre de l'échantillon,
0 = hors échantillon. Au moins 3 ressources et 2 points d'intérêt par biome. Une créature listée
ici doit aussi lister ce biome dans ses `biomes`. Au moins 2 notes cachées par biome.

## data/items.json — `{"items": [...]}`, 60 minimum
```json
{"id": "scaphandre_toile", "nom": "…", "categorie": "equipement", "palier": 0, "donne_palier": 1,
 "description": "≥ 60 caractères", "effets": {"oxygene_max": 60, "profondeur_max": 40},
 "obtention": [{"type": "recette", "ref": "r_scaphandre_toile"}]}
```
- `categorie` : materiau, minerai, outil, arme, equipement, consommable, construction, vehicule, relique, cle.
- `effets` obligatoire (non vide) pour outil, arme, equipement, consommable, vehicule, construction.
- `donne_palier` : sur les équipements qui ouvrent l'accès aux biomes de ce palier.
- `obtention` (au moins une) : `depart`, `biome` (ref = biome), `butin` (ref = créature ou boss),
  `recette` (ref = recette qui le produit), `quete` (ref = quête), `tresor` (ref = biome).
- Au moins 6 paliers différents ; au moins 3 véhicules dont le sous-marin géant au palier le plus haut.
- Chaque `materiau` et `minerai` sert dans au moins une recette ou un `objets_requis` de quête.

## data/stations.json — `{"stations": [...]}`, 4 minimum
```json
{"id": "etabli_radeau", "nom": "…", "description": "≥ 60 caractères", "debloque_par": null}
```
`debloque_par` : `null` (disponible au départ) ou l'`id` de l'objet `construction` qui la crée.

## data/recipes.json — `{"recipes": [...]}`, 45 minimum
```json
{"id": "r_scaphandre_toile", "resultat": "scaphandre_toile", "quantite": 1, "station": "etabli_radeau",
 "palier": 0, "ingredients": [{"item": "toile_voile", "qte": 3}, {"item": "corde", "qte": 2}]}
```
Ingrédients réels (au moins un), l'objet produit n'est pas son propre ingrédient.

## data/creatures.json — `{"creatures": [...]}`, 16 minimum
```json
{"id": "raie_lanterne", "nom": "…", "biomes": ["fosse_sombre"], "taille": "grande",
 "danger": "defensif", "comportement": "≥ 40 caractères", "silhouette": "≥ 20 caractères",
 "description": "≥ 100 caractères", "butin": ["id_objet"]}
```
`taille` : petite, moyenne, grande, colosse (dont un colosse `inoffensif` de fond).
`danger` : inoffensif, defensif, agressif. Silhouettes toutes différentes (pas de recoloration).

## data/bosses.json — `{"bosses": [...]}`, 3 minimum
```json
{"id": "gardien_cloche", "nom": "…", "biome": "…", "mini": true, "description": "≥ 200 caractères",
 "phases": [{"nom": "…", "description": "…"}, {"nom": "…", "description": "…"}], "butin": ["id_objet"]}
```
Au moins 2 phases chacun. Un `mini: true` dans un biome de la tranche (le mini-boss de l'échantillon).

## data/quests.json — `{"quests": [...]}`, 12 minimum
```json
{"id": "q_premiere_plongee", "nom": "…", "biome": "…", "description": "≥ 100 caractères",
 "objectifs": ["…"], "prerequis": ["id_quete"], "objets_requis": ["id_objet"],
 "recompenses": ["id_objet"], "notes_liees": ["id_note"]}
```
Pas de cycle de prérequis.

## data/notes.json — `{"notes": [...]}`, 24 minimum
```json
{"id": "n_journal_plongeur_1", "titre": "…", "biome": "…", "texte": "≥ 250 caractères",
 "sujets": ["civilisation", "signal", "chronologie", "id_faction"], "indice_fin": "id_fin ou null"}
```

## data/endings.json — `{"endings": [...]}`, 3 minimum
```json
{"id": "fin_silence", "nom": "…", "condition": "≥ 80 caractères", "description": "≥ 250 caractères",
 "notes_requises": ["id_note", "id_note"], "quete_finale": "id_quete"}
```

## data/depart.json
```json
{"palier": 0, "inventaire": [{"item": "id_objet", "qte": 1}]}
```

## Au-delà du contrôle (ce que l'audit regardera)

- Un univers cohérent : les noms, matières, créatures et notes racontent la même histoire.
- Une progression qui donne envie : chaque palier ouvre un biome nouveau, une mécanique, une révélation.
- Les liens se lisent dans les deux sens : un objet rare a une histoire, une note éclaire une fin.
