#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contour_dc.py - contour 1 px et nettoyage des pixels isolés, d'après les cartes d'identité du rendu direct
(méthode Dead Cells : le rendu est déjà à la taille finale, aucune réduction ni quantification ici).

    python3 tools/pixelisation/contour_dc.py RENDU.png MATIERE.png GROUPE.png SORTIE.png [--palette palette.json]

Entrées (même taille, 112 px) :
    RENDU    rendu couleur plat par paliers (plongeur_v5_dc.py)
    MATIERE  carte d'identité des matières (couleurs plates)
    GROUPE   carte d'identité des groupes (couleurs plates)
Règles :
    - Contour de silhouette : un pixel du bord est contour SEULEMENT s'il est côté ombre (voisin hors
      silhouette à droite ou en bas, la lumière vient du haut-gauche). Côté lumière : pas de contour.
    - Contour interne : entre deux pixels voisins de matières ou de groupes différents, 1 px du côté
      bas-droit du bord. Une seule rangée de pixels de contour, jamais plus.
    - Couleur du contour : un ton foncé de la palette (contour, brun très foncé, jamais noir pur).
    - Épaisseur 1 px : un bloc 2 x 2 de contour est aminci (un pixel repasse à la couleur du corps voisin).
    - Pixel isolé (aucun voisin sur 8 de la même couleur) : remplacé par la couleur majoritaire de ses
      8 voisins (ou, sans majorité, par un voisin direct, en second lieu diagonal), en boucle jusqu'à zéro (6 passes au plus).
Sortie : l'image, et à côté un JSON de contrôle (pixels changés, isolés avant/après, couleurs, hauteur).
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

CONTOUR = (0x1F, 0x17, 0x14)     # « contour » de la palette : brun très foncé
VOISINS4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
VOISINS8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]


def charger(chemin):
    return np.asarray(Image.open(chemin).convert("RGBA")).copy()


def identite_plate(arr):
    """Clé entière par pixel (couleur RGB), -1 hors silhouette."""
    cle = (arr[..., 0].astype(np.int64) << 16) | (arr[..., 1].astype(np.int64) << 8) | arr[..., 2].astype(np.int64)
    cle[arr[..., 3] == 0] = -1
    return cle


def contours(corps, matiere, groupe):
    """Masque des pixels de contour : silhouette côté ombre + bords internes entre parties différentes."""
    h, w = corps.shape
    marque = np.zeros((h, w), dtype=bool)
    # silhouette : voisin hors corps à droite (dx=+1) ou en bas (dy=+1)
    for y in range(h):
        for x in range(w):
            if not corps[y, x]:
                continue
            for dy, dx in VOISINS4:
                yy, xx = y + dy, x + dx
                hors = yy < 0 or xx < 0 or yy >= h or xx >= w or not corps[yy, xx]
                if hors and dx + dy >= 1:
                    marque[y, x] = True
    # bords internes : entre deux pixels du corps de matière ou de groupe différents, le pixel bas-droit
    for y in range(h):
        for x in range(w):
            if not corps[y, x]:
                continue
            for dy, dx in ((0, 1), (1, 0)):
                yy, xx = y + dy, x + dx
                if yy >= h or xx >= w or not corps[yy, xx]:
                    continue
                if matiere[y, x] != matiere[yy, xx] or groupe[y, x] != groupe[yy, xx]:
                    marque[yy, xx] = True
    return marque


def isoles(arr, corps):
    """Pixels du corps sans aucun voisin (sur 8) de même couleur."""
    h, w = corps.shape
    cle = identite_plate(arr)
    n = 0
    for y in range(h):
        for x in range(w):
            if not corps[y, x]:
                continue
            voisins = [cle[y + dy, x + dx] for dy, dx in VOISINS8
                       if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]]
            if voisins and cle[y, x] not in voisins:
                n += 1
    return n


