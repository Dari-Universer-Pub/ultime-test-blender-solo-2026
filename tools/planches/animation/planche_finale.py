#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_finale.py - planche de fin de lot : l'ancre à côté des images du lot, en ×4 et en ×1, et les effets séparés.

    python3 tools/planches/animation/planche_finale.py FICHE.json LOT_DOSSIER SORTIE.png

Assemble (ne dessine rien) : ancre validée, puis les images sortie/<NN_nom>.png dans l'ordre de la fiche, sur un
fond d'eau claire ; une rangée ×4 et une rangée ×1 (pixels nets) ; les effets (effets/arc_*.png, impact_particules.png)
dans une troisième rangée, ×4. Les étiquettes sont posées sur la planche.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent.parent.parent
ANCRE = RACINE / "art" / "references" / "ancre_plongeur_v6.png"
FOND = (64, 140, 170, 255)
MARGE = 10


def sur_fond(im):
    fond = Image.new("RGBA", im.size, FOND)
    fond.alpha_composite(im.convert("RGBA"))
    return fond.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fiche")
    ap.add_argument("lot")
    ap.add_argument("sortie")
    a = ap.parse_args()
    fiche = json.loads(Path(a.fiche).read_text(encoding="utf-8"))
    lot = Path(a.lot)
    images = [("ancre", Image.open(ANCRE).convert("RGBA"))]
    for f in fiche["images"]:
        nom = "%02d_%s" % (f["n"], f["nom"])
        images.append((nom, Image.open(lot / "sortie" / (nom + ".png")).convert("RGBA")))
    effets = []
    if (lot / "effets").is_dir():  # lot sans effets (saut) : pas de troisième rangée
        effets = [("arc_%d" % k, Image.open(lot / "effets" / ("arc_%d.png" % k)).convert("RGBA")) for k in range(1, 5)]
        effets.append(("impact+part.", Image.open(lot / "effets" / "impact_particules.png").convert("RGBA")))
    cote = 112
    colonnes = max(len(images), len(effets))
    lignes = [(4, images), (1, images)] + ([(4, effets)] if effets else [])
    hauteur = sum(e * cote + 22 + MARGE for e, _ in lignes) + MARGE
    largeur = colonnes * (cote * 4 + MARGE) + MARGE
    planche = Image.new("RGB", (largeur, hauteur), (14, 32, 52))
    d = ImageDraw.Draw(planche)
    y = MARGE
    for echelle, liste in lignes:
        x = MARGE
        for nom, im in liste:
            w = cote * echelle
            planche.paste(sur_fond(im).resize((w, w), Image.NEAREST), (x, y + 16))
            d.text((x + 2, y + 2), "%s ×%d" % (nom, echelle), fill=(255, 220, 120))
            x += cote * 4 + MARGE
        y += cote * echelle + 22 + MARGE
    a.sortie = Path(a.sortie)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    planche.save(a.sortie)
    print(a.sortie)


if __name__ == "__main__":
    main()
