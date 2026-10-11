#!/usr/bin/env bash
# Verifie que chaque outil marche VRAIMENT : versions, rendu Blender, capture Godot,
# Movie Maker Godot, script Aseprite, capture d'ecran. Images de preuve dans le dossier de sortie.
D="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
O="${1:-/tmp/outils-varekh-verif}"; rm -rf "$O"; mkdir -p "$O/export_windows"
B="$D/bin"; V="$O/verif"; cp -r "$D/verif" "$V"; ok=0; ko=0
res() { if [ "$1" = 0 ]; then echo "  OK    $2"; ok=$((ok+1)); else echo "  ECHEC $2 (voir $O/$3)"; ko=$((ko+1)); fi; }
png() { [ -s "$1" ] && head -c 8 "$1" | grep -q PNG; }
echo "== outils-varekh : verification ($D)"
"$B/godot" --headless --version >"$O/godot_version.log" 2>&1; res $? "Godot $(head -1 "$O/godot_version.log")" godot_version.log
"$B/blender" --version >"$O/blender_version.log" 2>&1; res $? "$(head -1 "$O/blender_version.log")" blender_version.log
"$B/aseprite" --batch --version >"$O/aseprite_version.log" 2>&1; res $? "$(head -1 "$O/aseprite_version.log")" aseprite_version.log
for m in BLENDER_WORKBENCH BLENDER_EEVEE; do
  "$B/blender" -b --factory-startup --python "$V/rendu_blender.py" -- "$O/blender_$m.png" "$m" >"$O/blender_$m.log" 2>&1
  grep -q RENDU_OK "$O/blender_$m.log" && png "$O/blender_$m.png"; res $? "Blender rendu $m -> $O/blender_$m.png" "blender_$m.log"
done
"$B/blender" -b --factory-startup --python-expr "import bpy;bpy.ops.mesh.primitive_monkey_add();bpy.ops.wm.save_as_mainfile(filepath='$O/test.blend');bpy.ops.export_scene.gltf(filepath='$O/test.glb');print('GLB_OK')" >"$O/blender_glb.log" 2>&1
grep -q GLB_OK "$O/blender_glb.log" && [ -s "$O/test.glb" ]; res $? "Blender .blend + export GLB" blender_glb.log
VERIF_SORTIE="$O/godot_capture.png" "$B/godot" --path "$V/godot" --audio-driver Dummy >"$O/godot_capture.log" 2>&1
grep -q "CAPTURE_GODOT 0" "$O/godot_capture.log" && png "$O/godot_capture.png"; res $? "Godot capture viewport (get_texture().get_image()) -> $O/godot_capture.png" godot_capture.log
"$B/godot" --headless --path "$V/godot" --quit >"$O/godot_headless.log" 2>&1; res $? "Godot --headless --quit" godot_headless.log
"$B/godot" --headless --path "$V/godot" --export-release "Windows Desktop" "$O/export_windows/verif.exe" >"$O/godot_export.log" 2>&1
[ -s "$O/export_windows/verif.exe" ]; res $? "Godot export Windows (.exe) -> $O/export_windows/verif.exe" godot_export.log
VERIF_SORTIE=/dev/null "$B/godot-capture" "$V/godot" "$O/film" 8 >"$O/godot_film.log" 2>&1
png "$O/film/image00000005.png"; res $? "Godot Movie Maker -> $O/film/image0000000*.png" godot_film.log
"$B/aseprite" --batch --script-param out="$O" --script "$V/sprite.lua" >"$O/aseprite_script.log" 2>&1
grep -q ASEPRITE_OK "$O/aseprite_script.log" && png "$O/sprite_planche.png" && [ -s "$O/sprite.aseprite" ]; res $? "Aseprite script Lua + .aseprite + planche -> $O/sprite_planche.png" aseprite_script.log
"$B/aseprite" --batch "$O/sprite.aseprite" --scale 8 --save-as "$O/sprite_x8_{frame}.png" >"$O/aseprite_cli.log" 2>&1
png "$O/sprite_x8_1.png"; res $? "Aseprite ligne de commande (--scale 8 --save-as)" aseprite_cli.log
VERIF_ATTENTE=1 "$B/godot" --path "$V/godot" --audio-driver Dummy >"$O/godot_fenetre.log" 2>&1 & gp=$!
sleep 3; "$B/capture-ecran" "$O/ecran.png" >"$O/capture_ecran.log" 2>&1; c=$?; wait $gp
[ $c = 0 ] && png "$O/ecran.png"; res $? "capture-ecran (ecran virtuel :99, fenetre Godot ouverte) -> $O/ecran.png" capture_ecran.log
echo "== $ok OK, $ko ECHEC"
[ "$ko" = 0 ] && echo "SUCCES : tout marche. Regarde les images dans $O" || echo "ECHEC : lis les .log indiques"
[ "$ko" = 0 ]
