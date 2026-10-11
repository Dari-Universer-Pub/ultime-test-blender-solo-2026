"""
conque.py - conque (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : cône enroulé et bouche ronde. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/conque.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "conque"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_c = ob.materiau("conque_m", "recif", bandes=(2, 3, 4, 4), rugosite=0.4)
    ob.cone((0.0, 0.0, 0.0), 0.3, 0.7, m_c, rotation=(0.0, math.radians(90), 0.0), nom="spire")
    ob.sphere((-0.3, 0.0, 0.0), 0.14, m_c, echelle=(0.8, 0.6, 0.9), nom="bouche")



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
