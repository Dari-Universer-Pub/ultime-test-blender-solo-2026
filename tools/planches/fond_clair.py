#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fond_clair.py - pose un rendu transparent seul sur un fond gris clair, pour la revue d'un rendu haute résolution.

    python3 tools/planches/fond_clair.py RENDU.png SORTIE.png [--fond d8dce0] [--marge 24]

Outil d'ASSEMBLAGE : il ne dessine aucun asset ; il pose le rendu sur une couleur de fond, sans
redimensionner. Affiche le SHA-256 de la planche, à recopier dans le journal visuel.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("sortie")
    ap.add_argument("--fond", default="d8dce0", help="couleur hexadécimale du fond")
    ap.add_argument("--marge", type=int, default=24)
    a = ap.parse_args()
    src = Image.open(a.rendu).convert("RGBA")
    w, h = src.size
    couleur = tuple(int(a.fond[k:k + 2], 16) for k in (0, 2, 4)) + (255,)
    planche = Image.new("RGBA", (w + 2 * a.marge, h + 2 * a.marge), couleur)
    planche.alpha_composite(src, (a.marge, a.marge))
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    planche.convert("RGB").save(a.sortie)
    sha = hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest()
    print("planche :", a.sortie)
    print("image_sha256 :", sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
