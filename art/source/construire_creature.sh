#!/bin/bash
# construire_creature.sh <id> : chaîne complète d'une créature vivante (M3).
#   1. Blender : rendu des images (nage, attaque, mort) -> art/rendu/<id>/
#   2. pixelisation -> art/pixel/<id>/ (64 px, palette)
#   3. feuille Aseprite à 3 étiquettes -> art/source/aseprite/<id>.aseprite
#   4. itérations Aseprite 2 à 4 (retouches de art/source/aseprite/retouches_<id>.lua), feuille exportée à chaque
#   5. planches d'itération -> boards/iterations/<id>_it{2,3,4}.png
# Les retouches sont des recolorations limitées à une zone : voir finition_creature.lua.
set -e
ID="$1"
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RACINE"
BLENDER=/opt/outils-varekh/bin/blender
ASEPRITE=/opt/outils-varekh/bin/aseprite
RETOUCHES="$RACINE/art/source/aseprite/retouches_$ID.lua"
S="${TMPDIR:-/tmp}/construire_creature_$ID"
rm -rf "art/rendu/$ID" "art/pixel/$ID" && mkdir -p "art/rendu/$ID" "$S"
timeout 2400 "$BLENDER" -b --factory-startup --python "art/source/blender/$ID.py" > "$S/blender.log" 2>&1
test "$(ls art/rendu/$ID/*.png | wc -l)" = "18" || { echo "RENDU INCOMPLET $ID"; exit 1; }
python3 tools/pixelisation/pixeliser.py "art/rendu/$ID" "art/pixel/$ID" > /dev/null
FICHIERS=$(for f in nage_01 nage_02 nage_03 nage_04 nage_05 nage_06 nage_07 nage_08 attaque_01 attaque_02 attaque_03 attaque_04 mort_01 mort_02 mort_03 mort_04 mort_05 mort_06; do printf "%s.png," $f; done | sed 's/,$//')
mkdir -p "assets/sprites/$ID" boards/iterations
rm -f "assets/sprites/$ID/$ID.png" "assets/sprites/$ID/$ID.json" "art/source/aseprite/$ID.aseprite"
timeout 300 "$ASEPRITE" --batch --script-param entree="$RACINE/art/pixel/$ID" --script-param fichiers="$FICHIERS" \
  --script-param etiquettes=nage:1:8,attaque:9:12,mort:13:18 --script-param sortie="$RACINE/art/source/aseprite/$ID.aseprite" \
  --script-param feuille="$RACINE/assets/sprites/$ID/$ID.png" --script-param donnees="$RACINE/assets/sprites/$ID/$ID.json" \
  --script art/source/aseprite/construire_lot.lua > "$S/lot.log" 2>&1
for n in 2 3 4; do
  rm -rf "$S/it$n" && mkdir -p "$S/it$n"
  timeout 300 "$ASEPRITE" --batch --script-param sortie="$RACINE/art/source/aseprite/$ID.aseprite" \
    --script-param feuille="$RACINE/assets/sprites/$ID/$ID.png" --script-param donnees="$RACINE/assets/sprites/$ID/$ID.json" \
    --script-param iteration=$n --script-param retouches="$RETOUCHES" --script-param images="$S/it$n" \
    --script art/source/aseprite/finition_creature.lua > "$S/it$n.log" 2>&1
  grep -q FINITION_CREATURE_OK "$S/it$n.log" || { echo "FINITION ECHEC $ID it$n"; exit 1; }
  python3 tools/planches/planche_etats.py --sortie "boards/iterations/${ID}_it$n.png" \
    --ligne "$ID it$n nage 1-8" $(for i in 01 02 03 04 05 06 07 08; do echo "$S/it$n/nage_$i.png"; done) \
    --ligne "$ID it$n attaque 1-4" $(for i in 01 02 03 04; do echo "$S/it$n/attaque_$i.png"; done) \
    --ligne "$ID it$n mort 1-6" $(for i in 01 02 03 04 05 06; do echo "$S/it$n/mort_$i.png"; done) > /dev/null
done
echo "CREATURE_OK $ID"
