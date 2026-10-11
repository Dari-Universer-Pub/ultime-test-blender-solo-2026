"""
ancre.py - ancre de métal (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : tige, anneau, traverse et deux pattes. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/ancre.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "ancre"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_fer = ob.materiau("ancre_fer", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    ob.cylindre((0.0, 0.0, -0.05), 0.06, 1.1, m_fer, nom="tige")
    ob.tore((0.0, 0.0, 0.62), 0.12, 0.035, m_fer, rotation=(math.pi / 2, 0.0, 0.0), nom="anneau")
    ob.cylindre((0.0, 0.0, 0.42), 0.045, 0.6, m_fer, rotation=(0.0, math.pi / 2, 0.0), nom="traverse")
    for k, s in enumerate((-1, 1)):
        ob.cone((0.22 * s, 0.0, -0.46), 0.14, 0.42, m_fer, rotation=(0.0, math.radians(-50 * s), 0.0), nom=f"patte_{k + 1}")



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
