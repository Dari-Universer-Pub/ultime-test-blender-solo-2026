"""
planche_cassee.py - planche cassée (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : planche de bois au bout déchiré. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/planche_cassee.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "planche_cassee"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_bois = ob.materiau("planche_bois", "ocre", bandes=(1, 2, 3, 4), rugosite=0.8)
    ob.cube((0.0, 0.0, 0.0), 1.0, m_bois, echelle=(1.4, 0.3, 0.2), nom="planche")
    ob.cube((0.62, 0.0, 0.0), 1.0, m_bois, echelle=(0.22, 0.3, 0.16), nom="bout_casse")



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
