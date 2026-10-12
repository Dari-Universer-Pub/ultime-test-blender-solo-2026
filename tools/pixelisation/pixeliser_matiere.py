#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pixeliser_matiere.py - pixelisation d'un RENDU Blender PILOTÉE PAR MATIÈRE (plongeur v4).

    python3 tools/pixelisation/pixeliser_matiere.py <dossier_rendu> <dossier_identite> <sortie>
        --palette art/palette_plongeur_v4_matiere.json [--facteur 4]

<dossier_rendu>   : idle_01.png en couleurs (rendu à 4 fois la taille cible, sans flou)
<dossier_identite>: le dossier produit par le script du plongeur (PLONGEUR_IDENTITE=1) : matiere/,
                    identite/ (groupes des membres) et les deux palettes JSON à sa racine.

Étapes :
  1. réduction : la COULEUR se moyenne par bloc (FACTEUR x FACTEUR) ; la MATIÈRE et le GROUPE se
     prennent à la MAJORITÉ du bloc (jamais de mélange d'identités) ;
  2. quantification par matière : chaque pixel prend le ton de SA rampe, choisi sur la luminance (L*)
     seule : aucune dérive de teinte ni de matière possible ;
  3. contour sombre sélectif sur la silhouette (côté ombre seulement, pas de trait côté lumière) ;
  4. contour interne d'1 px entre deux matières ou deux groupes différents, calculé depuis la carte ;
  5. nettoyage : un pixel sans voisin de même couleur prend la couleur majoritaire de ses voisins ;
  6. mesures : pixels isolés avant/après, nombre de couleurs, hauteur de la silhouette.

Outil de PIXELISATION (autorisé par AGENTS.md) : il réduit et quantifie un rendu, il ne dessine pas.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

CONTOUR_SILHOUETTE = ("contour", 0)
CONTOUR_INTERNE = ("contour", 1)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[k:k + 2], 16) for k in (0, 2, 4)], dtype=np.float64) / 255.0


def luminance_l(rgb):
    """L* (CIE) d'une couleur sRGB 0..1 (tableau (..., 3))."""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    return np.where(y > 0.008856, 116.0 * np.cbrt(y) - 16.0, 903.3 * y)


def lire_etiquettes(chemin_image, palette_json):
    """Étiquette (indice de la liste) de chaque pixel dont la couleur plate est dans la palette ; -1 sinon."""
    couleurs = json.load(open(palette_json, encoding="utf-8"))["rampes"]
    noms = list(couleurs)
    arr = np.asarray(Image.open(chemin_image).convert("RGBA"))
    etiq = np.full(arr.shape[:2], -1, dtype=np.int32)
    for i, nom in enumerate(noms):
        c = (np.array([int(couleurs[nom][0].lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)], dtype=np.uint8))
        m = (arr[..., :3] == c).all(axis=2) & (arr[..., 3] > 0)
        etiq[m] = i
    return etiq, noms


