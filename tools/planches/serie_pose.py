#!/usr/bin/env python3
"""serie_pose.py - planche d'une série d'images du plongeur : pour chaque eau (claire, sombre), une ligne
« avant » (version précédente) et une ligne « après » (version nouvelle), une colonne par image, à côté de la
référence. Assemble seulement : ne dessine aucun personnage.

Usage : python3 tools/planches/serie_pose.py --ref REF.jpg --avant DOSSIER --apres DOSSIER \
            --noms nage_01,nage_02,... --sortie SORTIE.png [--zoom 2]
"""
import argparse
import os

from PIL import Image, ImageDraw

EAU = {"eau claire": (42, 138, 160), "eau sombre": (12, 42, 74)}
CASE = 80          # cellule de chaque image (case du jeu)


def cellule(chemin, fond, zoom):
    img = Image.open(chemin).convert("RGBA")
    grand = Image.new("RGBA", (CASE, CASE), fond + (255,))
    ox, oy = (CASE - img.width) // 2, (CASE - img.height) // 2
    fond_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fond_img.alpha_composite(img)
    grand.alpha_composite(fond_img, (ox, oy))
    return grand.resize((CASE * zoom, CASE * zoom), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--avant", required=True)
    ap.add_argument("--apres", required=True)
    ap.add_argument("--noms", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    noms = [n.strip() for n in a.noms.split(",") if n.strip()]

    marge, titre = 10, 20
    cell = CASE * a.zoom
    ref = Image.open(a.ref).convert("RGB")
    ref = ref.resize((int(ref.width * cell / ref.height), cell), Image.LANCZOS)
    lignes = []
    for nom_eau, fond in EAU.items():
        for libelle, dossier in (("avant", a.avant), ("apres", a.apres)):
            cols = [cellule(os.path.join(dossier, n + ".png"), fond, a.zoom) for n in noms]
            largeur = ref.width + marge + len(cols) * (cell + marge) + marge
            ligne = Image.new("RGBA", (largeur, cell + marge * 2 + titre), (20, 24, 36, 255))
            d = ImageDraw.Draw(ligne)
            d.text((marge, marge), f"{libelle} - {nom_eau}", fill=(230, 230, 230, 255))
            ligne.alpha_composite(ref.convert("RGBA"), (marge, marge + titre))
            x = marge + ref.width + marge
            for c in cols:
                ligne.alpha_composite(c, (x, marge + titre))
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
