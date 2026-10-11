"""
corail_branche.py - corail branchu du récif (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : cinq branches coniques rayonnantes. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/corail_branche.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "corail_branche"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_c = ob.materiau("corail_branche_m", "recif", bandes=(1, 2, 3, 4), rugosite=0.6)
    for k in range(5):
        a = (k - 2) * 0.42
        ob.cone((math.sin(a) * 0.22, 0.0, -0.22 + 0.22 * math.cos(a)), 0.10, 0.5, m_c, rotation=(0.0, a, 0.0), nom=f"branche_{k + 1}")



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
