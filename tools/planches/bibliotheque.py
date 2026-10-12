#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bibliotheque.py - planches de la bibliothèque d'angles du creusage (étape 2) et vérification des jonctions.

    python3 tools/planches/bibliotheque.py DOSSIER_BIBLIO DOSSIER_PIECES SORTIE

DOSSIER_BIBLIO : écrit par plongeur_v6 (PLONGEUR_BIBLIO=...) : bibliotheque.json, variantes/<piece>/<angle>.png,
                 capuchons/<nom>.png. Chaque variante est rendue à 112 px par Blender (rotation autour du pivot),
                 jamais par rotation de pixels.
DOSSIER_PIECES : étape 1 (decoupe_ancre) : pieces/torse.png, pour replacer le torse au repos dans la vérification.

Sorties : planche_<piece>.png (variantes, x3), jonctions.png (bras à 90 degrés, x4 autour de l'épaule et du coude),
rapport.json (trous enclos par jonction, surfaces des variantes).
"""
import argparse
import json
from pathlib import Path
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

ECH_PLANCHE = 3
ECH_JONCTION = 4


def charger(p):
    return np.array(Image.open(p).convert("RGBA"))


def trous_enclos(masque):
    """Pixels transparents non reliés au bord de l'image : ce sont des trous visibles dans la silhouette."""
    h, w = masque.shape
    libre = ~masque
    vus = np.zeros_like(libre)
    file = deque()
    for x in range(w):
        for y in (0, h - 1):
            if libre[y, x] and not vus[y, x]:
                vus[y, x] = True
                file.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if libre[y, x] and not vus[y, x]:
                vus[y, x] = True
                file.append((y, x))
    while file:
        y, x = file.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and libre[ny, nx] and not vus[ny, nx]:
                vus[ny, nx] = True
                file.append((ny, nx))
    return int(np.sum(libre & ~vus))


def planche_piece(dossier, piece, angles, sortie):
    e = ECH_PLANCHE
    w = 112 * e
    colonnes = 6
    rangees = (len(angles) + colonnes - 1) // colonnes
    img = Image.new("RGB", (colonnes * (w + 8) + 8, rangees * (w + 22) + 8), (30, 120, 150))
    d = ImageDraw.Draw(img)
    for i, a in enumerate(angles):
        r, c = divmod(i, colonnes)
        x, y = 8 + c * (w + 8), 8 + r * (w + 22)
        t = Image.open(dossier / "variantes" / piece / ("%+04d.png" % a)).convert("RGBA").resize((w, w), Image.NEAREST)
        img.paste(t, (x, y + 14), t)
        d.text((x + 2, y + 1), "%s %+d deg" % (piece, a), fill=(255, 220, 120))
    img.save(sortie)


def translater(img, dx, dy):
    """Translation entière d'une image 112 x 112 (pixels décalés, aucune rotation ni échelle)."""
    out = np.zeros_like(img)
    h, w = img.shape[:2]
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = img[ys0:ys1, xs0:xs1]
    return out


def composer(couches, fond=None):
    """Empilement de pièces (ordre d'affichage explicite, du fond vers l'avant), sans rotation ni échelle."""
    out = np.zeros((112, 112, 4), dtype=np.uint8) if fond is None else fond.copy()
    for c in couches:
        m = c[..., 3] > 0
        out[m] = c[m]
    return out


def crop_zoom(img, centre, rayon, e=ECH_JONCTION):
    cx, cy = int(round(centre[0])), int(round(centre[1]))
    x0, y0 = max(0, cx - rayon), max(0, cy - rayon)
    x1, y1 = min(112, cx + rayon), min(112, cy + rayon)
    c = Image.fromarray(img[y0:y1, x0:x1]).convert("RGBA")
    fond = Image.new("RGBA", c.size, (30, 120, 150, 255))
    fond.alpha_composite(c)
    return fond.resize((c.size[0] * e, c.size[1] * e), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("biblio")
    ap.add_argument("pieces")
    ap.add_argument("sortie")
    args = ap.parse_args()
    biblio, pieces, sortie = Path(args.biblio), Path(args.pieces), Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    lib = json.loads((biblio / "bibliotheque.json").read_text(encoding="utf-8"))
    angles = lib["angles_deg"]
    rapport = {"angles_deg": angles, "surfaces_px": {}, "trous_enclos": {}}

    for piece in lib["pieces"]:
        planche_piece(biblio, piece, angles, sortie / ("planche_%s.png" % piece))
        rapport["surfaces_px"][piece] = {
            "%+d" % a: int(np.sum(charger(biblio / "variantes" / piece / ("%+04d.png" % a))[..., 3] > 0)) for a in angles}

    # jonctions : bras droit à 90 degrés (haut et avant-bras au même angle, bras tendu).
    # Règle de chaîne : le coude se déplace avec le haut du bras (rotation autour de l'épaule). L'avant-bras et son
    # capuchon, rendus au coude de repos, sont translatés du déplacement du coude (entiers, pas de rotation de pixels).
    torse = charger(pieces / "pieces" / "torse.png")
    S = np.array(lib["pieces"]["bras_d_haut"]["pivot_px"])
    E = np.array(lib["capuchons"]["coude_d"]["centre_px"])
    cap_e = charger(biblio / "capuchons" / "epaule_d.png")
    cap_c = charger(biblio / "capuchons" / "coude_d.png")
    theta = np.radians(90.0)
    dx, dy = E - S
    E_new = S + np.array([dx * np.cos(theta) + dy * np.sin(theta), -dx * np.sin(theta) + dy * np.cos(theta)])
    tx, ty = int(round(E_new[0] - E[0])), int(round(E_new[1] - E[1]))
    haut = charger(biblio / "variantes" / "bras_d_haut" / "+090.png")
    avant = translater(charger(biblio / "variantes" / "bras_d_avant" / "+090.png"), tx, ty)
    cap_c = translater(cap_c, tx, ty)
    membre = composer([cap_e, haut, cap_c, avant])
    rapport["trous_enclos"]["bras_d_90_membre"] = trous_enclos(membre[..., 3] > 0)
    rapport["trous_enclos"]["bras_d_90_sans_capuchons"] = trous_enclos(composer([haut, avant])[..., 3] > 0)
    rapport["coude_translation_px"] = [tx, ty]
    tout = composer([torse, cap_e, haut, cap_c, avant])
    z1 = crop_zoom(tout, S, 18, e=6)
    z2 = crop_zoom(tout, E_new, 18, e=6)
    z3 = crop_zoom(membre, E_new, 18, e=6)
    planche = Image.new("RGB", (z1.size[0] * 3 + 40, z1.size[1] + 40), (28, 28, 28))
    d = ImageDraw.Draw(planche)
    for i, (z, titre) in enumerate(((z1, "epaule (bras a 90)"), (z2, "coude (bras a 90)"),
                                    (z3, "coude : membre seul"))):
        x = 8 + i * (z1.size[0] + 12)
        planche.paste(z.convert("RGB"), (x, 28))
        d.text((x, 10), titre, fill=(255, 220, 120))
    planche.save(sortie / "jonctions.png")
    rapport["regles"] = {
        "rotation": "chaque variante est rendue par Blender, pivotée autour de son pivot de repos ; aucune rotation de pixels",
        "bras": "angle +90 = anti-horaire pour le spectateur depuis le bras pendu (vers la droite)",
        "chaine_coude": "avant-bras et capuchon coude : translation entière (E_nouveau - E_repos), "
                        "E_nouveau = S + rotation(E - S, angle du haut du bras)",
        "pioche": "manche et tête dans la même variante, pivot = poignée (main droite)",
        "capuchons": "épaule r = 0,21 m, coude r = 0,19 m, sphères de même matière, pas de rotation",
        "tete_pioche_repos": {"largeur_px": 12, "hauteur_px": 5, "minimum": "12 x 4 px à ×1"},
    }
    (sortie / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rapport["trous_enclos"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
