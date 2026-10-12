"""
tonneau_bois.py - tonneau de bois (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : fût cylindrique et trois cerclages. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/tonneau_bois.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "tonneau_bois"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_bois = ob.materiau("tonneau_bois", "ocre", bandes=(1, 2, 3, 4), rugosite=0.8)
    m_cercle = ob.materiau("tonneau_cercle", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    ob.cylindre((0.0, 0.0, 0.0), 0.40, 0.9, m_bois, nom="fut")
    for k, z in enumerate((-0.3, 0.0, 0.3)):
        ob.cylindre((0.0, 0.0, z), 0.41, 0.05, m_cercle, nom=f"cercle_{k + 1}")



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
