# Comment le paquet outils-varekh a été fabriqué (pour le refaire un jour)

Machine : Ubuntu 24.04 x86_64.
1. Godot 4.4.1 officiel (`Godot_v4.4.1-stable_linux.x86_64.zip`) avec les modèles d'export Windows x86_64 tirés de `Godot_v4.4.1-stable_export_templates.tpz`.
2. Blender 5.2.1 officiel (`blender-5.2.1-linux-x64.tar.xz`), sans les noyaux GPU Cycles (CUDA/HIP/oneAPI) ni les modules GPU d'OpenImageDenoise.
3. Aseprite v1.3.18.6 compilé avec clang et libstdc++, `-DLAF_BACKEND=skia`, et Skia (branche `aseprite-m124` de aseprite/skia) compilé avec gn et ninja.
4. Paquets apt installés : `xvfb x11-xkb-utils x11-utils x11-apps libgl1-mesa-dri libglx-mesa0 libegl-mesa0 mesa-vulkan-drivers patchelf`, plus les bibliothèques X11, Wayland, ALSA et Pulse chargées par Godot et Blender.
5. `python3 assembler.py <sortie>` copie les applis et toutes les bibliothèques (glibc comprise) dans `runtime/lib`. Il pose des RUNPATH relatifs (`$ORIGIN`) sur chaque ELF et remplace le chemin `/usr/bin` de xkbcomp codé dans Xvfb par `.`. On copie ensuite `contenu/*` dans la sortie.
6. `tar | xz -7`, découpé en morceaux de 90 Mo (`split -b 90M -d -a 2`), puis `sha256sum > SHA256SUMS`.

À l'installation, `installer.sh` pointe l'interpréteur ELF de chaque programme vers le `ld-linux` embarqué (patchelf). Les outils ne dépendent donc plus de la glibc de la machine.
