#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_dc.py - planche de comparaison du héros « Dead Cells » (v5) avec les versions précédentes.

    python3 tools/planches/planche_dc.py HD.png V4PX.png V5.png SORTIE.png [--echelle 4] [--texte points.txt]

Ligne 1 : rendu v4 haute résolution (réduit à la hauteur du ×4), héros v4_px (×4, eau claire), héros v5 (×4, eau claire).
Ligne 2 : héros v5 ×4 sur eau sombre, sur damier, et la liste des trois points les plus faibles.
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


def damier(w, h, pas=8):
    im = Image.new("RGBA", (w, h), (200, 200, 200, 255))
    fonce = Image.new("RGBA", (pas, pas), (150, 150, 150, 255))
    for y in range(0, h, pas):
        for x in range(0, w, pas):
            if ((x // pas) + (y // pas)) % 2:
                im.paste(fonce, (x, y))
    return im


def sur_fond(sprite, fond, taille):
    """Sprite agrandi (pixels nets) posé sur un fond de la taille donnée."""
    if fond is None:
        base = damier(taille, taille)
    else:
        base = Image.new("RGBA", (taille, taille), fond)
    agrandi = sprite.resize((taille, taille), Image.NEAREST)
    base.alpha_composite(agrandi)
    return base


def hd_sur_fond(hd, taille):
    base = Image.new("RGBA", (taille, taille), EAU_CLAIRE)
    reduit = hd.copy()
    reduit.thumbnail((taille - 2 * MARGE, taille - 2 * MARGE), Image.LANCZOS)
    base.alpha_composite(reduit, ((taille - reduit.width) // 2, (taille - reduit.height) // 2))
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hd")
    ap.add_argument("v4px")
    ap.add_argument("v5")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=4)
    ap.add_argument("--texte", default=None, help="fichier texte : les trois points faibles, une ligne chacun (sans accents : police par défaut)")
    args = ap.parse_args()

    taille = 112 * args.echelle
    hd = Image.open(args.hd).convert("RGBA")
    v4px = Image.open(args.v4px).convert("RGBA")
    v5 = Image.open(args.v5).convert("RGBA")
    if v4px.size != (112, 112) or v5.size != (112, 112):
        raise SystemExit("les sprites doivent faire 112 x 112")

    panneaux = [
        ("v4 haute resolution (768 px)", hd_sur_fond(hd, taille)),
        ("v4_px, hero actuel (x4)", sur_fond(v4px, EAU_CLAIRE, taille)),
        ("v5 Dead Cells (x4), eau claire", sur_fond(v5, EAU_CLAIRE, taille)),
        ("v5 Dead Cells (x4), eau sombre", sur_fond(v5, EAU_SOMBRE, taille)),
        ("v5 Dead Cells (x4), damier", sur_fond(v5, None, taille)),
    ]
    colonnes = 3
    lignes = 2
    w = colonnes * taille + (colonnes + 1) * MARGE
    h = lignes * (taille + ETIQUETTE) + (lignes + 1) * MARGE
    planche = Image.new("RGBA", (w, h), (28, 28, 28, 255))
    dessin = ImageDraw.Draw(planche)
    for i, (titre, image) in enumerate(panneaux):
        ligne, col = divmod(i, colonnes)
        x = MARGE + col * (taille + MARGE)
        y = MARGE + ligne * (taille + ETIQUETTE + MARGE)
        dessin.text((x, y + 4), titre, fill=(230, 230, 230, 255))
        planche.alpha_composite(image, (x, y + ETIQUETTE))
    # case libre (ligne 2, colonne 3) : les trois points faibles
    x = MARGE + 2 * (taille + MARGE)
    y = MARGE + (taille + ETIQUETTE + MARGE)
    dessin.rectangle((x, y + ETIQUETTE, x + taille, y + ETIQUETTE + taille), fill=(40, 40, 46, 255))
    dessin.text((x + 12, y + ETIQUETTE + 10), "Points les plus faibles", fill=(255, 220, 120, 255))
    if args.texte:
        points = [p.strip() for p in Path(args.texte).read_text(encoding="utf-8").splitlines() if p.strip()]
        for k, point in enumerate(points[:3]):
            dessin.text((x + 12, y + ETIQUETTE + 36 + k * 44), f"{k + 1}. {point}", fill=(235, 235, 235, 255))
    planche.convert("RGB").save(args.sortie)
    print("planche :", args.sortie)
    print("image_sha256 :", hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
