#!/usr/bin/env python3
"""cote_a_cote.py - planche d'une pose du plongeur : la référence, puis une colonne par version (chemin d'une
image de pose), sur eau claire et sur eau sombre (couleurs du dégradé d'eau du jeu), à ×N. Assemble seulement.

Usage : python3 tools/planches/cote_a_cote.py --ref REF.jpg --sortie SORTIE.png --zoom 4 \
            --colonne "profil validé=chemin.png" --colonne "azimut 30=chemin.png" ...
"""
import argparse

from PIL import Image, ImageDraw

EAU = {"eau claire": (42, 138, 160), "eau sombre": (12, 42, 74)}
CASE = 80


def cellule(chemin, fond, zoom):
    img = Image.open(chemin).convert("RGBA")
    grand = Image.new("RGBA", (CASE, CASE), fond + (255,))
    grand.alpha_composite(img, ((CASE - img.width) // 2, (CASE - img.height) // 2))
    return grand.resize((CASE * zoom, CASE * zoom), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("--colonne", action="append", required=True, help="libellé=chemin")
    a = ap.parse_args()
    colonnes = [c.split("=", 1) for c in a.colonne]
    cell = CASE * a.zoom
    marge, titre = 10, 22
    ref = Image.open(a.ref).convert("RGB")
    ref = ref.resize((int(ref.width * cell / ref.height), cell), Image.LANCZOS).convert("RGBA")
    lignes = []
    for nom_eau, fond in EAU.items():
        largeur = ref.width + marge + len(colonnes) * (cell + marge) + marge
        ligne = Image.new("RGBA", (largeur, cell + marge * 2 + titre), (20, 24, 36, 255))
        d = ImageDraw.Draw(ligne)
        d.text((marge, marge), f"référence - {nom_eau}", fill=(230, 230, 230, 255))
        ligne.alpha_composite(ref, (marge, marge + titre))
        x = marge + ref.width + marge
        for libelle, chemin in colonnes:
            d.text((x, marge), f"{libelle} - {nom_eau}", fill=(230, 230, 230, 255))
            ligne.alpha_composite(cellule(chemin, fond, a.zoom), (x, marge + titre))
            x += cell + marge
        lignes.append(ligne)
    planche = Image.new("RGBA", (max(l.width for l in lignes), sum(l.height for l in lignes)), (20, 24, 36, 255))
    y = 0
    for l in lignes:
        planche.alpha_composite(l, (0, y))
        y += l.height
    planche.convert("RGB").save(a.sortie)
    print("planche :", a.sortie, planche.size)


if __name__ == "__main__":
    main()
