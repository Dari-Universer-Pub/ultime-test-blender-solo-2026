"""
bitte_amarrage.py - bitte d'amarrage (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : tige verticale et cornes en croix. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/bitte_amarrage.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "bitte_amarrage"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_fer = ob.materiau("bitte_fer", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    ob.cylindre((0.0, 0.0, 0.0), 0.08, 0.6, m_fer, nom="tige")
    ob.cube((0.0, 0.0, 0.22), 1.0, m_fer, echelle=(0.7, 0.07, 0.07), nom="corne_1")
    ob.cube((0.0, 0.0, 0.22), 1.0, m_fer, echelle=(0.07, 0.07, 0.7), nom="corne_2")



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
