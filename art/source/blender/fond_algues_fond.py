"""
fond_algues_fond.py - forêt d'algues de fond (fond, biome recif_peu_profond, M3), construit dans Blender.

Plan large 640 x 360 (16:9), couches de silhouettes : tiges vertes sombres. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/fond_algues_fond.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "fond_algues_fond"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES_X, RES_Y = 640, 360
ECHANTILLONS = int(os.environ.get("FOND_ECHANTILLONS", "32"))
LARGEUR_CADRE = 5.0


def construire():
    m_alg = ob.materiau("fond_algue", "bouteille", bandes=(0, 1, 2, 3), rugosite=0.5)
    for k, x in enumerate((-3.2, -1.6, 0.0, 1.6, 3.2)):
        ob.cylindre((x, 1.0, -0.2), 0.12, 2.4, m_alg, rotation=(0.0, math.radians(4 * (k - 2)), 0.0), nom=f"tige_{k + 1}")



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
