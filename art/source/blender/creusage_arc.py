#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
creusage_arc.py - effets séparés du creusage (plongeur v6) : arc de mouvement (4 images) et particules d'impact.

    PLONGEUR_ARC=<dossier de sortie> /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/creusage_arc.py

Construit dans Blender, avec la caméra et la lumière du personnage (plongeur_v6.py) :
  - arc : un ruban clair (croissant : épaisseur nulle aux deux bouts, maximale au milieu) posé sur la trajectoire
    de la tête de pioche, de l'armement à l'impact ; 4 images, chacune montre le ruban jusqu'à une fraction plus
    grande de la trajectoire. Sans contour : une seule matière claire (famille « reflet » de la palette).
  - particules : quelques sphères (débris bruns, bulles claires) autour du point d'impact, une image.
Trajectoire : position de la tête de pioche dans chaque pose du lot (chaîne bras droit, pivots de la bibliothèque).
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plongeur_v6 as P  # noqa: E402

RACINE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CREUSAGE = os.path.join(RACINE, "art", "pixel", "plongeur_v6", "creusage")
LOT = os.path.join(CREUSAGE, "lot")
BIBLIO = os.path.join(CREUSAGE, "bibliotheque")
# décalage de la tête par rapport au centre du gant, pour la pioche à 0 degré (mesuré sur la variante +000)
TETE_DECALAGE = (-0.18, -23.08)
ARC_IMAGES = [0.40, 0.62, 0.82, 1.00]     # fraction de la trajectoire dessinée dans chaque image de l'arc
LARGEUR_ARC_PX = 5.0                       # épaisseur maximale du croissant (px à 112), nulle aux deux bouts


def tourner(v, deg):
    """Rotation en coordonnées écran (y vers le bas), même convention que assembleur.tourner_px."""
    t = math.radians(deg)
    dx, dy = v
    return (dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t))


def positions_tete():
    """Position écran (px) de la tête de pioche pour chaque pose du lot, dans l'ordre des images."""
    lib = json.load(open(os.path.join(BIBLIO, "bibliotheque.json"), encoding="utf-8"))
    blocs = json.load(open(os.path.join(BIBLIO, "blocs_main.json"), encoding="utf-8"))
    S = lib["pieces"]["bras_d_haut"]["pivot_px"]
    E0 = lib["capuchons"]["coude_d"]["centre_px"]
    Gp = blocs["pivots_px"]["poignee_gant"]
    Ep = blocs["pivots_px"]["coude"]
    sortie = []
    for nom in sorted(os.listdir(os.path.join(LOT, "poses"))):
        pose = json.load(open(os.path.join(LOT, "poses", nom), encoding="utf-8"))
        a = pose["chaine"]["bras_d"]
        E = (S[0] + tourner((E0[0] - S[0], E0[1] - S[1]), a["haut"])[0],
             S[1] + tourner((E0[0] - S[0], E0[1] - S[1]), a["haut"])[1])
        d = tourner((Gp[0] - Ep[0], Gp[1] - Ep[1]), a["avant"])
        G = (E[0] + d[0], E[1] + d[1])
        h = tourner(TETE_DECALAGE, -pose["chaine"]["bloc_main_d"])
        sortie.append({"pose": nom[:-5], "grip": G, "tete": (G[0] + h[0], G[1] + h[1])})
    return sortie


