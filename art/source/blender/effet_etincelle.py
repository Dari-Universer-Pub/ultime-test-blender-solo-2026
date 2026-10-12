"""
effet_etincelle.py - étincelle (effet, M3), construit dans Blender.

Pièces : croix de pointes lumineuses. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_etincelle.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_etincelle"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.4


def construire():
    m_l = ob.materiau("etincelle_m", "lampe", bandes=(2, 3, 4, 4), rugosite=0.2)
    for k in range(4):
        a = k * math.pi / 4
        ob.cone((0.0, 0.0, 0.0), 0.07, 0.8, m_l, rotation=(0.0, a, 0.0), nom=f"pointe_{k + 1}")



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
