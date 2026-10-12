#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nettoyage.py - nettoyage des pixels isolés d'un rendu direct (sans contour).

    python3 tools/pixelisation/nettoyage.py RENDU.png SORTIE.png

Un pixel isolé est un pixel du corps dont aucun des 8 voisins n'a la même couleur. Il prend la couleur
majoritaire de ses voisins du corps (au moins 2 voisins de cette couleur), sinon celle d'un voisin direct,
en boucle jusqu'à zéro (6 passes au plus). Pas de contour : ce script ne trace rien.
Affiche le nombre d'isolés avant et après, le nombre de pixels changés, et le SHA-256 de la sortie.
"""
import argparse
import collections
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

VOISINS8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
VOISINS4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def cles(arr):
    c = (arr[..., 0].astype(np.int64) << 16) | (arr[..., 1].astype(np.int64) << 8) | arr[..., 2].astype(np.int64)
    c[arr[..., 3] == 0] = -1
    return c


def isoles(arr):
    corps = arr[..., 3] > 0
    c = cles(arr)
    h, w = corps.shape
    n = 0
    for y in range(h):
        for x in range(w):
            if not corps[y, x]:
                continue
            v = [c[y + dy, x + dx] for dy, dx in VOISINS8 if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]]
            if v and c[y, x] not in v:
                n += 1
    return n


def nettoyer(arr, passes=6):
    arr = arr.copy()
    corps = arr[..., 3] > 0
    h, w = corps.shape
    for _ in range(passes):
        c = cles(arr)
        modifies = 0
        for y in range(h):
            for x in range(w):
                if not corps[y, x]:
                    continue
                voisins = [(y + dy, x + dx) for dy, dx in VOISINS8
                           if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]]
                if not voisins or c[y, x] in [c[p] for p in voisins]:
                    continue
                majo, n = collections.Counter(c[p] for p in voisins).most_common(1)[0]
                if n >= 2:
                    src = next(p for p in voisins if c[p] == majo)
                else:
                    src = next(((y + dy, x + dx) for dy, dx in VOISINS4 + tuple(VOISINS8)
                                if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]), None)
                    if src is None:
                        continue
                arr[y, x, :3] = arr[src[0], src[1], :3]
                modifies += 1
        if modifies == 0:
            break
    return arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("sortie")
    args = ap.parse_args()
    avant = np.asarray(Image.open(args.rendu).convert("RGBA")).copy()
    apres = nettoyer(avant)
    Image.fromarray(apres).save(args.sortie)
    changes = int((np.abs(apres.astype(int) - avant.astype(int)).sum(-1) > 0).sum())
    corps = int((avant[..., 3] > 0).sum())
    print(f"isolés avant : {isoles(avant)} ; après : {isoles(apres)} ; pixels changés : {changes} ({100.0 * changes / corps:.1f} %)")
    print(f"image_sha256 : {hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
