"""
lanterne.py - lanterne de bord (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : globe lumineux, cage métallique et socle. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/lanterne.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "lanterne"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.6


def construire():
    m_verre = ob.materiau("lanterne_verre", "lampe", bandes=(2, 3, 4, 4), rugosite=0.2)
    m_metal = ob.materiau("lanterne_metal", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    ob.sphere((0.0, 0.0, 0.05), 0.24, m_verre, nom="globe")
    ob.cylindre((0.0, 0.0, -0.32), 0.26, 0.08, m_metal, nom="socle")
    ob.cylindre((0.0, 0.0, 0.42), 0.26, 0.08, m_metal, nom="chapeau")
    ob.cone((0.0, 0.0, 0.62), 0.22, 0.18, m_metal, nom="toit")



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
