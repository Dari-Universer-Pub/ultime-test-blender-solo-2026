#!/bin/bash
# construire_prop.sh <id> : chaîne complète d'un prop construit (un seul cadre, 64 px).
#   1. Blender : art/source/blender/<id>.py -> art/rendu/<id>/<id>.png (512 px) et <id>.blend
#   2. pixelisation -> art/pixel/<id>/<id>.png (64 px, palette)
#   3. feuille Aseprite -> art/source/aseprite/<id>.aseprite, assets/sprites/<id>/<id>.{png,json}
#   4. planches de contrôle -> boards/props/<id>_base.png (rendu) et <id>_modifie.png (pixel)
# Lancement depuis la racine du dépôt : bash art/source/construire_prop.sh bidon_rouille
set -e
ID="$1"
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RACINE"
BLENDER=/opt/outils-varekh/bin/blender
ASEPRITE=/opt/outils-varekh/bin/aseprite
rm -f "art/rendu/$ID/$ID.png" "art/pixel/$ID/$ID.png"
timeout 900 "$BLENDER" -b --factory-startup --python "art/source/blender/$ID.py" > "/tmp/prop_$ID.log" 2>&1
test -f "art/rendu/$ID/$ID.png" || { echo "RENDU ABSENT $ID"; tail -n 5 "/tmp/prop_$ID.log"; exit 1; }
python3 tools/pixelisation/pixeliser.py "art/rendu/$ID" "art/pixel/$ID" > /dev/null
mkdir -p "assets/sprites/$ID" boards/props
rm -f "assets/sprites/$ID/$ID.png" "assets/sprites/$ID/$ID.json" "art/source/aseprite/$ID.aseprite"
timeout 300 "$ASEPRITE" --batch --script-param entree="$RACINE/art/pixel/$ID" --script-param fichiers="$ID.png" \
  --script-param etiquettes="" --script-param sortie="$RACINE/art/source/aseprite/$ID.aseprite" \
  --script-param feuille="$RACINE/assets/sprites/$ID/$ID.png" --script-param donnees="$RACINE/assets/sprites/$ID/$ID.json" \
  --script art/source/aseprite/construire_lot.lua 2>&1 | tail -n 1
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_base.png" --ligne "$ID rendu brut 512 px" "art/rendu/$ID/$ID.png" > /dev/null
python3 tools/planches/planche_etats.py --sortie "boards/props/${ID}_modifie.png" --ligne "$ID pixel 64 px" "art/pixel/$ID/$ID.png" > /dev/null
echo "CHAINE_OK $ID"