def majorite_par_bloc(etiq, f):
    """Étiquette majoritaire de chaque bloc f x f. Un bloc de bord (étiquettes absentes ou partagées) prend
    l'étiquette majoritaire des blocs voisins : jamais de mélange, jamais de trou."""
    h, w = etiq.shape[0] // f, etiq.shape[1] // f
    e = etiq[:h * f, :w * f].reshape(h, f, w, f)
    nb = int(e.max()) + 1
    comptes = np.stack([(e == v).sum(axis=(1, 3)) for v in range(nb)])   # (nb, h, w)
    comptes[0] = 0 if False else comptes[0]
    meilleur = comptes.argmax(axis=0)
    maxi = comptes.max(axis=0)
    maj = np.where(maxi > 0, meilleur, -1)
    # bloc vide : on reprend la majorité d'un voisinage 3 x 3 de blocs étiquetés
    manque = maj < 0
    if manque.any():
        voisin = np.zeros((nb, h, w), dtype=np.int64)
        for k in range(nb):
            pk = np.pad((maj == k).astype(np.int64), 1)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    voisin[k] += pk[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
        remplace = voisin.argmax(axis=0)
        ok = voisin.max(axis=0) > 0
        maj = np.where(manque & ok, remplace, maj)
    return maj


def reduire(rgba, etiq_mat, etiq_grp, f):
    """Couleur moyenne (pré-multipliée) par bloc ; matière et groupe à la majorité."""
    h, w = rgba.shape[0] // f, rgba.shape[1] // f
    bloc = rgba[:h * f, :w * f].reshape(h, f, w, f, 4)
    a = bloc[..., 3].mean(axis=(1, 3))
    premul = (bloc[..., :3] * bloc[..., 3:4]).mean(axis=(1, 3))
    rgb = np.where(a[..., None] > 0, premul / np.maximum(a[..., None], 1e-6), 0.0)
    return rgb, a >= 0.5, majorite_par_bloc(etiq_mat, f), majorite_par_bloc(etiq_grp, f)


def pixeliser(rendu, dossier_identite, palette, facteur):
    rampes = json.load(open(palette, encoding="utf-8"))["rampes"]
    etiq_mat, noms_mat = lire_etiquettes(os.path.join(dossier_identite, "matiere", "idle_01.png"),
                                         os.path.join(dossier_identite, "matiere_palette.json"))
    etiq_grp, _ = lire_etiquettes(os.path.join(dossier_identite, "identite", "idle_01.png"),
                                  os.path.join(dossier_identite, "identite_palette.json"))
    im = np.asarray(Image.open(rendu).convert("RGBA"), dtype=np.float64) / 255.0
    rgb, opaque, mat, grp = reduire(im, etiq_mat, etiq_grp, facteur)
    h, w = opaque.shape

    # 2. quantification par matière : ton de SA rampe, choisi sur L* seul
    sortie = np.zeros((h, w, 3), dtype=np.float64)
    sans_matiere = 0
    lstar_bloc = luminance_l(np.clip(rgb, 0, 1))
    for i, nom in enumerate(noms_mat):
        m = opaque & (mat == i)
        if not m.any():
            continue
        tons = np.array([hex_rgb(t) for t in rampes[nom]])
        lt = luminance_l(tons)
        choix = np.abs(lstar_bloc[m][:, None] - lt[None, :]).argmin(axis=1)
        sortie[m] = tons[choix]
    sans_matiere = int((opaque & (mat < 0)).sum())

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[opaque, :3] = np.round(sortie[opaque] * 255).astype(np.uint8)
    out[opaque, 3] = 255
    contour_s = np.round(hex_rgb(rampes[CONTOUR_SILHOUETTE[0]][CONTOUR_SILHOUETTE[1]]) * 255).astype(np.uint8)
    contour_i = np.round(hex_rgb(rampes[CONTOUR_INTERNE[0]][CONTOUR_INTERNE[1]]) * 255).astype(np.uint8)

    # 3. contour sombre sélectif : silhouette, côté ombre (matière en haut-gauche) seulement
    p = np.pad(opaque, 1, constant_values=False)
    bord = np.zeros((h, w), dtype=bool)
    cote = np.zeros((h, w), dtype=np.float64)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            voisin = p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
            bord |= voisin & ~opaque
            cote += voisin * (dx + dy)
    bord &= ~opaque
    ombre = bord & (cote <= 0)
    out[ombre, :3] = contour_s
    out[ombre, 3] = 255
    opaque = opaque | ombre

    # 4. contour interne : entre deux blocs opaques de matière ou de groupe différents (côté gauche/haut)
    interne = np.zeros((h, w), dtype=bool)
    paires = [
        (opaque[:, :-1] & opaque[:, 1:] & ((mat[:, :-1] != mat[:, 1:]) | (grp[:, :-1] != grp[:, 1:])), (slice(None), slice(None, -1))),
        (opaque[:-1, :] & opaque[1:, :] & ((mat[:-1, :] != mat[1:, :]) | (grp[:-1, :] != grp[1:, :])), (slice(None, -1), slice(None))),
    ]
    for masque, idx in paires:
        interne[idx] |= masque
    interne &= opaque
    out[interne, :3] = contour_i
    out[interne, 3] = 255

    # 5. nettoyage : pixel sans voisin de même couleur -> couleur majoritaire de ses voisins
    isoles_avant = contar_isoles(out)
    for _ in range(10):
        iso = contar_masque(out)
        if not iso.any():
            break
        out = remplacer_isoles(out, iso)
    # reste : pixel sans aucun voisin opaque de même couleur (point de contour flottant) -> retiré
    retires = contar_masque(out)
    out[retires] = 0
    isoles_apres = contar_isoles(out)
    return out, {"isoles_avant": isoles_avant, "isoles_apres": isoles_apres, "retires": int(retires.sum()),
                 "sans_matiere": sans_matiere}


def contar_masque(out):
    """Pixels opaques dont aucun des 4 voisins n'a la même couleur."""
    op = out[..., 3] > 0
    rgb = out[..., :3].astype(np.int32)
    p_op = np.pad(op, 1, constant_values=False)
    p_rgb = np.pad(rgb, ((1, 1), (1, 1), (0, 0)), constant_values=-1)
    h, w = op.shape
    meme = np.zeros((h, w), dtype=bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        vois = p_rgb[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
        meme |= (vois == rgb).all(axis=2)
    return op & ~meme


def contar_isoles(out):
    return int(contar_masque(out).sum())


def remplacer_isoles(out, iso):
    """Pixel isolé -> couleur majoritaire de ses voisins opaques (les 4 voisins d'abord, pour que le
    pixel rejoigne vraiment une couleur voisine)."""
    h, w = iso.shape
    res = out.copy()
    op = out[..., 3] > 0
    for y, x in zip(*np.nonzero(iso)):
        voisins = []
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= y + dy < h and 0 <= x + dx < w and op[y + dy, x + dx]:
                voisins.append(tuple(out[y + dy, x + dx, :3]))
        if voisins:
            res[y, x, :3] = max(set(voisins), key=voisins.count)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu", help="image couleur (idle_01.png), 4 fois la taille cible")
    ap.add_argument("identite", help="dossier de la carte d'identité (matiere/, identite/, JSON)")
    ap.add_argument("sortie", help="image pixelisée de sortie (PNG)")
    ap.add_argument("--palette", default=os.path.join("art", "palette_plongeur_v4_matiere.json"))
    ap.add_argument("--facteur", type=int, default=4)
    a = ap.parse_args()
    out, stats = pixeliser(a.rendu, a.identite, a.palette, a.facteur)
    if os.path.exists(a.sortie):
        os.remove(a.sortie)
    os.makedirs(os.path.dirname(os.path.abspath(a.sortie)), exist_ok=True)
    Image.fromarray(out, "RGBA").save(a.sortie)
    op = out[..., 3] > 0
    ys = np.nonzero(op.any(axis=1))[0]
    hauteur = int(ys.max() - ys.min() + 1) if len(ys) else 0
    couleurs = len({tuple(c) for c in out[op][:, :3]})
    print(f"taille {out.shape[1]}x{out.shape[0]} px ; silhouette {hauteur} px de haut")
    print(f"pixels isolés : avant nettoyage {stats['isoles_avant']}, après {stats['isoles_apres']} "
          f"(dont {stats['retires']} points flottants retirés)")
    print(f"couleurs distinctes dans l'image : {couleurs}")
    print(f"blocs opaques sans matière : {stats['sans_matiere']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
