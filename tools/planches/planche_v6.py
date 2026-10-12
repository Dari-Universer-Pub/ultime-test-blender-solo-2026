#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planche_v6.py - planche de revue du héros v6 : références actuelles | aperçu actuel | aperçu précédent,
puis le bloc de mesures et d'écarts, lu sur la planche elle-même.

    python3 tools/planches/planche_v6.py REF1.jpg REF2.jpg V6.png V5.png MESURES.txt SORTIE.png [--echelle 4]

MESURES.txt : une ligne par mesure ou écart (police par défaut : pas d'accents, pas de symboles).
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
    base = damier(taille, taille) if fond is None else Image.new("RGBA", (taille, taille), fond)
    base.alpha_composite(sprite.resize((taille, taille), Image.NEAREST))
    return base


def reference(chemin, taille):
    """Référence photographique : réduite pour tenir dans la case, sur fond neutre."""
    base = Image.new("RGBA", (taille, taille), (30, 30, 34, 255))
    im = Image.open(chemin).convert("RGBA")
    im.thumbnail((taille - 2 * MARGE, taille - 2 * MARGE), Image.LANCZOS)
    base.alpha_composite(im, ((taille - im.width) // 2, (taille - im.height) // 2))
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref1")
    ap.add_argument("ref2")
    ap.add_argument("v6")
    ap.add_argument("v5")
    ap.add_argument("mesures")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=4)
    args = ap.parse_args()

    taille = 112 * args.echelle
    v6 = Image.open(args.v6).convert("RGBA")
    v5 = Image.open(args.v5).convert("RGBA")
    if v6.size != (112, 112) or v5.size != (112, 112):
        raise SystemExit("les sprites doivent faire 112 x 112")
    lignes_texte = [t.rstrip() for t in Path(args.mesures).read_text(encoding="utf-8").splitlines() if t.strip()]

    panneaux = [
        ("reference 1951 (Stockholm, Wikimedia)", reference(args.ref1, taille)),
        ("reference 1970 (USF, Gandy)", reference(args.ref2, taille)),
        ("v6 actuel, eau claire (x4)", sur_fond(v6, EAU_CLAIRE, taille)),
        ("v6 actuel, eau sombre (x4)", sur_fond(v6, EAU_SOMBRE, taille)),
        ("v6 actuel, damier (x4)", sur_fond(v6, None, taille)),
        ("v5 precedent (x4), eau claire", sur_fond(v5, EAU_CLAIRE, taille)),
    ]
    colonnes = 3
    hauteur_texte = 24 + 15 * len(lignes_texte) + MARGE
    w = colonnes * taille + (colonnes + 1) * MARGE
    h = 2 * (taille + ETIQUETTE) + (3 * MARGE) + hauteur_texte
    planche = Image.new("RGBA", (w, h), (28, 28, 28, 255))
    dessin = ImageDraw.Draw(planche)
    for i, (titre, image) in enumerate(panneaux):
        ligne, col = divmod(i, colonnes)
        x = MARGE + col * (taille + MARGE)
        y = MARGE + ligne * (taille + ETIQUETTE + MARGE)
        dessin.text((x, y + 4), titre, fill=(230, 230, 230, 255))
        planche.alpha_composite(image, (x, y + ETIQUETTE))
    y = MARGE + 2 * (taille + ETIQUETTE + MARGE)
    dessin.text((MARGE, y), "Mesures et ecarts (objectifs chiffres : voir ETAT.md)", fill=(255, 220, 120, 255))
    for k, texte in enumerate(lignes_texte):
        dessin.text((MARGE, y + 24 + 15 * k), texte, fill=(235, 235, 235, 255))
    planche.convert("RGB").save(args.sortie)
    print("planche :", args.sortie)
    print("image_sha256 :", hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