def catmull(points, n):
    """Courbe lisse passant par les points (Catmull-Rom), n échantillons par segment."""
    out = []
    P_ = [points[0]] + points + [points[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / float(n)
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(tuple(points[-1]))
    return out


def ruban(chemin_px, fraction, mat, nom):
    """Croissant sur une partie de la trajectoire (fraction 0 à 1), épaisseur nulle aux bouts."""
    n = len(chemin_px)
    k_max = max(1, int(round(fraction * (n - 1))))
    pts = chemin_px[:k_max + 1]
    me = bpy.data.meshes.new(nom)
    verts, faces = [], []
    m = len(pts)
    for i, (x, y) in enumerate(pts):
        if i + 1 < m:
            tx, ty = pts[i + 1][0] - x, pts[i + 1][1] - y
        else:
            tx, ty = x - pts[i - 1][0], y - pts[i - 1][1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L, tx / L
        s = i / float(max(1, m - 1))
        w = LARGEUR_ARC_PX * math.sin(math.pi * min(1.0, s + 0.02)) * 0.5
        a = P.monde(x + nx * w, y + ny * w, 0.0)
        b = P.monde(x - nx * w, y - ny * w, 0.0)
        verts += [a, b]
    for i in range(m - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(nom, me)
    o.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(o)
    return o


def sphere(centre, rayon, mat, nom):
    return P.ellipsoide(centre, rayon, (1.0, 1.0, 1.0), mat, nom, niveau=0)


def main():
    dossier = os.environ.get("PLONGEUR_ARC")
    if not dossier:
        sys.exit("PLONGEUR_ARC absent")
    os.makedirs(dossier, exist_ok=True)
    poses = positions_tete()
    # trajectoire : armement -> sommet -> descente -> frappe -> impact
    idx = [i for i, p in enumerate(poses) if p["pose"] in ("02_armement", "03_sommet", "04_descente", "05_frappe",
                                                            "06_impact")]
    points = [poses[i]["tete"] for i in idx]
    chemin = catmull(points, 16)
    chemin_px = chemin
    scene = P.construire_tout()
    for x in scene.objects:
        if x.type == "MESH":
            x.hide_render = True
    mat_arc = P.materiau_plat("arc_clair", "#d8f4fa")   # reflet de la palette, couleur plate (pas d'ombrage)
    resultats = []
    for k, f in enumerate(ARC_IMAGES, start=1):
        o = ruban(chemin_px, f, mat_arc, "arc_%d" % k)
        chemin_png = os.path.join(dossier, "arc_%d.png" % k)
        P.rendre_fichier(scene, chemin_png)
        bpy.data.objects.remove(o, do_unlink=True)
        resultats.append({"image": "arc_%d.png" % k, "fraction": f})
        print("ARC", k, flush=True)
    # particules d'impact : débris bruns et bulles claires autour du point de contact (tête au sol)
    impact = [p for p in poses if p["pose"] == "06_impact"][0]["tete"]
    mat_debris = P.materiau_plat("debris", "#b77a36")   # bois de la palette
    mat_bulle = P.materiau_plat("bulle_claire", "#d8f4fa")
    graines = [(-7.0, -6.0, 0.9, 0), (-4.0, -9.0, 0.7, 0), (-1.0, -5.0, 1.0, 1), (2.5, -8.0, 0.8, 1),
               (5.0, -4.5, 0.7, 0), (-9.0, -2.0, 0.6, 1), (7.5, -10.0, 0.6, 1)]
    crees = []
    for i, (dx, dy, r, genre) in enumerate(graines):
        x, y = impact[0] + dx, impact[1] + dy
        c = P.monde(x, y, 0.0)
        mat = mat_bulle if genre else mat_debris
        crees.append(sphere(c, 0.05 * r + 0.02, mat, "particule_%d" % i))
    chemin_png = os.path.join(dossier, "particules_impact.png")
    P.rendre_fichier(scene, chemin_png)
    resultats.append({"image": "particules_impact.png", "points": len(graines)})
    with open(os.path.join(dossier, "effets.json"), "w", encoding="utf-8") as fh:
        json.dump({"arc_chemin_px": [[round(x, 2), round(y, 2)] for x, y in chemin],
                   "impact_px": [round(impact[0], 2), round(impact[1], 2)], "images": resultats},
                  fh, ensure_ascii=False, indent=1)
    print("EFFETS_OK", flush=True)


if __name__ == "__main__":
    main()
