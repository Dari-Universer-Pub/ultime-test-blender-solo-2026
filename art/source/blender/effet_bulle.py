"""
effet_bulle.py - bulle d'eau (effet, M3), construit dans Blender.

Pièces : une bulle claire avec reflet. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_bulle.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_bulle"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.2


def construire():
    m_b = ob.materiau("bulle_m", "bulle", bandes=(2, 3, 4, 4), rugosite=0.2)
    ob.sphere((0.0, 0.0, 0.0), 0.38, m_b, nom="bulle")
    ob.sphere((-0.12, -0.2, 0.14), 0.07, m_b, nom="reflet")



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
