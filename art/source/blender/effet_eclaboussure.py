"""
effet_eclaboussure.py - éclaboussure (effet, M3), construit dans Blender.

Pièces : gouttes rayonnantes. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_eclaboussure.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_eclaboussure"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_b = ob.materiau("eclab_m", "bulle", bandes=(1, 2, 3, 4), rugosite=0.3)
    for k in range(7):
        a = k * 2 * math.pi / 7
        ob.cone((math.cos(a) * 0.45, 0.0, math.sin(a) * 0.45), 0.08, 0.3, m_b, rotation=(0.0, a + math.pi / 2, 0.0), nom=f"goutte_{k + 1}")



def main():
    scene = ob.scene_vide()
    construire()
    ob.eclairer(scene)
    ob.camera(scene, LARGEUR_CADRE, centre=(0.0, 0.0, 0.0))
    ob.reglages(scene, RES, echantillons=ECHANTILLONS)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, ID + ".png")
    scene.render.filepath = chemin
    ob.rendre(scene, chemin)


main()
