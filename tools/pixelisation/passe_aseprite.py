#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
passe_aseprite.py - applique une passe de nettoyage à la main (liste de pixels) à une image, dans Aseprite.

    python3 tools/pixelisation/passe_aseprite.py ENTREE.png PASSE.json SORTIE.png

PASSE.json : {"nom": "...", "pixels": [{"x": 12, "y": 40, "rgb": "#1f1714", "raison": "..."}, ...]}
Le script écrit un Lua qui ouvre ENTREE.png dans Aseprite, pose chaque pixel, enregistre SORTIE.png et
SORTIE.aseprite. Il compte les pixels réellement changés et affiche le total et le SHA-256 de la sortie.
Outil de nettoyage : il ne dessine rien, il applique les corrections écrites dans PASSE.json.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ASEPRITE = "/opt/outils-varekh/bin/aseprite"


def lua(entree, sortie, pixels):
    lignes = [
        f'local spr = app.open("{entree}")',
        'if not spr then error("ouverture impossible") end',
        "local img = spr.cels[1].image",
    ]
    for p in pixels:
        r, g, b = (int(p["rgb"].lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
        lignes.append(f"img:putPixel({p['x']}, {p['y']}, app.pixelColor.rgba({r}, {g}, {b}, 255))")
    lignes += [
        f'spr:saveAs("{sortie.with_suffix(".aseprite")}")',
        f'spr:saveCopyAs("{sortie}")',
        'print("PASSE_OK")',
    ]
    return "\n".join(lignes) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entree")
    ap.add_argument("passe")
    ap.add_argument("sortie")
    args = ap.parse_args()
    entree, sortie = Path(args.entree).resolve(), Path(args.sortie).resolve()
    passe = json.loads(Path(args.passe).read_text(encoding="utf-8"))
    avant = np.asarray(Image.open(entree).convert("RGBA")).copy()
    if sortie.exists():
        sortie.unlink()
    sortie.with_suffix(".aseprite").unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
        script = Path(tmp) / "passe.lua"
        script.write_text(lua(entree, sortie, passe["pixels"]), encoding="utf-8")
        r = subprocess.run([ASEPRITE, "--batch", "--script", str(script)], capture_output=True, text=True,
                           timeout=300)
    if r.returncode != 0 or "PASSE_OK" not in r.stdout or not sortie.exists():
        sys.exit(f"Aseprite a échoué (code {r.returncode}) :\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    apres = np.asarray(Image.open(sortie).convert("RGBA"))
    changes = int((np.abs(apres.astype(int) - avant.astype(int)).sum(-1) > 0).sum())
    corps = avant[..., 3] > 0
    print(f"passe : {passe.get('nom', '')}")
    print(f"pixels demandés : {len(passe['pixels'])} ; pixels changés : {changes} "
          f"({100.0 * changes / max(1, corps.sum()):.1f} % du héros)")
    print(f"image_sha256 : {hashlib.sha256(sortie.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
