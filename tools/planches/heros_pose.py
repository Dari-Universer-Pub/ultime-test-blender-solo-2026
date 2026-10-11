#!/usr/bin/env python3
"""heros_pose.py - planche de comparaison d'une pose du plongeur : référence | avant | après, ×N, sur eau claire
et eau sombre (couleurs du dégradé d'eau du jeu). Assemble seulement : ne dessine aucun personnage.

Usage : python3 tools/planches/heros_pose.py --ref REF.jpg --avant AVANT.png --apres APRES.png \
            --sortie SORTIE.png [--zoom 4]
"""
import argparse

from PIL import Image, ImageDraw

EAU = {"eau claire": (42, 138, 160), "eau sombre": (12, 42, 74)}
HAUTEUR_REF = 320


def case(image, fond, zoom):
    img = image.convert("RGBA").resize((image.width * zoom, image.height * zoom), Image.NEAREST)
    cellule = Image.new("RGBA", img.size, fond + (255,))
    cellule.alpha_composite(img)
    return cellule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--avant", required=True)
    ap.add_argument("--apres", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("--lib-avant", dest="lib_avant", default="avant")
    ap.add_argument("--lib-apres", dest="lib_apres", default="apres")
    a = ap.parse_args()

    ref = Image.open(a.ref).convert("RGB")
    ref = ref.resize((int(ref.width * HAUTEUR_REF / ref.height), HAUTEUR_REF), Image.LANCZOS)
    avant = Image.open(a.avant)
    apres = Image.open(a.apres)

    lignes = []
    for nom, fond in EAU.items():
        cellules = [
            ("reference", Image.alpha_composite(Image.new("RGBA", ref.size, (40, 40, 40, 255)), ref.convert("RGBA"))),
            (a.lib_avant, case(avant, fond, a.zoom)),
            (a.lib_apres, case(apres, fond, a.zoom)),
        ]
        hauteur = max(c.height for _, c in cellules)
        marge, titre = 12, 22
        largeur = sum(c.width for _, c in cellules) + marge * (len(cellules) + 1)
        ligne = Image.new("RGBA", (largeur, hauteur + marge * 2 + titre), (20, 24, 36, 255))
        d = ImageDraw.Draw(ligne)
        x = marge
        for lib, c in cellules:
            d.text((x, marge), f"{lib} - {nom}", fill=(230, 230, 230, 255))
            ligne.alpha_composite(c, (x, marge + titre))
            x += c.width + marge
        lignes.append(ligne)

    largeur = max(l.width for l in lignes)
    hauteur = sum(l.height for l in lignes)
    planche = Image.new("RGBA", (largeur, hauteur), (20, 24, 36, 255))
    y = 0
    for l in lignes:
        planche.alpha_composite(l, (0, y))
        y += l.height
    planche.convert("RGB").save(a.sortie)
    print("planche :", a.sortie, planche.size)


if __name__ == "__main__":
    main()
