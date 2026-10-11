"""
effet_poussiere_creusage.py - poussière de creusage (effet, M3), construit dans Blender.

Pièces : amas de grains de roche. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/effet_poussiere_creusage.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "effet_poussiere_creusage"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.6


def construire():
    m_r = ob.materiau("poussiere_m", "roche", bandes=(1, 2, 3, 4), rugosite=0.9)
    for k, (x, z) in enumerate(((-0.3, 0.1), (0.1, 0.25), (0.3, -0.05), (-0.05, -0.2), (0.22, -0.3))):
        ob.sphere((x, 0.0, z), 0.13, m_r, nom=f"grain_{k + 1}")



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
