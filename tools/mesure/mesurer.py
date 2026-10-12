#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mesurer.py - mesures du plongeur (M0) : taille de chaque image et amplitude d'animation.

    python3 tools/mesure/mesurer.py art/pixel/plongeur

Taille : boite englobante des pixels opaques de chaque image (contour compris), en pixels.
Amplitude d'un groupe d'images = 1 - (pixels communs a TOUTES les images) / (pixels d'AU MOINS une image).
Un groupe immobile vaut 0 ; un groupe qui bouge beaucoup se rapproche de 1.

Outil de MESURE (autorise par AGENTS.md) : il lit des images, ne dessine rien.
"""
import os
import sys

import numpy as np
from PIL import Image

GROUPES = {"nage": [f"nage_{i:02d}.png" for i in range(1, 9)],
           "idle": [f"idle_{i:02d}.png" for i in range(1, 7)]}


def masque(chemin):
    a = np.asarray(Image.open(chemin).convert("RGBA"))[..., 3]
    return a > 0


def boite(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return 0, 0
    return int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


def amplitude(masques):
    inter = np.logical_and.reduce(masques)
    union = np.logical_or.reduce(masques)
    return 1.0 - inter.sum() / max(1, union.sum())


def main(dossier):
    rapport = {}
    for groupe, fichiers in GROUPES.items():
        chemins = [os.path.join(dossier, f) for f in fichiers]
        if not all(os.path.exists(c) for c in chemins):
            print(f"{groupe} : images manquantes dans {dossier}")
            return 1
        ms = [masque(c) for c in chemins]
        print(f"## {groupe} ({len(ms)} images)")
        print("| image | largeur | hauteur | plus grande dimension |")
        print("|---|---|---|---|")
        for f, m in zip(fichiers, ms):
            w, h = boite(m)
            print(f"| {f} | {w} | {h} | {max(w, h)} |")
        plus = [max(boite(m)) for m in ms]
        print(f"plus grande dimension : min {min(plus)}, max {max(plus)}")
        amp = amplitude(ms)
        print(f"amplitude {groupe} : {amp:.3f}")
        rapport[groupe] = {"amplitude": round(float(amp), 3), "dimensions": plus}
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "art/pixel/plongeur"))
