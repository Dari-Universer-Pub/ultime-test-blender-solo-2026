"""
tube_ver.py - tubes de vers (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : trois tubes calcaires verticaux. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/tube_ver.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "tube_ver"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_t = ob.materiau("tube_calcaire", "sable", bandes=(1, 2, 3, 4), rugosite=0.7)
    m_o = ob.materiau("tube_ouverture", "recif", bandes=(0, 1, 1, 2), rugosite=0.6)
    for k, (x, h) in enumerate(((-0.2, 0.8), (0.0, 1.0), (0.2, 0.6))):
        ob.cylindre((x, 0.0, 0.0), 0.07, h, m_t, nom=f"tube_{k + 1}")
        ob.cylindre((x, 0.0, h / 2.0), 0.075, 0.03, m_o, nom=f"ouverture_{k + 1}")



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
