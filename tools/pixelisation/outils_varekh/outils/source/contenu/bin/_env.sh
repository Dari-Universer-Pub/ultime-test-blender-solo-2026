# Environnement commun (source par les lanceurs). Ne pas lancer directement.
D="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
R="$D/runtime"
if [ "$(cat "$D/.installe" 2>/dev/null)" != "$D" ]; then
  echo "outils-varekh : lance d'abord  bash $D/installer.sh  (dossier deplace ou pas encore installe)" >&2
  exit 3
fi
export LIBGL_DRIVERS_PATH="$R/lib/dri"
export GBM_BACKENDS_PATH="$R/lib/gbm"
export __EGL_VENDOR_LIBRARY_DIRS="$R/share/glvnd/egl_vendor.d"
export __GLX_VENDOR_LIBRARY_NAME=mesa
export VK_DRIVER_FILES="$R/share/vulkan/icd.d/lvp_icd.json"
export VK_ICD_FILENAMES="$VK_DRIVER_FILES"
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export FONTCONFIG_FILE="$R/etc/fonts/fonts.conf"
export XKB_CONFIG_ROOT="$R/share/X11/xkb"
export XLOCALEDIR="$R/share/X11/locale"
export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"

# Ecran virtuel : Xvfb (:99, sinon :100...) si aucun ecran utilisable n'est fourni.
ecran_ok() { "$R/bin/xdpyinfo" -display "$1" >/dev/null 2>&1; }
assurer_ecran() {
  if [ -n "${DISPLAY:-}" ] && ecran_ok "$DISPLAY"; then return 0; fi
  mkdir -p /tmp/.X11-unix 2>/dev/null; chmod 1777 /tmp/.X11-unix 2>/dev/null
  local u; u="$(id -u)"
  local n
  n="$( (
    flock -w 60 9
    for n in 99 100 101 102 103 104 105 106 107 108 109; do
      if ecran_ok ":$n"; then echo "$n"; exit 0; fi
      rm -f "/tmp/.X11-unix/X$n" "/tmp/.X$n-lock" 2>/dev/null
      [ -e "/tmp/.X11-unix/X$n" ] || [ -e "/tmp/.X$n-lock" ] && continue
      ( cd "$R/bin" && exec nohup ./Xvfb ":$n" -screen 0 "${VAREKH_ECRAN:-1920x1080x24}" -nolisten tcp \
          -xkbdir "$R/share/X11/xkb" +extension GLX +render -noreset ) >"/tmp/outils-varekh-xvfb-$u.log" 2>&1 9>&- &
      for _ in $(seq 1 100); do ecran_ok ":$n" && { echo "$n"; exit 0; }; sleep 0.1; done
    done
  ) 9>"/tmp/outils-varekh-$u.lock" )"
  if [ -n "$n" ]; then export DISPLAY=":$n"; return 0; fi
  echo "outils-varekh : impossible de demarrer l'ecran virtuel, voir /tmp/outils-varekh-xvfb-$u.log" >&2
  return 1
}
