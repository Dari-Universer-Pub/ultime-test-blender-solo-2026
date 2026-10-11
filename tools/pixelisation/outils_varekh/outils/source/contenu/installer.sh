#!/usr/bin/env bash
# Installe les outils sur place (quelques secondes) : fixe le chargeur glibc embarque dans
# chaque programme. A relancer si le dossier est deplace. Aucun acces reseau, aucun apt.
set -e
D="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
LD="$D/runtime/lib/ld-linux-x86-64.so.2"
[ "$(uname -m)" = "x86_64" ] || { echo "Ces outils sont pour Linux x86_64 (machine : $(uname -m))"; exit 1; }
PE=("$LD" --library-path "$D/runtime/lib" "$D/runtime/bin/patchelf")
EXES=(
  runtime/bin/Xvfb runtime/bin/xkbcomp runtime/bin/xdpyinfo runtime/bin/xwd
  runtime/bin/glxinfo runtime/bin/eglinfo
  godot/godot aseprite/aseprite
  blender/blender blender/blender-thumbnailer blender/5.2/python/bin/python3.13
)
for e in "${EXES[@]}"; do
  [ -f "$D/$e" ] || continue
  "${PE[@]}" --set-interpreter "$LD" "$D/$e"
done
chmod +x "$D"/bin/* "$D"/installer.sh "$D"/verifier.sh 2>/dev/null || true
echo "$D" > "$D/.installe"

# Modeles d'export Godot (Windows x86_64) la ou Godot les cherche
TPL="${XDG_DATA_HOME:-$HOME/.local/share}/godot/export_templates"
mkdir -p "$TPL" && rm -rf "$TPL/4.4.1.stable" && ln -s "$D/godot/export_templates/4.4.1.stable" "$TPL/4.4.1.stable"

# Raccourcis dans le PATH si possible (sinon utiliser les chemins complets)
for t in godot blender aseprite capture-ecran godot-capture xvfb-demarrer; do
  ln -sf "$D/bin/$t" "/usr/local/bin/$t" 2>/dev/null || \
  { command -v sudo >/dev/null && sudo -n ln -sf "$D/bin/$t" "/usr/local/bin/$t" 2>/dev/null; } || true
done

cat <<FIN
Outils installes dans $D
  Godot     : $D/bin/godot
  Blender   : $D/bin/blender
  Aseprite  : $D/bin/aseprite
  Captures  : $D/bin/capture-ecran  et  $D/bin/godot-capture
tools/outils.json pour ce dossier :
{
  "_note": "Outils Linux portables (outils-varekh). Ne pas modifier, sauf ajouter la cle 'robot' en phase M2.",
  "godot": ["$D/bin/godot"],
  "blender": ["$D/bin/blender"],
  "aseprite": ["$D/bin/aseprite"]
}
Verification complete : bash $D/verifier.sh
FIN
