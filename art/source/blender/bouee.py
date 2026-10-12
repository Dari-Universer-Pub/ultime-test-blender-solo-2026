"""
bouee.py - bouée de sauvetage (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : anneau orange et anneau blanc. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/bouee.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "bouee"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_orange = ob.materiau("bouee_orange", "palmes", bandes=(2, 3, 4, 4), rugosite=0.5)
    ob.tore((0.0, 0.0, 0.0), 0.32, 0.12, m_orange, rotation=(math.pi / 2, 0.0, 0.0), nom="anneau")



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
