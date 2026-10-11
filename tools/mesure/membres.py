#!/usr/bin/env python3
"""membres.py - mesure, image par image, la visibilité des quatre membres du plongeur (carte d'identité).

Entrée : un dossier de rendu produit par le script du plongeur avec PLONGEUR_IDENTITE=1 :
    identite/<image>.png              image complète, couleurs plates (une couleur par partie)
    parties/<groupe>/<image>.png      chaque groupe seul (les autres faces supprimées)
    identite_palette.json             couleur plate de chaque groupe

Réduction : BLOC MAJORITAIRE. Un pixel de la case (80 px) prend la partie majoritaire de son bloc
(8 x 8 px du rendu 640). Une couleur plate reste exacte, et les bords entre deux parties ne créent
pas de partie fantôme (une moyenne de couleurs ferait exactement cela).

Pour chaque membre (segment + extrémité du même côté) :
    visible  = blocs où le membre est la partie majoritaire, dans l'image complète
    surface  = blocs du membre quand il est seul (sa surface sans cache)
    non caché = visible / surface
Critère (demande de Julien) : visible >= 20 px ET non caché >= 60 %, sur chaque image.

Usage :
    python3 tools/mesure/membres.py <dossier_rendu> [--facteur 8] [--groupe nage|idle]
        [--cote-proche g|d]     modèle v3 (noms bras_g, bras_d, ...) : côté le plus proche de la caméra
Sortie : tableau markdown (à coller dans ETAT.md) ; code 0 si toutes les images passent, 1 sinon.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

# Modèle de profil (plongeur.py) : noms de groupes fixes.
MEMBRES = {
    "bras_proche": ["bras_proche", "gant_proche"],
    "bras_lointain": ["bras_lointain", "gant_lointain"],
    "jambe_proche": ["jambe_proche", "botte_proche"],
    "jambe_lointaine": ["jambe_lointaine", "botte_lointaine"],
}
PREFIXES = {"nage": 8, "idle": 6}
MIN_PX, MIN_NON_CACHE = 20, 0.60


def couleur(palette, groupe):
    hexa = palette[groupe][0].lstrip("#")
    return tuple(int(hexa[k:k + 2], 16) for k in (0, 2, 4))


def etiquettes(chemin, couleurs, facteur):
    """Étiquette majoritaire de chaque bloc : indice du groupe dans `noms` (-1 si aucune majorité)."""
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
    return np.where(comptes.max(axis=0) > facteur * facteur / 2, etiq, -1), noms


def surface_seule(chemin, facteur):
    """Blocs où la partie seule est majoritaire (partie seule : tout pixel opaque est cette partie)."""
    arr = np.asarray(Image.open(chemin).convert("RGBA"))
    h, w = arr.shape[0] // facteur * facteur, arr.shape[1] // facteur * facteur
    arr = arr[:h, :w]
    bh, bw = h // facteur, w // facteur
    return (arr[..., 3] > 0).reshape(bh, facteur, bw, facteur).sum(axis=(1, 3)) > facteur * facteur / 2


def membres_pour(cote_proche):
    if not cote_proche:
        return MEMBRES
    loin = "d" if cote_proche == "g" else "g"
    return {
        "bras_proche": [f"bras_{cote_proche}", f"gant_{cote_proche}"],
        "bras_lointain": [f"bras_{loin}", f"gant_{loin}"],
        "jambe_proche": [f"jambe_{cote_proche}", f"botte_{cote_proche}"],
        "jambe_lointaine": [f"jambe_{loin}", f"botte_{loin}"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--facteur", type=int, default=8)
    ap.add_argument("--groupe", choices=sorted(PREFIXES), default="nage")
    ap.add_argument("--cote-proche", choices=["g", "d"], default=None)
    a = ap.parse_args()
    membres = membres_pour(a.cote_proche)
    palette = json.load(open(os.path.join(a.dossier, "identite_palette.json"), encoding="utf-8"))["rampes"]
    couleurs = {g: couleur(palette, g) for g in palette}
    images = [f"{a.groupe}_{i:02d}.png" for i in range(1, PREFIXES[a.groupe] + 1)]

    echecs = []
    print("| image | " + " | ".join(f"{m} (vis / non caché)" for m in membres) + " | verdict |")
    print("|---|" + "---|" * len(membres) + "---|")
    for img in images:
        etiq, noms = etiquettes(os.path.join(a.dossier, "identite", img), couleurs, a.facteur)
        cellules, ok = [], True
        for m, groupes in membres.items():
            visible = int(sum((etiq == noms.index(g)).sum() for g in groupes))
            surface = None
            for g in groupes:
                s = surface_seule(os.path.join(a.dossier, "parties", g, img), a.facteur)
                surface = s if surface is None else (surface | s)
            surface_n = int(surface.sum())
            non_cache = visible / surface_n if surface_n else 0.0
            passe = visible >= MIN_PX and non_cache >= MIN_NON_CACHE
            ok = ok and passe
            cellules.append(f"{visible} px / {non_cache * 100:.0f} % {'' if passe else '**KO**'}")
        if not ok:
            echecs.append(img)
        print(f"| {img} | " + " | ".join(cellules) + f" | {'OK' if ok else 'ÉCHEC'} |")
    print()
    print("images en échec : " + (", ".join(echecs) if echecs else "aucune"))
    return 0 if not echecs else 1


if __name__ == "__main__":
    sys.exit(main())
