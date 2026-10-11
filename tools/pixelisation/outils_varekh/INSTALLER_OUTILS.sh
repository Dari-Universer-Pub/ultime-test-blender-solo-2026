#!/usr/bin/env bash
# Installe Godot 4.4.1 + Blender 5.2.1 + Aseprite 1.3.18.6 deja compiles (Linux x86_64),
# sans reseau, sans apt, sans compilation. Environ 1 minute.
#   bash INSTALLER_OUTILS.sh               -> /opt/outils-varekh (ou ~/outils-varekh si /opt est interdit)
#   bash INSTALLER_OUTILS.sh /autre/dossier
set -e
ICI="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
if [ -f "$ICI/outils/outils-varekh.tar.xz" ]; then PARTIES=("$ICI/outils/outils-varekh.tar.xz")
else PARTIES=("$ICI"/outils/outils-varekh.tar.xz.partie-*); fi
[ -f "${PARTIES[0]}" ] || { echo "Archive des outils introuvable dans $ICI/outils/"; exit 1; }

DEST="${1:-}"
if [ -z "$DEST" ]; then
  if mkdir -p /opt/outils-varekh 2>/dev/null && [ -w /opt/outils-varekh ]; then DEST=/opt/outils-varekh
  elif command -v sudo >/dev/null && sudo -n mkdir -p /opt/outils-varekh 2>/dev/null \
       && sudo -n chown "$(id -u):$(id -g)" /opt/outils-varekh; then DEST=/opt/outils-varekh
  else DEST="$HOME/outils-varekh"; fi
fi
mkdir -p "$DEST"

if [ -x "$DEST/installer.sh" ] && [ "$(cat "$DEST/.version" 2>/dev/null)" = "$(cat "$ICI/outils/VERSION")" ]; then
  echo "Deja decompresse dans $DEST"
else
  echo "Verification de l'archive..."
  if command -v sha256sum >/dev/null; then
    ( cd "$ICI/outils" && sha256sum -c --quiet SHA256SUMS ) || { echo "Archive abimee (SHA256)"; exit 1; }
  fi
  echo "Decompression dans $DEST ..."
  if command -v xz >/dev/null; then
    cat "${PARTIES[@]}" | xz -dc -T0 | tar -x -C "$DEST" --strip-components=1
  elif command -v python3 >/dev/null; then
    cat "${PARTIES[@]}" | python3 -c "import sys,tarfile,lzma
t=tarfile.open(fileobj=lzma.LZMAFile(sys.stdin.buffer),mode='r|')
for m in t:
    m.name=m.name.split('/',1)[1] if '/' in m.name else '.'
    if m.islnk(): m.linkname=m.linkname.split('/',1)[1]
    t.extract(m,sys.argv[1])" "$DEST"
  else
    X="$ICI/outils/xz"   # xz embarque (avec sa glibc) si la machine n'a ni xz ni python3
    cat "${PARTIES[@]}" | "$X/ld-linux-x86-64.so.2" --library-path "$X" "$X/xz" -dc -T0 \
      | tar -x -C "$DEST" --strip-components=1
  fi
  cp "$ICI/outils/VERSION" "$DEST/.version"
fi
# Usine a assets (si presente a cote) : commande "usine"
if [ -f "$ICI/usine/usine.sh" ]; then
  chmod +x "$ICI/usine/usine.sh"
  ln -sf "$ICI/usine/usine.sh" /usr/local/bin/usine 2>/dev/null || \
  { command -v sudo >/dev/null && sudo -n ln -sf "$ICI/usine/usine.sh" /usr/local/bin/usine 2>/dev/null; } || \
  { mkdir -p "$HOME/.local/bin" && ln -sf "$ICI/usine/usine.sh" "$HOME/.local/bin/usine" && echo "usine : ajoute $HOME/.local/bin au PATH"; }
  echo "Usine a assets : commande 'usine' (mode d'emploi : $ICI/usine/LISEZMOI.md)"
fi
if [ "$(cat "$DEST/.installe" 2>/dev/null)" = "$DEST" ]; then
  echo "Outils deja installes dans $DEST (rien a refaire). Verification : bash $DEST/verifier.sh"
else
  bash "$DEST/installer.sh"
fi
