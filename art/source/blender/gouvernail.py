"""
gouvernail.py - gouvernail de barque (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : barre de bois et pale plate. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/gouvernail.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "gouvernail"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.2


def construire():
    m_bois = ob.materiau("gouvernail_bois", "ocre", bandes=(1, 2, 3, 4), rugosite=0.8)
    m_fer = ob.materiau("gouvernail_fer", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    ob.cube((0.0, 0.0, 0.0), 1.0, m_bois, echelle=(0.12, 0.12, 0.9), nom="barre")
    ob.cube((0.0, 0.0, -0.4), 1.0, m_fer, echelle=(0.5, 0.06, 0.26), nom="pale")



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