def nettoyer(arr, corps, passes=6):
    """Remplace chaque pixel isolé par la couleur majoritaire de ses voisins (sur 8)."""
    h, w = corps.shape
    for _ in range(passes):
        cle = identite_plate(arr)
        changes = 0
        for y in range(h):
            for x in range(w):
                if not corps[y, x]:
                    continue
                voisins = [(y + dy, x + dx) for dy, dx in VOISINS8
                           if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]]
                if not voisins:
                    continue
                valeurs = [cle[v] for v in voisins]
                if cle[y, x] in valeurs:
                    continue
                majo, n = collections.Counter(valeurs).most_common(1)[0]
                if n >= 2:
                    src = voisins[valeurs.index(majo)]
                else:
                    # aucun voisin partagé : on prend le voisin direct (haut, bas, gauche, droite) du corps
                    src = next(((y + dy, x + dx) for dy, dx in VOISINS4 + tuple(VOISINS8)
                                if 0 <= y + dy < h and 0 <= x + dx < w and corps[y + dy, x + dx]), None)
                    if src is None:
                        continue
                arr[y, x, :3] = arr[src[0], src[1], :3]
                changes += 1
        if changes == 0:
            break
    return arr


def amincir(arr, corps, passes=4):
    """Contour à 1 px : dans chaque bloc 2 x 2 de pixels de contour, un pixel repasse à la couleur de son
    voisin de corps le plus fréquent. Ainsi le contour de silhouette et le bord interne ne s'épaississent pas
    l'un l'autre. Renvoie le nombre de blocs restants."""
    h, w = corps.shape
    for _ in range(passes):
        cont = identite_plate(arr) == (CONTOUR[0] << 16 | CONTOUR[1] << 8 | CONTOUR[2])
        restants = 0
        for y in range(h - 1):
            for x in range(w - 1):
                bloc = [(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)]
                if not all(cont[p] for p in bloc):
                    continue
                restants += 1
                cible = bloc[0]
                voisins = [(cible[0] + dy, cible[1] + dx) for dy, dx in VOISINS4
                           if 0 <= cible[0] + dy < h and 0 <= cible[1] + dx < w
                           and corps[cible[0] + dy, cible[1] + dx] and not cont[cible[0] + dy, cible[1] + dx]]
                if voisins:
                    src = voisins[0]
                    arr[cible[0], cible[1], :3] = arr[src[0], src[1], :3]
                    cont[cible] = False
        if restants == 0:
            break
    return arr


def blocs_contour(arr):
    cont = identite_plate(arr) == (CONTOUR[0] << 16 | CONTOUR[1] << 8 | CONTOUR[2])
    return int((cont[:-1, :-1] & cont[1:, :-1] & cont[:-1, 1:] & cont[1:, 1:]).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("matiere")
    ap.add_argument("groupe")
    ap.add_argument("sortie")
    args = ap.parse_args()

    rendu = charger(args.rendu)
    matiere = identite_plate(charger(args.matiere))
    groupe = identite_plate(charger(args.groupe))
    corps = rendu[..., 3] > 0
    if matiere.shape != corps.shape or groupe.shape != corps.shape:
        raise SystemExit("cartes d'identité et rendu de tailles différentes")

    avant_isoles = isoles(rendu, corps)
    sortie = rendu.copy()
    marque = contours(corps, matiere, groupe)
    sortie[marque, :3] = CONTOUR
    sortie = nettoyer(sortie, corps)
    blocs_avant = blocs_contour(sortie)
    sortie = amincir(sortie, corps)
    sortie = nettoyer(sortie, corps)
    apres_isoles = isoles(sortie, corps)

    Image.fromarray(sortie).save(args.sortie)
    diff = (np.abs(sortie.astype(int) - rendu.astype(int)).sum(axis=-1) > 0) & (corps | (rendu[..., 3] > 0))
    ys, xs = np.where(corps)
    controle = {
        "image": Path(args.sortie).name,
        "image_sha256": hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest(),
        "pixels_changes_pct": round(100.0 * diff.sum() / max(1, corps.sum()), 1),
        "isoles_avant": int(avant_isoles),
        "isoles_apres": int(apres_isoles),
        "contour_px": int(marque.sum()),
        "blocs_contour_2x2_avant_amincir": int(blocs_avant),
        "blocs_contour_2x2_apres": int(blocs_contour(sortie)),
        "couleurs": len({tuple(c) for c in sortie[corps][:, :3]}),
        "hauteur_px": int(ys.max() - ys.min() + 1),
        "alpha": sorted(int(v) for v in np.unique(sortie[..., 3])),
    }
    Path(args.sortie).with_suffix(".json").write_text(json.dumps(controle, indent=1, ensure_ascii=False),
                                                     encoding="utf-8")
    print(json.dumps(controle, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
