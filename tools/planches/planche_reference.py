#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_reference.py - planche "references + rendu" pour la regle de l'oeil (AGENTS.md, regle 6).

    python3 tools/planches/planche_reference.py --refs art/references/a.jpg art/references/b.jpg \
        --rendus art/pixel/plongeur/idle_01.png art/pixel/plongeur/nage_01.png \
        --sortie boards/plongeur_reference.png

Outil d'ASSEMBLAGE : il pose des images deja existantes cote a cote, avec leurs legendes.
Il ne dessine aucun asset. Les references ne sont jamais utilisees dans le jeu.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HAUTEUR_REF = 240      # hauteur des references (affichage seulement)
ECHELLE_RENDU = 4      # pixels nets pour le rendu du jeu
MARGE = 14
FOND = (22, 40, 58, 255)
TEXTE = (235, 240, 245, 255)


def charger_ref(chemin):
    im = Image.open(chemin).convert("RGBA")
    ratio = HAUTEUR_REF / im.height
    return im.resize((max(1, round(im.width * ratio)), HAUTEUR_REF), Image.LANCZOS)


def charger_rendu(chemin):
    im = Image.open(chemin).convert("RGBA")
    return im.resize((im.width * ECHELLE_RENDU, im.height * ECHELLE_RENDU), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", nargs="+", required=True)
    ap.add_argument("--rendus", nargs="+", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--credit", default="Reference : libre d'usage, voir art/references/SOURCES.md")
    a = ap.parse_args()

    refs = [charger_ref(r) for r in a.refs]
    rendus = [charger_rendu(r) for r in a.rendus]
    largeur_ligne1 = sum(r.width for r in refs) + MARGE * (len(refs) + 1)
    largeur_ligne2 = sum(r.width for r in rendus) + MARGE * (len(rendus) + 1)
    W = max(largeur_ligne1, largeur_ligne2, 760)
    hauteur_rendu = max(r.height for r in rendus)
    H = MARGE + 18 + HAUTEUR_REF + MARGE + 18 + hauteur_rendu + MARGE + 18 + MARGE
    planche = Image.new("RGBA", (W, H), FOND)
    d = ImageDraw.Draw(planche)

    y = MARGE
    d.text((MARGE, y), "REFERENCES (on s'inspire des silhouettes et proportions, on ne copie pas)", fill=TEXTE)
    y += 18
    x = MARGE
    for r in refs:
        planche.alpha_composite(r, (x, y))
        x += r.width + MARGE
    y += HAUTEUR_REF + MARGE
    d.text((MARGE, y), "RENDU DU PROJET (pixelise, palette art/palette.json)", fill=TEXTE)
    y += 18
    x = MARGE
    for r in rendus:
        planche.alpha_composite(r, (x, y))
        x += r.width + MARGE
    y += hauteur_rendu + MARGE
    d.text((MARGE, y), a.credit, fill=TEXTE)

    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    if Path(a.sortie).exists():
        Path(a.sortie).unlink()
    planche.save(a.sortie)
    print(f"planche : {a.sortie}")
    print(f"image_sha256 : {hashlib.sha256(Path(a.sortie).read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
