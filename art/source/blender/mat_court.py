"""
mat_court.py - tronçon de mât (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : fût de bois et deux cerclages de cordage. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/mat_court.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "mat_court"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_bois = ob.materiau("mat_bois", "ocre", bandes=(1, 2, 3, 4), rugosite=0.8)
    m_corde = ob.materiau("mat_corde", "sable", bandes=(1, 2, 3, 4), rugosite=0.9)
    ob.cylindre((0.0, 0.0, 0.0), 0.13, 1.0, m_bois, nom="mat")
    for k, z in enumerate((-0.25, 0.25)):
        ob.tore((0.0, 0.0, z), 0.135, 0.03, m_corde, nom=f"liens_{k + 1}")



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
