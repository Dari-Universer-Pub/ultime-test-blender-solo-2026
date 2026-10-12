#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_sans_contour.py - planche de revue d'un sprite SANS contour : eau claire, eau sombre, damier et
niveaux de gris, à ×6, puis les mesures et les écarts lus sur la planche.

    python3 tools/planches/planche_sans_contour.py SPRITE.png MESURES.txt SORTIE.png [--echelle 6]

Outil d'ASSEMBLAGE : il ne dessine aucun asset ; il pose et agrandit des images. Affiche le SHA-256 de la planche.
"""
import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

EAU_CLAIRE = (64, 140, 170, 255)
EAU_SOMBRE = (14, 32, 52, 255)
MARGE = 16
ETIQUETTE = 20


def damier(taille, pas=8):
    im = Image.new("RGBA", (taille, taille), (200, 200, 200, 255))
    fonce = Image.new("RGBA", (pas, pas), (150, 150, 150, 255))
    for y in range(0, taille, pas):
        for x in range(0, taille, pas):
            if ((x // pas) + (y // pas)) % 2:
                im.paste(fonce, (x, y))
    return im


def sur_fond(sprite, fond, taille):
    base = damier(taille) if fond is None else Image.new("RGBA", (taille, taille), fond)
    base.alpha_composite(sprite.resize((taille, taille), Image.NEAREST))
    return base


def gris(sprite, taille):
    """Niveaux de gris sur fond gris moyen : vérifie que la silhouette se lit par la seule valeur."""
    g = sprite.convert("LA").convert("RGBA")
    g = Image.merge("RGBA", (*(g.split()[0],) * 3, g.split()[1]))
    return sur_fond(g, (128, 128, 128, 255), taille)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sprite")
    ap.add_argument("mesures")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=6)
    args = ap.parse_args()
    taille = 112 * args.echelle
    sp = Image.open(args.sprite).convert("RGBA")
    if sp.size != (112, 112):
        raise SystemExit("le sprite doit faire 112 x 112")
    lignes = [t.rstrip() for t in Path(args.mesures).read_text(encoding="utf-8").splitlines() if t.strip()]
    panneaux = [
        ("eau claire (x6)", sur_fond(sp, EAU_CLAIRE, taille)),
        ("eau sombre (x6)", sur_fond(sp, EAU_SOMBRE, taille)),
        ("damier (x6)", sur_fond(sp, None, taille)),
        ("niveaux de gris, fond gris (x6)", gris(sp, taille)),
    ]
    colonnes = 2
    lignes_rangees = 2
    w = colonnes * taille + (colonnes + 1) * MARGE
    h = lignes_rangees * (taille + ETIQUETTE + MARGE) + MARGE + 24 + 16 * len(lignes) + MARGE
    planche = Image.new("RGBA", (w, h), (28, 28, 28, 255))
    d = ImageDraw.Draw(planche)
    for i, (titre, im) in enumerate(panneaux):
        ligne, col = divmod(i, colonnes)
        x = MARGE + col * (taille + MARGE)
        y = MARGE + ligne * (taille + ETIQUETTE + MARGE)
        d.text((x, y + 4), titre, fill=(230, 230, 230, 255))
        planche.alpha_composite(im, (x, y + ETIQUETTE))
    y = MARGE + lignes_rangees * (taille + ETIQUETTE + MARGE)
    d.text((MARGE, y), "Mesures et ecarts (sans contour)", fill=(255, 220, 120, 255))
    for k, t in enumerate(lignes):
        d.text((MARGE, y + 24 + 16 * k), t, fill=(235, 235, 235, 255))
    planche.convert("RGB").save(args.sortie)
    print("planche :", args.sortie)
    print("image_sha256 :", hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
