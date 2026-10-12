#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
animation.py - mesure d'une animation image par image (sprites 112 x 112 nettoyés, sans contour).

    python3 tools/mesure/animation.py ANCRE.png DOSSIER [--motif "idle_*.png"]

Pour chaque image, par rapport à l'ancre : hauteur (px), décalage du haut et du bas (négatif = plus haut),
largeur, pixels opaques au-dessus du haut de l'ancre (bulles, fumée), pixels différents de l'ancre et de
l'image précédente (cycle). Mesure seulement : ce script ne dessine rien.
Code de retour 0 si aucune image n'est vide et si deux images consécutives ne sont pas identiques.
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image


def charger(chemin):
    return np.asarray(Image.open(chemin).convert("RGBA"))


def boite(arr):
    ys, xs = np.where(arr[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ancre")
    ap.add_argument("dossier")
    ap.add_argument("--motif", default="idle_*.png")
    args = ap.parse_args()
    ancre = charger(args.ancre)
    haut0, bas0, g0, d0 = boite(ancre)
    alpha0 = ancre[..., 3] > 0
    print("ANCRE hauteur %d px (haut %d, bas %d), largeur %d px" % (bas0 - haut0 + 1, haut0, bas0, d0 - g0 + 1))
    precedente = None
    ok = True
    images = []
    for f in sorted(glob.glob(os.path.join(args.dossier, args.motif))):
        im = charger(f)
        a = im[..., 3] > 0
        if not a.any():
            print("VIDE", f)
            ok = False
            continue
        haut, bas, g, d = boite(im)
        au_dessus = int(a[:haut0, :].sum())
        vs_ancre = int(((im != ancre).any(axis=2) & (a | alpha0)).sum())
        vs_prec = None if precedente is None else int(((im != precedente).any(axis=2) & (a | (precedente[..., 3] > 0))).sum())
        if vs_prec == 0:
            ok = False
        print("%s : hauteur %d px, haut %+d, bas %+d, largeur %d px, au-dessus de l'ancre %d px, "
              "écart ancre %d px, écart image précédente %s"
              % (os.path.basename(f), bas - haut + 1, haut - haut0, bas - bas0, d - g + 1, au_dessus, vs_ancre,
                 "-" if vs_prec is None else "%d px" % vs_prec))
        images.append(im)
        precedente = im
    distinctes = len({im.tobytes() for im in images})
    print("IMAGES DISTINCTES %d sur %d" % (distinctes, len(images)))
    if distinctes != len(images):
        ok = False
    print("RESULTAT", "OK" if ok else "ECHEC")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
