#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contour_interne.py - trait sombre d'1 px entre deux parties du corps, calculé depuis la CARTE D'IDENTITÉ.

    python3 tools/pixelisation/contour_interne.py <dossier_pixel> <dossier_identite> <dossier_sortie>
        [--facteur 8] [--ton 2]

<dossier_identite> : le dossier identite/ produit par le script du plongeur (PLONGEUR_IDENTITE=1),
                     avec identite_palette.json à son parent. Chaque partie a une couleur plate.
<dossier_pixel>    : les images déjà pixelisées (même grille : le rendu 640 px réduit par FACTEUR).

Règle : un pixel opaque dont le voisin droit ou bas est opaque et d'une AUTRE partie prend la couleur
du contour interne (rampe contour_sombre, ton --ton). Le trait tombe donc à gauche ou en haut de la
frontière, sur la partie de gauche/haut : aucune partie n'est retirée, seule sa bordure est assombrie.
Le contour extérieur reste celui de la pixelisation (contour_chaud / contour_sombre sur le bord).

Contrôle : le script affiche, par image, les pixels opaques de l'image pixelisée hors de la carte
d'identité (le contour extérieur, attendu) et les pixels opaques de la carte absents de l'image
(doit être nul ou presque : sinon la grille ne concorde pas).

Outil de PIXELISATION (autorisé par AGENTS.md) : il lit des cartes et assombrit des bords ; il ne dessine
pas de forme.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PALETTE = os.path.join(RACINE, "art", "palette.json")  # défaut ; --palette pour une autre palette


def lire_palette_identite(dossier_identite):
    """Groupe -> couleur plate (RGB), depuis identite_palette.json du parent."""
    chemin = os.path.join(os.path.dirname(os.path.normpath(dossier_identite)), "identite_palette.json")
    rampes = json.load(open(chemin, encoding="utf-8"))["rampes"]
    couleurs = {}
    for groupe, liste in rampes.items():
        hexa = liste[0].lstrip("#")
        couleurs[groupe] = tuple(int(hexa[k:k + 2], 16) for k in (0, 2, 4))
    return couleurs


def etiquettes(chemin, couleurs, facteur):
    """Étiquette de chaque bloc (indice du groupe, -1 si fond ou pas de majorité), en bloc majoritaire."""
    arr = np.asarray(Image.open(chemin).convert("RGBA"))
    h, w = arr.shape[0] // facteur * facteur, arr.shape[1] // facteur * facteur
    arr = arr[:h, :w]
    bh, bw = h // facteur, w // facteur
    noms = list(couleurs)
    comptes = []
    for nom in noms:
        m = (arr[..., :3] == np.array(couleurs[nom], dtype=np.uint8)).all(axis=2) & (arr[..., 3] > 0)
        comptes.append(m.reshape(bh, facteur, bw, facteur).sum(axis=(1, 3)))
    comptes = np.stack(comptes)
    etiq = comptes.argmax(axis=0)
    etiq = np.where(comptes.max(axis=0) > facteur * facteur / 2, etiq, -1)
    return etiq, noms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier_pixel")
    ap.add_argument("dossier_identite")
    ap.add_argument("dossier_sortie")
    ap.add_argument("--facteur", type=int, default=8)
    ap.add_argument("--ton", type=int, default=2, help="ton de la rampe contour_sombre (0 = le plus sombre)")
    ap.add_argument("--palette", default=PALETTE, help="palette JSON (rampe contour_sombre)")
    a = ap.parse_args()

    palette = json.load(open(a.palette, encoding="utf-8"))
    rampes = palette.get("rampes", palette)
    ton = rampes["contour_sombre"][a.ton].lstrip("#")
    couleur_trait = tuple(int(ton[k:k + 2], 16) for k in (0, 2, 4)) + (255,)

    couleurs = lire_palette_identite(a.dossier_identite)
    os.makedirs(a.dossier_sortie, exist_ok=True)
    for nom in sorted(os.listdir(a.dossier_pixel)):
        if not nom.endswith(".png") or not os.path.exists(os.path.join(a.dossier_identite, nom)):
            continue
        etiq, _ = etiquettes(os.path.join(a.dossier_identite, nom), couleurs, a.facteur)
        image = np.asarray(Image.open(os.path.join(a.dossier_pixel, nom)).convert("RGBA")).copy()
        h, w = image.shape[:2]
        if etiq.shape != (h, w):
            sys.exit(f"grilles différentes pour {nom} : identité {etiq.shape}, image {(h, w)}")
        opaque_id = etiq >= 0
        opaque_img = image[..., 3] >= 128
        print(f"{nom} : contour extérieur (opaque dans l'image seulement) = {int((opaque_img & ~opaque_id).sum())} ;"
              f" absent de l'image = {int((opaque_id & ~opaque_img).sum())}")

        diff = np.zeros((h, w), dtype=bool)
        d_droite = (etiq[:, :-1] >= 0) & (etiq[:, 1:] >= 0) & (etiq[:, :-1] != etiq[:, 1:])
        diff[:, :-1] |= d_droite
        d_bas = (etiq[:-1, :] >= 0) & (etiq[1:, :] >= 0) & (etiq[:-1, :] != etiq[1:, :])
        diff[:-1, :] |= d_bas
        trait = diff & opaque_img
        image[trait] = couleur_trait
        Image.fromarray(image, "RGBA").save(os.path.join(a.dossier_sortie, nom))
        print(f"{nom} : {int(trait.sum())} pixels de contour interne")
    return 0


if __name__ == "__main__":
    sys.exit(main())
