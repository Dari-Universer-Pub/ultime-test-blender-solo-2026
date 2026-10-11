#!/bin/bash
# construire_fond.sh <id> : chaîne d'un fond (paysage 16:9), un seul cadre.
#   rendu Blender 640 x 360 -> pixelisation facteur 2 (320 x 180, palette) -> feuille -> planches.
# Lancement depuis la racine : bash art/source/construire_fond.sh fond_vagues_radeau
set -e
ID="$1"
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RACINE"
BLENDER=/opt/outils-varekh/bin/blender
ASEPRITE=/opt/outils-varekh/bin/aseprite
rm -f "art/rendu/$ID/$ID.png" "art/pixel/$ID/$ID.png"
timeout 900 "$BLENDER" -b --factory-startup --python "art/source/blender/$ID.py" > "/tmp/fond_$ID.log" 2>&1
test -f "art/rendu/$ID/$ID.png" || { echo "RENDU ABSENT $ID"; tail -n 5 "/tmp/fond_$ID.log"; exit 1; }
python3 tools/pixelisation/pixeliser.py "art/rendu/$ID" "art/pixel/$ID" --facteur 2 > /dev/null
mkdir -p "assets/sprites/$ID" boards/props
rm -f "assets/sprites/$ID/$ID.png" "assets/sprites/$ID/$ID.json" "art/source/aseprite/$ID.aseprite"
timeout 300 "$ASEPRITE" --batch --script-param entree="$RACINE/art/pixel/$ID" --script-param fichiers="$ID.png" \
  --script-param etiquettes="" --script-param sortie="$RACINE/art/source/aseprite/$ID.aseprite" \
  --script-param feuille="$RACINE/assets/sprites/$ID/$ID.png" --script-param donnees="$RACINE/assets/sprites/$ID/$ID.json" \
  --script art/source/aseprite/construire_lot.lua 2>&1 | tail -n 1
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_base.png" --ligne "$ID rendu brut 640 x 360" "art/rendu/$ID/$ID.png" > /dev/null
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_modifie.png" --ligne "$ID pixel 320 x 180" "art/pixel/$ID/$ID.png" > /dev/null
echo "CHAINE_OK $ID"
