"""
fond_roche_fond.py - roche du fond (fond, biome recif_peu_profond, M3), construit dans Blender.

Plan large 640 x 360 (16:9), couches de silhouettes : blocs de roche sombre au pied. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/fond_roche_fond.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "fond_roche_fond"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES_X, RES_Y = 640, 360
ECHANTILLONS = int(os.environ.get("FOND_ECHANTILLONS", "32"))
LARGEUR_CADRE = 8.0


def construire():
    m_roche = ob.materiau("fond_roche", "roche", bandes=(0, 1, 2, 3), rugosite=0.9)
    for k, x in enumerate((-2.8, -0.8, 1.2, 3.0)):
        ob.sphere((x, 0.8, -1.5), 0.8, m_roche, echelle=(1.4, 0.6, 0.5), nom=f"bloc_{k + 1}")



def main():
    scene = ob.scene_vide()
    construire()
    ob.eclairer(scene)
    ob.camera(scene, LARGEUR_CADRE, centre=(0.0, 0.0, 0.0))
    ob.reglages(scene, RES_X, echantillons=ECHANTILLONS)
    scene.render.resolution_y = RES_Y
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, ID + ".png")
    scene.render.filepath = chemin
    ob.rendre(scene, chemin)


main()
