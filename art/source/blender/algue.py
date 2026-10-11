"""
algue.py - touffe d'algue (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : trois tiges vertes et deux feuilles. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/algue.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "algue"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_a = ob.materiau("algue_verte", "bouteille", bandes=(1, 2, 3, 4), rugosite=0.5)
    for k, x in enumerate((-0.18, 0.0, 0.18)):
        ob.cylindre((x, 0.0, 0.0), 0.05, 0.9, m_a, rotation=(0.0, math.radians(8 * (k - 1)), 0.0), nom=f"tige_{k + 1}")
    ob.sphere((-0.1, 0.0, 0.12), 0.1, m_a, echelle=(1.4, 0.4, 0.5), nom="feuille_1")
    ob.sphere((0.12, 0.0, 0.25), 0.1, m_a, echelle=(1.4, 0.4, 0.5), nom="feuille_2")



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
