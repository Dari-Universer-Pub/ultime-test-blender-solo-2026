#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pixel_quatre.py - planche de revue d'une pixelisation : le rendu haute résolution à gauche, la pixelisation
agrandie (×4, pixels nets) sur eau claire, eau sombre et damier à droite.

    python3 tools/planches/pixel_quatre.py RENDU.png PIXEL.png SORTIE.png [--echelle 4]

Outil d'ASSEMBLAGE : il ne dessine aucun asset ; il pose et agrandit des images. Affiche le SHA-256 de la planche.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FONDS = [("eau claire", (64, 140, 170, 255)), ("eau sombre", (14, 32, 52, 255)), ("damier", None)]
MARGE = 16
ETIQUETTE = 22


def damier(w, h, pas=8):
    im = Image.new("RGBA", (w, h), (200, 200, 200, 255))
    fonce = Image.new("RGBA", (pas, pas), (150, 150, 150, 255))
    for y in range(0, h, pas):
        for x in range(0, w, pas):
            if ((x // pas) + (y // pas)) % 2:
                im.paste(fonce, (x, y))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("pixel")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=4)
    a = ap.parse_args()
    haute = Image.open(a.rendu).convert("RGBA")
    px = Image.open(a.pixel).convert("RGBA")
    grand = px.resize((px.width * a.echelle, px.height * a.echelle), Image.NEAREST)
    h_max = max(haute.height, grand.height)
    colonnes = [("rendu haute résolution", haute)]
    for nom, fond in FONDS:
        base = damier(grand.width, grand.height) if fond is None else Image.new("RGBA", grand.size, fond)
        base.alpha_composite(grand)
        colonnes.append((f"pixel ×{a.echelle} · {nom}", base))
    largeur = sum(c.width for _, c in colonnes) + MARGE * (len(colonnes) + 1)
    hauteur = h_max + 2 * MARGE + ETIQUETTE
    planche = Image.new("RGBA", (largeur, hauteur), (232, 234, 236, 255))
    dessin = ImageDraw.Draw(planche)
    x = MARGE
    for nom, im in colonnes:
        dessin.text((x, 4), nom, fill=(30, 30, 30, 255))
        planche.alpha_composite(im, (x, MARGE + ETIQUETTE))
        x += im.width + MARGE
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    planche.convert("RGB").save(a.sortie)
    print("planche :", a.sortie)
    print("image_sha256 :", hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
