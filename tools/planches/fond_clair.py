#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fond_clair.py - pose un rendu transparent sur un fond gris clair, pour la revue d'un rendu haute résolution.

    python3 tools/planches/fond_clair.py RENDU.png SORTIE.png [--fond d8dce0] [--marge 24]
    python3 tools/planches/fond_clair.py RENDU.png SORTIE.png --avant AVANT.png

Avec --avant, les deux rendus sont posés côte à côte (AVANT à gauche, APRÈS à droite), étiquetés.
Outil d'ASSEMBLAGE : il ne dessine aucun asset ; il pose les rendus sur une couleur de fond, sans les
redimensionner. Affiche le SHA-256 de la planche, à recopier dans le journal visuel.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("sortie")
    ap.add_argument("--avant", default=None, help="rendu précédent, posé à gauche pour la comparaison")
    ap.add_argument("--fond", default="d8dce0", help="couleur hexadécimale du fond")
    ap.add_argument("--marge", type=int, default=24)
    a = ap.parse_args()
    couleur = tuple(int(a.fond[k:k + 2], 16) for k in (0, 2, 4)) + (255,)
    apres = Image.open(a.rendu).convert("RGBA")
    if not a.avant:
        panneaux = [("", apres)]
    else:
        panneaux = [("AVANT", Image.open(a.avant).convert("RGBA")), ("APRÈS", apres)]
    ecart = 2 * a.marge
    haut = 28 if a.avant else 0
    largeur = sum(p.size[0] for _, p in panneaux) + a.marge * 2 + ecart * (len(panneaux) - 1)
    hauteur = max(p.size[1] for _, p in panneaux) + 2 * a.marge + haut
    planche = Image.new("RGBA", (largeur, hauteur), couleur)
    dessin = ImageDraw.Draw(planche)
    x = a.marge
    for nom, p in panneaux:
        planche.alpha_composite(p, (x, a.marge + haut))
        if nom:
            dessin.text((x, 8), nom, fill=(20, 20, 20, 255))
        x += p.size[0] + ecart
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    planche.convert("RGB").save(a.sortie)
    sha = hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest()
    print("planche :", a.sortie)
    print("image_sha256 :", sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
