#!/bin/bash
# pixel_px.sh NOM (variable R = dossier de travail) : rendu 448 px, carte d'identité (matière + groupes), pixelisation par matière x4, mesures
set -e
R=${R:?dossier de travail}
cd "$(dirname "$0")/../.."
N=$1
rm -rf "$R/$N"; mkdir -p "$R/$N"
PLONGEUR_SORTIE="$R/$N/rendu" PLONGEUR_ECHANTILLONS=64 timeout 500 /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v4_px.py > "$R/$N/rendu.log" 2>&1
grep -q Traceback "$R/$N/rendu.log" && { echo "TB rendu"; grep -A8 Traceback "$R/$N/rendu.log"; exit 1; }
PLONGEUR_SORTIE="$R/$N/id" PLONGEUR_IDENTITE=1 PLONGEUR_ECHANTILLONS=16 timeout 500 /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v4_px.py > "$R/$N/id.log" 2>&1
grep -q Traceback "$R/$N/id.log" && { echo "TB identite"; grep -A8 Traceback "$R/$N/id.log"; exit 1; }
python3 tools/pixelisation/pixeliser_matiere.py "$R/$N/rendu/px_base.png" "$R/$N/id" "$R/$N/pixel.png" --palette art/palette_plongeur_px_matiere.json --facteur 4
python3 tools/mesure/membres.py "$R/$N/id" --facteur 4 --groupe idle --cote-proche d --images 1 || true
python3 tools/planches/pixel_quatre.py "$R/$N/rendu/px_base.png" "$R/$N/pixel.png" "$R/$N/planche.png" > /dev/null
