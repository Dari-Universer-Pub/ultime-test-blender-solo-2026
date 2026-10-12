#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tons.py - part de chaque ton de la rampe combinaison dans le corps du plongeur (M0).

    python3 tools/mesure/tons.py art/pixel/plongeur

Compte les pixels de la combinaison (les 4 tons de paliers) sur toutes les images, par groupe.
Critere : le ton le plus fonce ne doit pas occuper la majorite des pixels de combinaison.
Outil de MESURE : il lit des images, ne dessine rien.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def main(dossier):
    pal = json.load(open(os.path.join(RACINE, "art", "palette.json"), encoding="utf-8"))["rampes"]
    comb = [hex_rgb(t) for t in pal["combinaison"]]
    # tous les tons de la rampe combinaison, du plus sombre au plus clair
    paliers = comb
    noms = [f"ton{k}" for k in range(len(comb))]
    for groupe, n in (("nage", 8), ("idle", 6)):
        compte = np.zeros(len(paliers), dtype=np.int64)
        for i in range(1, n + 1):
            f = os.path.join(dossier, f"{groupe}_{i:02d}.png")
            a = np.asarray(Image.open(f).convert("RGBA")).reshape(-1, 4)
            a = a[a[:, 3] == 255][:, :3]
            for k, p in enumerate(paliers):
                compte[k] += int(np.all(a == np.array(p), axis=1).sum())
        tot = compte.sum()
        print(f"## {groupe} : pixels de combinaison {tot}")
        for k in range(len(paliers)):
            if compte[k]:
                print(f"  {noms[k]:6s} #{paliers[k][0]:02x}{paliers[k][1]:02x}{paliers[k][2]:02x} : {100 * compte[k] / max(1, tot):5.1f} %")
        actifs = [k for k in range(len(paliers)) if compte[k]]
        print(f"  tons utilises : {len(actifs)} ; le plus sombre utilise est majoritaire : {'OUI' if compte[actifs[0]] > tot / 2 else 'non'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "art/pixel/plongeur"))
