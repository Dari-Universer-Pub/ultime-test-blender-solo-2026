# outils-varekh : Godot, Blender et Aseprite déjà compilés (Linux x86_64)

Tout est autonome : glibc, X11, Mesa (rendu OpenGL/Vulkan logiciel llvmpipe), écran virtuel Xvfb.
Rien à compiler, rien à installer avec apt, aucun accès réseau. Testé sur Ubuntu 24.04 et sur
Debian 11 minimal (sans X, sans Mesa, sans Python).

| Outil | Version | Lanceur |
|---|---|---|
| Godot | 4.4.1 stable (officiel) + modèles d'export Windows x86_64 | `bin/godot` |
| Blender | 5.2.1 LTS (officiel, noyaux GPU Cycles retirés) | `bin/blender` |
| Aseprite | 1.3.18.6 compilé depuis les sources (Skia m124) | `bin/aseprite` |
| Python | 3.13 (celui de Blender, avec numpy) | `bin/python` |

## Installer (à chaque nouvelle sandbox, environ 1 minute)

Depuis le dépôt : `bash INSTALLER_OUTILS.sh` (dans `/opt/outils-varekh`, ou `~/outils-varekh` si `/opt` est interdit).
Si le dossier est déplacé : `bash installer.sh` dans le dossier (quelques secondes).
Puis : `bash verifier.sh`. Il doit afficher `SUCCES`, et les images de preuve sont dans `/tmp/outils-varekh-verif/`.

## Utilisation

```bash
O=/opt/outils-varekh/bin
$O/godot --headless --path projet --quit                 # charge le projet sans écran
$O/godot --path projet                                   # lance le jeu (écran virtuel :99 auto)
$O/godot --headless --path projet --export-release "Windows Desktop" builds/jeu.exe
$O/blender -b fichier.blend --python script.py           # rendu Workbench / EEVEE sans écran
$O/aseprite --batch --script fichier.lua                 # Aseprite en ligne de commande
$O/aseprite --batch sprite.aseprite --sheet planche.png --data planche.json --format json-array
```

### Voir ce que fait le jeu (vision)

- **Capture prise par Godot** (exigée par le kit) : `get_viewport().get_texture().get_image().save_png(...)`
  marche tel quel, car `bin/godot` démarre tout seul un écran virtuel avec OpenGL.
- **Film image par image** sans toucher au code du jeu :
  `$O/godot-capture projet shots/film 120` donne `shots/film/image00000000.png` … (120 images à 30 i/s).
  Une scène précise : `$O/godot-capture projet shots/film 60 res://scenes/plongee.tscn`.
- **Capture de tout l'écran** pendant que le jeu tourne :
  `$O/godot --path projet & sleep 3; $O/capture-ecran shots/ecran.png`

Ensuite l'IA ouvre et regarde le PNG.

## Notes

- L'écran virtuel est `:99` (1920x1080, réglable avec `VAREKH_ECRAN=1280x720x24`). Pour d'autres programmes : `eval $($O/xvfb-demarrer)`.
- Le rendu est logiciel (llvmpipe). Il est plus lent qu'une carte graphique, mais l'image est identique.
- Le son passe par le pilote factice dans la sandbox. C'est normal, il n'y a pas de carte son.
- Ces programmes ne marchent que lancés par `bin/…` : ce sont les lanceurs qui règlent l'environnement.
