#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
passe_majorite.py - passe de finition par MAJORITÉ 3 x 3, limitée à des groupes de la carte d'identité.

    python3 tools/pixelisation/passe_majorite.py CONTOUR.png GROUPES.png PALETTE.json GROUPES_A_TRAITER SORTIE.json
        [--seuil 4] [--nom "passe 1 : ..."]

Pour chaque pixel de la zone (groupe demandé, hors contour) : si, parmi ses 8 voisins de même groupe et
hors contour, une couleur en apparaît au moins --seuil fois et que le pixel n'a pas cette couleur, le pixel
prend cette couleur. Une passe ne touche donc que des pixels isolés dans leur ton, jamais les contours.
Sortie : un JSON de pixels pour tools/pixelisation/passe_aseprite.py (pixels : x, y, rgb, raison).
"""
import argparse
import collections
import json
from pathlib import Path

import numpy as np
from PIL import Image


CONTOURS = {"#120c28", "#3c3a7a"}     # contours de la palette v6 (ombre, lumière) : jamais retouchés ici


def charger(chemin):
    return np.asarray(Image.open(chemin).convert("RGBA")).copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contour")
    ap.add_argument("groupes")
    ap.add_argument("palette")
    ap.add_argument("a_traiter", help="noms de groupes séparés par des virgules, ex. tete,collerette")
    ap.add_argument("sortie")
    ap.add_argument("--seuil", type=int, default=4)
    ap.add_argument("--nom", default="passe de majorité 3 x 3")
    args = ap.parse_args()

    img = charger(args.contour)
    ident = charger(args.groupes)
    rampes = json.loads(Path(args.palette).read_text(encoding="utf-8"))["rampes"]
    nom_de = {"#%02x%02x%02x" % tuple(int(v.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)): g
              for g, (v,) in rampes.items()}
    voulus = set(args.a_traiter.split(","))
    h, w = img[..., 3].shape
    corps = img[..., 3] > 0
    contour_hex = "#%02x%02x%02x"
    groupe_px = np.full((h, w), "", dtype=object)
    for y, x in zip(*np.where(corps)):
        groupe_px[y, x] = nom_de.get(contour_hex % tuple(ident[y, x, :3]), "")
    couleur = np.array([[contour_hex % tuple(img[y, x, :3]) if corps[y, x] else "" for x in range(w)]
                        for y in range(h)], dtype=object)
    contours = CONTOURS
    pixels = []
    for y in range(h):
        for x in range(w):
            if not corps[y, x] or groupe_px[y, x] not in voulus or couleur[y, x] in contours:
                continue
            voisins = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (dy, dx) == (0, 0):
                        continue
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and corps[yy, xx] and groupe_px[yy, xx] == groupe_px[y, x] \
                            and couleur[yy, xx] not in contours:
                        voisins.append(couleur[yy, xx])
            if not voisins:
                continue
            majo, n = collections.Counter(voisins).most_common(1)[0]
            if n >= args.seuil and majo != couleur[y, x] and voisins.count(couleur[y, x]) < args.seuil:
                pixels.append({"x": x, "y": y, "rgb": majo, "raison": "majorité 3 x 3 dans le groupe " + groupe_px[y, x]})
    Path(args.sortie).write_text(json.dumps({"nom": args.nom, "pixels": pixels}, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
    surface = int((corps & np.isin(groupe_px, list(voulus))).sum())
    print(f"{args.nom} : {len(pixels)} pixels proposés sur {surface} de la zone ({100.0 * len(pixels) / max(1, corps.sum()):.1f} % du héros)")


if __name__ == "__main__":
    main()
