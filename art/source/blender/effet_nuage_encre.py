"""
effet_nuage_encre.py - nuage d'encre (effet, M3), construit dans Blender.

Pièces : amas sombre d'encre de seiche. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_nuage_encre.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_nuage_encre"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.8


def construire():
    m_e = ob.materiau("encre_m", "caoutchouc", bandes=(0, 0, 1, 2), rugosite=0.6)
    for k, (x, z) in enumerate(((0.0, 0.0), (-0.25, 0.1), (0.25, 0.12), (0.0, 0.3), (0.12, -0.18))):
        ob.sphere((x, 0.0, z), 0.22, m_e, nom=f"volute_{k + 1}")



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
