"""
effet_impact_coup.py - impact de coup (effet, M3), construit dans Blender.

Pièces : anneau et éclats. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_impact_coup.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_impact_coup"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.6


def construire():
    m_l = ob.materiau("impact_m", "lampe", bandes=(2, 3, 4, 4), rugosite=0.3)
    ob.tore((0.0, 0.0, 0.0), 0.3, 0.05, m_l, rotation=(math.pi / 2, 0.0, 0.0), nom="anneau")
    for k in range(6):
        a = k * math.pi / 3
        ob.cone((math.cos(a) * 0.5, 0.0, math.sin(a) * 0.5), 0.05, 0.25, m_l, rotation=(0.0, a + math.pi / 2, 0.0), nom=f"eclat_{k + 1}")



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
