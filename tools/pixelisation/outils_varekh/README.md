# Outils déjà compilés : Godot + Blender + Aseprite (Linux x86_64)

Ce zip ne contient que les 3 logiciels, aucun kit de jeu. Rien à compiler.

```bash
unzip abyssal-sandbox-arena-outils-seuls.zip     # si c'est le zip téléchargé
bash abyssal-sandbox-arena-outils-seuls/INSTALLER_OUTILS.sh   # 1 minute, sans réseau -> /opt/outils-varekh
bash /opt/outils-varekh/verifier.sh               # doit afficher SUCCES (13 tests)
```

**Après chaque réinitialisation de la sandbox, les outils disparaissent : relance `INSTALLER_OUTILS.sh`
(1 minute). Il ne faut JAMAIS recompiler Godot, Blender ou Aseprite.**

| Outil | Version | Commande |
|---|---|---|
| Godot | 4.4.1 + modèles d'export Windows | `/opt/outils-varekh/bin/godot` |
| Blender | 5.2.1 LTS | `/opt/outils-varekh/bin/blender` |
| Aseprite | 1.3.18.6 (compilé, Skia) | `/opt/outils-varekh/bin/aseprite` |
| Vision | écran virtuel + OpenGL logiciel | `/opt/outils-varekh/bin/godot-capture`, `/opt/outils-varekh/bin/capture-ecran` |

Pour `tools/outils.json` d'un projet :
```json
{
  "godot": ["/opt/outils-varekh/bin/godot"],
  "blender": ["/opt/outils-varekh/bin/blender"],
  "aseprite": ["/opt/outils-varekh/bin/aseprite"]
}
```
Si `/opt` est interdit, l'installateur se rabat sur `~/outils-varekh` et affiche les bons chemins.
Détails, captures et exemples : [LISEZMOI_OUTILS.md](LISEZMOI_OUTILS.md).

**Dans un projet de jeu** : place ce dossier HORS du projet, ou dedans sous `tools/pixelisation/outils_varekh/`
(jamais à la racine du projet : `gate.py` y verrait du code Pillow comme du dessin par code).
