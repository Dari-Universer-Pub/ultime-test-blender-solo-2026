"""
fond_rayons_lumiere.py - rayons de lumière (fond, biome recif_peu_profond, M3), construit dans Blender.

Plan large 640 x 360 (16:9), couches de silhouettes : faisceaux obliques clairs. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/fond_rayons_lumiere.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "fond_rayons_lumiere"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES_X, RES_Y = 640, 360
ECHANTILLONS = int(os.environ.get("FOND_ECHANTILLONS", "32"))
LARGEUR_CADRE = 8.0


def construire():
    m_rayon = ob.materiau("fond_rayon", "bulle", bandes=(3, 4, 4, 4), rugosite=0.2)
    for k, x in enumerate((-2.4, -0.8, 0.8, 2.4)):
        ob.cylindre((x, 0.5, 0.5), 0.12, 3.6, m_rayon, rotation=(0.0, math.radians(-18), 0.0), nom=f"rayon_{k + 1}")



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
