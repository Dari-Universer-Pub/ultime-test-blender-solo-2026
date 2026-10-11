#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_etats.py - planche « états » : des lignes d'images déjà existantes, agrandies (pixels nets),
avec un titre par ligne. Sert à montrer la base (rendu brut) et la version actuelle, côte à côte.

    python3 tools/planches/planche_etats.py --sortie boards/plongeur_base.png \
        --ligne "BASE : pixelisation brute" art/pixel/plongeur/nage_01.png art/pixel/plongeur/idle_01.png

Outil d'ASSEMBLAGE : il pose des images existantes, il ne dessine aucun asset.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ECHELLE = 4
MARGE = 12
FOND = (22, 40, 58, 255)
TEXTE = (235, 240, 245, 255)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--ligne", nargs="+", action="append", required=True,
                    help="titre suivi des images de la ligne")
    a = ap.parse_args()
    lignes = []
    for ligne in a.ligne:
        titre, images = ligne[0], ligne[1:]
        ims = [Image.open(p).convert("RGBA") for p in images]
        ims = [i.resize((i.width * ECHELLE, i.height * ECHELLE), Image.NEAREST) for i in ims]
        lignes.append((titre, ims))
    largeur = max(sum(i.width for i in ims) + MARGE * (len(ims) + 1) for _, ims in lignes)
    hauteur = sum(18 + max(i.height for i in ims) + MARGE for _, ims in lignes) + MARGE
    planche = Image.new("RGBA", (max(largeur, 400), hauteur), FOND)
    d = ImageDraw.Draw(planche)
    y = MARGE
    for titre, ims in lignes:
        d.text((MARGE, y), titre, fill=TEXTE)
        y += 18
        x = MARGE
        for i in ims:
            planche.alpha_composite(i, (x, y))
            x += i.width + MARGE
        y += max(i.height for i in ims) + MARGE
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    if Path(a.sortie).exists():
        Path(a.sortie).unlink()
    planche.save(a.sortie)
    print(f"planche : {a.sortie}")
    print(f"image_sha256 : {hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
