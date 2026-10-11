#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carte.py - affiche la carte des couleurs d'une image pixel art (lecture seule).

    python3 tools/mesure/carte.py <image.png> [--image-index N] [--x0 0 --y0 0 --x1 W --y1 H]

Chaque couleur opaque reçoit une lettre ; les pixels transparents sont « . ».
La légende donne le code hexadécimal de chaque lettre et son nombre de pixels.
Outil de MESURE (autorisé par AGENTS.md) : il lit les pixels et ne modifie rien.
"""
import argparse
import sys
from collections import Counter

from PIL import Image

LETTRES = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--x0", type=int, default=0)
    ap.add_argument("--y0", type=int, default=0)
    ap.add_argument("--x1", type=int, default=None)
    ap.add_argument("--y1", type=int, default=None)
    a = ap.parse_args()
    im = Image.open(a.image).convert("RGBA")
    w, h = im.size
    x1 = a.x1 if a.x1 is not None else w
    y1 = a.y1 if a.y1 is not None else h
    px = im.load()
    compte = Counter()
    for y in range(a.y0, y1):
        for x in range(a.x0, x1):
            r, g, b, al = px[x, y]
            if al > 0:
                compte["#%02x%02x%02x" % (r, g, b)] += 1
    lettre = {}
    for k, (c, _) in enumerate(compte.most_common(len(LETTRES))):
        lettre[c] = LETTRES[k]
    print("   " + "".join(str((x // 10) % 10) if x % 10 == 0 else " " for x in range(a.x0, x1)))
    print("   " + "".join(str(x % 10) for x in range(a.x0, x1)))
    for y in range(a.y0, y1):
        ligne = ""
        for x in range(a.x0, x1):
            r, g, b, al = px[x, y]
            ligne += "." if al == 0 else lettre.get("#%02x%02x%02x" % (r, g, b), "?")
        print("%2d %s" % (y, ligne))
    print("légende :")
    for c, n in compte.most_common(len(LETTRES)):
        print("  %s %s %d" % (lettre[c], c, n))
    if len(compte) > len(LETTRES):
        print("  (%d couleurs en plus non affichées)" % (len(compte) - len(LETTRES)))


if __name__ == "__main__":
    sys.exit(main())
