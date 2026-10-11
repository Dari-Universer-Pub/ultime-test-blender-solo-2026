"""
coquillage.py - coquillage (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : coque bombée et pointe. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/coquillage.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "coquillage"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_s = ob.materiau("coquillage_coque", "sable", bandes=(1, 2, 3, 4), rugosite=0.4)
    ob.sphere((0.0, 0.0, 0.0), 0.36, m_s, echelle=(1.0, 0.6, 0.7), nom="coque")
    ob.cone((-0.36, 0.0, 0.0), 0.12, 0.3, m_s, rotation=(0.0, math.radians(90), 0.0), nom="pointe")



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
