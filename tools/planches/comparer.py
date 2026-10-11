#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comparer.py - planche AVANT / APRES pour la regle de l'oeil.

    python tools/planches/comparer.py AVANT.png APRES.png SORTIE.png [--echelle 6] [--case x,y,w,h]
    python tools/planches/comparer.py - APRES.png SORTIE.png          (premiere version : pas d'avant)

Chaque image est agrandie au plus proche voisin (pixels nets) et posee sur trois fonds :
eau claire, eau sombre, damier (pour voir la transparence). --case recadre une seule
image d'une feuille de sprites. La commande affiche le SHA-256 de la planche, a
recopier dans le journal visuel (art/journal/<id>.json).

Outil d'ASSEMBLAGE : il ne dessine aucun asset. Necessite Pillow (pip install pillow).
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FONDS = [("eau claire", (64, 140, 170, 255)), ("eau sombre", (14, 32, 52, 255)), ("damier", None)]
MARGE = 12


def damier(w, h, pas=8):
    im = Image.new("RGBA", (w, h), (200, 200, 200, 255))
    fonce = Image.new("RGBA", (pas, pas), (150, 150, 150, 255))
    for y in range(0, h, pas):
        for x in range((y // pas) % 2 * pas, w, 2 * pas):
            im.paste(fonce, (x, y))
    return im


def charger(chemin, case, echelle):
    if chemin == "-":
        return None
    im = Image.open(chemin).convert("RGBA")
    if case:
        x, y, w, h = case
        im = im.crop((x, y, x + w, y + h))
    return im.resize((im.width * echelle, im.height * echelle), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("avant")
    ap.add_argument("apres")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=6)
    ap.add_argument("--case", type=lambda s: tuple(int(v) for v in s.split(",")))
    a = ap.parse_args()
    images = [("AVANT", charger(a.avant, a.case, a.echelle)), ("APRES", charger(a.apres, a.case, a.echelle))]
    images = [(n, i) for n, i in images if i is not None]
    w = max(i.width for _, i in images)
    h = max(i.height for _, i in images)
    W = len(FONDS) * (w + MARGE) + MARGE
    H = len(images) * (h + MARGE + 14) + MARGE
    planche = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    d = ImageDraw.Draw(planche)
    for li, (nom, im) in enumerate(images):
        y = MARGE + li * (h + MARGE + 14)
        d.text((MARGE, y), nom, fill=(255, 255, 255, 255))
        for ci, (fnom, couleur) in enumerate(FONDS):
            x = MARGE + ci * (w + MARGE)
            fond = damier(w, h) if couleur is None else Image.new("RGBA", (w, h), couleur)
            fond.alpha_composite(im, (0, 0))
            planche.paste(fond, (x, y + 14))
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    planche.save(a.sortie)
    print(f"planche : {a.sortie}")
    print(f"image_sha256 : {hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest()}")
    print("Maintenant REGARDE cette image (ouvre le fichier) avant d'ecrire l'entree du journal.")


if __name__ == "__main__":
    sys.exit(main())
