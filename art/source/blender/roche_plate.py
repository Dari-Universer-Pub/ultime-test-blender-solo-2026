"""
roche_plate.py - dalle de roche plate (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : dalle ovale et éclats. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/roche_plate.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "roche_plate"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_r = ob.materiau("dalle_roche", "roche", bandes=(1, 2, 3, 4), rugosite=0.9)
    ob.sphere((0.0, 0.0, 0.0), 0.5, m_r, echelle=(1.0, 0.7, 0.4), nom="dalle")
    ob.sphere((0.3, 0.0, 0.14), 0.12, m_r, echelle=(1.0, 0.6, 0.5), nom="eclat")



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
