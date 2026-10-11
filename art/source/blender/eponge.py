"""
eponge.py - éponge de mer (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : masse ovale et cratères. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/eponge.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "eponge"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_o = ob.materiau("eponge_m", "ocre", bandes=(1, 2, 3, 4), rugosite=0.9)
    ob.sphere((0.0, 0.0, 0.0), 0.36, m_o, echelle=(1.0, 0.9, 0.8), nom="masse")
    for k, (x, z) in enumerate(((-0.14, 0.12), (0.12, 0.1), (0.0, -0.12))):
        ob.sphere((x, -0.2, z), 0.06, m_o, echelle=(1.0, 0.4, 1.0), nom=f"crater_{k + 1}")



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
