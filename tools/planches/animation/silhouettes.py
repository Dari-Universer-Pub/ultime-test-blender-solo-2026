#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
silhouettes.py - silhouette noire de chaque image d'un lot (union des masques des calques visibles).

    python3 tools/planches/animation/silhouettes.py FICHE.json LOT_DOSSIER

Écrit LOT/silhouettes/<NN_nom>.png : pixels noirs là où un calque est visible, transparent ailleurs.
Sert à lire le geste seul, avant la couleur (méthode : silhouette noire puis couleur). Ne dessine rien.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fiche")
    ap.add_argument("lot")
    a = ap.parse_args()
    fiche = json.loads(Path(a.fiche).read_text(encoding="utf-8"))
    lot = Path(a.lot)
    out = lot / "silhouettes"
    out.mkdir(parents=True, exist_ok=True)
    for f in fiche["images"]:
        nom = "%02d_%s" % (f["n"], f["nom"])
        dossier = lot / "sortie" / "masques" / nom
        union = None
        for p in sorted(dossier.glob("*.png")):
            m = np.array(Image.open(p).convert("L")) > 0
            union = m if union is None else (union | m)
        img = np.zeros(union.shape + (4,), dtype=np.uint8)
        img[union] = (0, 0, 0, 255)
        Image.fromarray(img).save(out / (nom + ".png"))
    print("silhouettes:", len(fiche["images"]), "->", out)


if __name__ == "__main__":
    main()
