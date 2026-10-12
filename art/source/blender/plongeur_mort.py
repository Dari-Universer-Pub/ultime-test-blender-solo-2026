#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plongeur_mort.py - chute du plongeur (mort, 8 images) : le corps entier tourne autour des hanches puis se pose au sol.

    PLONGEUR_MORT=<dossier de sortie> /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_mort.py

Rendu direct du personnage entier (même construction, même caméra, même lumière que plongeur_v6.py) : chaque image
est une rotation de tout le corps autour d'un pivot (hanches) et une translation vers le sol, rendues à 112 px.
Pas de pièce plate ni de rotation de pixels : le corps est tourné dans la scène 3D.
Les angles et translations sont dans MORT_IMAGES ; sortie : mort_<n>.png et mort.json.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plongeur_v6 as P  # noqa: E402

# (angle en degrés, décalage écran x, y en px) : rotation autour des hanches, puis translation
MORT_IMAGES = [
    (0, 0, 0),
    (-15, -2, 0),
    (-35, -5, 1),
    (-55, -9, 3),
    (-72, -13, 6),
    (-84, -17, 10),
    (-88, -19, 9),
    (-90, -19, 9),
]
PIVOT_PX = (56.0, 66.0)     # hanches (px écran) : le corps tourne autour de ce point
SENS = float(os.environ.get("PLONGEUR_MORT_SENS", "-1"))   # -1 : chute vers la gauche (écran)


def main():
    dossier = os.environ.get("PLONGEUR_MORT")
    if not dossier:
        sys.exit("PLONGEUR_MORT absent")
    os.makedirs(dossier, exist_ok=True)
    scene = P.construire_tout()
    meshes = [o for o in scene.objects if o.type == "MESH"]
    base = {o.name: o.matrix_world.copy() for o in meshes}
    R, U, F = P.base_camera()
    pivot = P.monde(PIVOT_PX[0], PIVOT_PX[1], 0.0)
    rapport = []
    for k, (ang, dx, dy) in enumerate(MORT_IMAGES, start=1):
        rot = Matrix.Rotation(SENS * math.radians(ang), 4, F)
        trans = Matrix.Translation(P.decal(dx, dy, 0.0))
        m = trans @ Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot)
        for o in meshes:
            o.matrix_world = m @ base[o.name]
        chemin = os.path.join(dossier, "mort_%d.png" % k)
        P.rendre_fichier(scene, chemin)
        rapport.append({"n": k, "angle_deg": ang, "dx_px": dx, "dy_px": dy, "image": "mort_%d.png" % k})
        print("MORT", k, ang, flush=True)
    for o in meshes:
        o.matrix_world = base[o.name]
    with open(os.path.join(dossier, "mort.json"), "w", encoding="utf-8") as fh:
        json.dump({"pivot_px": PIVOT_PX, "sens": SENS, "images": rapport}, fh, ensure_ascii=False, indent=1)
    print("MORT_OK", flush=True)


if __name__ == "__main__":
    main()
