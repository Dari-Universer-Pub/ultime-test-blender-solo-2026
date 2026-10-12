#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_nage.py - planche de revue d'une animation : l'ancre idle à gauche, puis les images de nage,
en quatre fonds (eau claire, eau sombre, damier, niveaux de gris), à ×4, avec les mesures et les écarts.

    python3 tools/planches/planche_nage.py ANCRE.png DOSSIER_NAGE MESURES.txt SORTIE.png [--echelle 4]
        [--motif "nage_*.png"] [--libelle nage] [--titre "Mesures et écarts (nage) : lignes ci-dessous"]

DOSSIER_NAGE contient nage_01.png ... nage_08.png (112 x 112) ; --motif choisit d'autres fichiers (ex. idle_*.png),
--libelle et --titre nomment les colonnes et la ligne de mesures. Outil d'ASSEMBLAGE : il ne dessine rien.
Affiche le SHA-256 de la planche.
"""
import argparse
import glob
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

FONDS = [("eau claire", (64, 140, 170, 255)), ("eau sombre", (14, 32, 52, 255)), ("damier", None),
         ("niveaux de gris", "gris")]
MARGE = 12
ETIQUETTE = 18


def damier(taille, pas=8):
    im = Image.new("RGBA", (taille, taille), (200, 200, 200, 255))
    fonce = Image.new("RGBA", (pas, pas), (150, 150, 150, 255))
    for y in range(0, taille, pas):
        for x in range(0, taille, pas):
            if ((x // pas) + (y // pas)) % 2:
                im.paste(fonce, (x, y))
    return im


def cadre(sprite, fond, taille):
    if fond is None:
        base = damier(taille)
    elif fond == "gris":
        base = Image.new("RGBA", (taille, taille), (128, 128, 128, 255))
        g = sprite.convert("LA")
        sprite = Image.merge("RGBA", (g.split()[0], g.split()[0], g.split()[0], g.split()[1]))
    else:
        base = Image.new("RGBA", (taille, taille), fond)
    base.alpha_composite(sprite.resize((taille, taille), Image.NEAREST))
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ancre")
    ap.add_argument("dossier")
    ap.add_argument("mesures")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=4)
    ap.add_argument("--motif", default="nage_*.png")
    ap.add_argument("--libelle", default="nage")
    ap.add_argument("--titre", default="Mesures et écarts (nage) : lignes ci-dessous")
    args = ap.parse_args()
    taille = 112 * args.echelle
    ancre = Image.open(args.ancre).convert("RGBA")
    images = [Image.open(f).convert("RGBA") for f in sorted(glob.glob(args.dossier + "/" + args.motif))]
    lignes = [t.rstrip() for t in Path(args.mesures).read_text(encoding="utf-8").splitlines() if t.strip()]
    colonnes = 1 + len(images)
    rangees = len(FONDS)
    w = colonnes * taille + (colonnes + 1) * MARGE
    h = rangees * (taille + ETIQUETTE + MARGE) + MARGE + 22 + 15 * len(lignes) + MARGE
    planche = Image.new("RGBA", (w, h), (28, 28, 28, 255))
    d = ImageDraw.Draw(planche)
    for r, (nom, fond) in enumerate(FONDS):
        y = MARGE + r * (taille + ETIQUETTE + MARGE)
        for c in range(colonnes):
            x = MARGE + c * (taille + MARGE)
            sprite = ancre if c == 0 else images[c - 1]
            titre = "ancre idle" if c == 0 else "%s %d" % (args.libelle, c)
            if r == 0:
                d.text((x, y - 1), titre, fill=(230, 230, 230, 255))
            planche.alpha_composite(cadre(sprite, fond, taille), (x, y + ETIQUETTE))
        d.text((MARGE, y + ETIQUETTE + 2), "", fill=(0, 0, 0, 0))
    y = MARGE + rangees * (taille + ETIQUETTE + MARGE)
    d.text((MARGE, y), args.titre, fill=(255, 220, 120, 255))
    for k, t in enumerate(lignes):
        d.text((MARGE, y + 22 + 15 * k), t, fill=(235, 235, 235, 255))
    planche.convert("RGB").save(args.sortie)
    print("planche :", args.sortie)
    print("image_sha256 :", hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
