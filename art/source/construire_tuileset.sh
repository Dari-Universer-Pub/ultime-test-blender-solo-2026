#!/bin/bash
# construire_tuileset.sh <biome> <rampe> : tuileset autotile 47 cases (rendu 128 px -> 16 px, palette).
#   art/rendu/tuileset/<biome>/tuile_01..47.png -> art/pixel/tuileset_<biome>/ (rampes du biome)
#   -> feuille horizontale 47 cases (assets/sprites/tuileset_<biome>/) + planche de contrôle.
# Lancement depuis la racine : bash art/source/construire_tuileset.sh radeau_surface ocre
set -e
BIOME="$1"
RAMPE="$2"
ID="tuileset_$BIOME"
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RACINE"
ASEPRITE=/opt/outils-varekh/bin/aseprite
rm -rf "art/pixel/$ID" && mkdir -p "art/pixel/$ID"
python3 tools/pixelisation/pixeliser.py "art/rendu/tuileset/$BIOME" "art/pixel/$ID" --rampes "$RAMPE" > /dev/null
FICHIERS=$(for k in $(seq -w 1 47); do printf "tile_%s.png," "$k"; done | sed 's/,$//')
mkdir -p "assets/sprites/$ID"
rm -f "assets/sprites/$ID/$ID.png" "assets/sprites/$ID/$ID.json" "art/source/aseprite/$ID.aseprite"
timeout 300 "$ASEPRITE" --batch --script-param entree="$RACINE/art/pixel/$ID" --script-param fichiers="$FICHIERS" \
  --script-param etiquettes="" --script-param sortie="$RACINE/art/source/aseprite/$ID.aseprite" \
  --script-param feuille="$RACINE/assets/sprites/$ID/$ID.png" --script-param donnees="$RACINE/assets/sprites/$ID/$ID.json" \
  --script art/source/aseprite/construire_lot.lua 2>&1 | tail -n 1
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_modifie.png" --ligne "$ID 47 cases, pixel 16 px" $(for k in $(seq -w 1 12); do echo "art/pixel/$ID/tile_$k.png"; done) > /dev/null
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_base.png" --ligne "$ID rendu brut 128 px" $(for k in $(seq -w 1 12); do echo "art/rendu/tuileset/$BIOME/tile_$k.png"; done) > /dev/null
echo "CHAINE_OK $ID"
