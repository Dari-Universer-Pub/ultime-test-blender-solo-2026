#!/usr/bin/env python3
"""membres.py - mesure, image par image, la visibilité des quatre membres du plongeur (carte d'identité).

Entrée : un dossier de rendu produit par `plongeur.py` avec PLONGEUR_IDENTITE=1 :
    identite/nage_01..08.png          image complète, couleurs plates
    parties/<groupe>/nage_01..08.png  chaque groupe seul (les autres faces supprimées)
    identite_palette.json             couleur plate de chaque groupe
La mesure pixelise les deux (même outil que le jeu : tools/pixelisation/pixeliser.py, palette d'identité,
sans contour), puis compte pour chaque membre :
    visible  = pixels de la couleur du membre dans l'image complète
    surface  = pixels du membre quand il est seul (sa surface sans cache)
    non caché = visible / surface
Critère (demande de Julien) : visible >= 20 px ET non caché >= 60 %, sur chaque image.

Usage : python3 tools/mesure/membres.py <dossier_rendu> [--facteur 8]
Sortie : tableau markdown (à coller dans ETAT.md) et code 0 si tout passe, 1 sinon.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PIXELISER = os.path.join(RACINE, "tools", "pixelisation", "pixeliser.py")
# Un membre = son segment principal + son extrémité (gant pour le bras, botte pour la jambe), du même côté.
MEMBRES = {
    "bras_proche": ["bras_proche", "gant_proche"],
    "bras_lointain": ["bras_lointain", "gant_lointain"],
    "jambe_proche": ["jambe_proche", "botte_proche"],
    "jambe_lointaine": ["jambe_lointaine", "botte_lointaine"],
}
IMAGES = [f"nage_{i:02d}.png" for i in range(1, 9)]
MIN_PX, MIN_NON_CACHE = 20, 0.60


def pixeliser(entree, sortie, palette, facteur):
    os.makedirs(sortie, exist_ok=True)
    subprocess.run([sys.executable, PIXELISER, entree, sortie, "--palette", palette, "--sans-contour",
                    "--facteur", str(facteur)], check=True, stdout=subprocess.DEVNULL)


def couleur(palette_json, groupe):
    hexa = json.load(open(palette_json, encoding="utf-8"))["rampes"][groupe][0].lstrip("#")
    return np.array([int(hexa[k:k + 2], 16) for k in (0, 2, 4)])


def opaque_de(chemin):
    return np.asarray(Image.open(chemin).convert("RGBA"))[..., 3] > 0


def compter(chemin, rgb):
    im = np.asarray(Image.open(chemin).convert("RGBA"))
    opaque = im[..., 3] > 0
    egal = (im[..., :3] == rgb).all(axis=2) & opaque
    return int(egal.sum()), int(opaque.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--facteur", type=int, default=8)
    a = ap.parse_args()
    palette = os.path.join(a.dossier, "identite_palette.json")
    pix_id = os.path.join(a.dossier, "pixel_identite")
    pixeliser(os.path.join(a.dossier, "identite"), pix_id, palette, a.facteur)
    groupes = list(json.load(open(palette, encoding="utf-8"))["rampes"].keys())
    for g in groupes:
        pixeliser(os.path.join(a.dossier, "parties", g), os.path.join(a.dossier, "pixel_parties", g), palette, a.facteur)

    echecs = []
    print("| image | " + " | ".join(f"{m} (vis / non caché)" for m in MEMBRES) + " | verdict |")
    print("|---|" + "---|" * len(MEMBRES) + "---|")
    for img in IMAGES:
        cellules, ok = [], True
        for m, groupes_m in MEMBRES.items():
            visible = 0
            surface = None
            for g in groupes_m:
                rgb = couleur(palette, g)
                visible += compter(os.path.join(pix_id, img), rgb)[0]
                masque = opaque_de(os.path.join(a.dossier, "pixel_parties", g, img))
                surface = masque if surface is None else (surface | masque)
            surface = int(surface.sum())
            non_cache = visible / surface if surface else 0.0
            passe = visible >= MIN_PX and non_cache >= MIN_NON_CACHE
            ok = ok and passe
            cellules.append(f"{visible} px / {non_cache * 100:.0f} % {'' if passe else '**KO**'}")
        verdict = "OK" if ok else "ÉCHEC"
        if not ok:
            echecs.append(img)
        print(f"| {img} | " + " | ".join(cellules) + f" | {verdict} |")
    print()
    print("images en échec : " + (", ".join(echecs) if echecs else "aucune"))
    return 0 if not echecs else 1


if __name__ == "__main__":
    sys.exit(main())
