"""
caisse_bois.py - caisse en bois de la plate-forme (prop, biome radeau_surface, M3), construit dans Blender.

Pièces : caisse cubique et deux lattes sombres. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/caisse_bois.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "caisse_bois"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_bois = ob.materiau("caisse_bois", "ocre", bandes=(1, 2, 3, 4), rugosite=0.8)
    m_lattes = ob.materiau("caisse_lattes", "ocre", bandes=(0, 0, 1, 1), rugosite=0.8)
    ob.cube((0.0, 0.0, 0.0), 1.0, m_bois, echelle=(0.8, 0.8, 0.8), nom="caisse")
    for k, z in enumerate((-0.2, 0.2)):
        ob.cube((0.0, -0.42, z), 1.0, m_lattes, echelle=(0.82, 0.03, 0.06), nom=f"latte_{k + 1}")
    for k, (x, z) in enumerate(((-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36))):
        ob.cube((x, -0.40, z), 1.0, m_lattes, echelle=(0.09, 0.05, 0.09), nom=f"montant_{k + 1}")



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
