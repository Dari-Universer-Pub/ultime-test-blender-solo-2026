#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pixeliser.py - reduit un RENDU Blender au pixel art du projet.

    python3 tools/pixelisation/pixeliser.py art/rendu/plongeur art/pixel/plongeur
    options : --facteur 8  --seuil 0.5  --sans-contour  --palette art/palette.json

Etapes, dans cet ordre (les memes pour tous les assets, voir STYLE.md) :
  1. reduction : un bloc de FACTEUR x FACTEUR pixels du rendu donne UN pixel (moyenne pre-multipliee) ;
  2. seuil d'alpha : chaque pixel est soit opaque (255) soit transparent (0), jamais entre les deux ;
  3. quantification : chaque pixel opaque prend le ton de la palette le plus proche (espace Lab),
     sauf les rampes de contour, reservees au contour ;
  4. contour selectif : le bord qui regarde le haut-gauche (lumiere) prend le contour chaud,
     le bord qui regarde le bas-droite prend le contour sombre ;
  5. nettoyage : un pixel opaque sans voisin opaque (haut, bas, gauche, droite) est retire.

Outil de PIXELISATION (autorise par AGENTS.md) : il reduit et quantifie un rendu. Il ne dessine rien.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Reglages communs (repris dans STYLE.md)
FACTEUR = 8                # rendu 512 px -> 64 px
SEUIL_ALPHA = 0.5          # alpha moyen >= 0.5 : pixel opaque
RAMPES_CONTOUR = ("contour_sombre", "contour_chaud")
CONTOUR_CHAUD = ("contour_chaud", 2)      # bord eclaire (haut-gauche)
CONTOUR_SOMBRE = ("contour_sombre", 1)    # bord dans l'ombre (bas-droite)


def hex_rgb(s):
    s = s.lstrip("#")
    return [int(s[i:i + 2], 16) for i in (0, 2, 4)]


def rgb_vers_lab(rgb):
    """rgb : tableau (..., 3) de 0 a 1 (sRGB). Renvoie du Lab (CIE, illuminant D65)."""
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805],
                  [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16.0 / 116.0)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def charger_palette(chemin):
    rampes = json.load(open(chemin, encoding="utf-8"))["rampes"]
    corps, contour = [], {}
    for nom, tons in rampes.items():
        rgb = [hex_rgb(t) for t in tons]
        if nom in RAMPES_CONTOUR:
            contour[nom] = rgb
        else:
            corps.extend(rgb)
    tous = corps + [c for r in contour.values() for c in r]
    return np.array(corps, dtype=np.uint8), contour, tous


def reduire(rgba):
    """rgba : (H, W, 4) en 0..1. Renvoie (h, w, 4) : moyenne pre-multipliee par blocs de FACTEUR."""
    h, w = rgba.shape[0] // FACTEUR, rgba.shape[1] // FACTEUR
    bloc = rgba[:h * FACTEUR, :w * FACTEUR].reshape(h, FACTEUR, w, FACTEUR, 4)
    a = bloc[..., 3].mean(axis=(1, 3))
    premul = (bloc[..., :3] * bloc[..., 3:4]).mean(axis=(1, 3))
    rgb = np.where(a[..., None] > 0, premul / np.maximum(a[..., None], 1e-6), 0.0)
    return np.concatenate([rgb, a[..., None]], axis=-1)


def voisins4(masque):
    p = np.pad(masque, 1, constant_values=False)
    return p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]   # haut, bas, gauche, droite


def pixeliser(entree, sortie, palette_chemin, sans_contour):
    corps, contour, _ = charger_palette(palette_chemin)
    corps_lab = rgb_vers_lab(corps / 255.0)
    im = np.asarray(Image.open(entree).convert("RGBA"), dtype=np.float64) / 255.0
    petit = reduire(im)
    h, w = petit.shape[:2]
    opaque = petit[..., 3] >= SEUIL_ALPHA

    # quantification des pixels opaques (Lab, plus proche voisin)
    lab = rgb_vers_lab(np.clip(petit[..., :3], 0, 1))
    flat = lab.reshape(-1, 3)
    dist = ((flat[:, None, :] - corps_lab[None, :, :]) ** 2).sum(axis=2)
    proche = corps[dist.argmin(axis=1)].reshape(h, w, 3)
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[opaque, :3] = proche[opaque]
    out[opaque, 3] = 255

    # contour selectif (1 pixel, a l'exterieur de la silhouette)
    if not sans_contour and contour:
        haut, bas, gauche, droite = voisins4(opaque)
        ch = np.pad(opaque, 1, constant_values=False)
        bord = np.zeros_like(opaque)
        cote = np.zeros((h, w), dtype=np.float64)     # > 0 : la matiere est en bas-droite (bord eclaire)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                voisin = ch[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
                bord |= voisin & ~opaque
                cote += voisin * (dx + dy)
        bord &= ~opaque
        ch_rgb = np.array(contour[CONTOUR_CHAUD[0]][CONTOUR_CHAUD[1]], dtype=np.uint8)
        sb_rgb = np.array(contour[CONTOUR_SOMBRE[0]][CONTOUR_SOMBRE[1]], dtype=np.uint8)
        eclaire = bord & (cote > 0)
        ombre = bord & (cote <= 0)
        out[eclaire, :3] = ch_rgb
        out[ombre, :3] = sb_rgb
        out[bord, 3] = 255
        opaque = opaque | bord

    # nettoyage : pixel opaque isole (aucun voisin opaque) retire
    haut, bas, gauche, droite = voisins4(opaque)
    isole = opaque & ~(haut | bas | gauche | droite)
    out[isole] = 0
    opaque = opaque & ~isole

    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    if os.path.exists(sortie):
        os.remove(sortie)
    Image.fromarray(out, "RGBA").save(sortie)
    return opaque


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entree")
    ap.add_argument("sortie")
    ap.add_argument("--facteur", type=int, default=FACTEUR)
    ap.add_argument("--seuil", type=float, default=SEUIL_ALPHA)
    ap.add_argument("--sans-contour", action="store_true")
    ap.add_argument("--palette", default=os.path.join(RACINE, "art", "palette.json"))
    ap.add_argument("--prefixe", default="")
    a = ap.parse_args()
    globals()["FACTEUR"] = a.facteur
    globals()["SEUIL_ALPHA"] = a.seuil
    fichiers = sorted(f for f in os.listdir(a.entree) if f.endswith(".png") and f.startswith(a.prefixe))
    if not fichiers:
        print("aucun rendu PNG dans", a.entree)
        return 1
    for f in fichiers:
        ent = os.path.join(a.entree, f)
        sort = os.path.join(a.sortie, f)
        masque = pixeliser(ent, sort, a.palette, a.sans_contour)
        ys, xs = np.nonzero(masque)
        hauteur = (ys.max() - ys.min() + 1) if len(ys) else 0
        print(f"{f} : {masque.shape[1]}x{masque.shape[0]} px, silhouette {hauteur} px de haut")
    return 0


if __name__ == "__main__":
    sys.exit(main())
