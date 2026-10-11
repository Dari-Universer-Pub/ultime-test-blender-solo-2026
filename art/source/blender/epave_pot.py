"""
epave_pot.py - pot de cuivre d'épave (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : pot cylindrique et deux anses. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/epave_pot.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "epave_pot"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_c = ob.materiau("pot_cuivre", "cuivre", bandes=(1, 2, 3, 4), rugosite=0.6)
    ob.sphere((0.0, 0.0, 0.0), 0.34, m_c, echelle=(1.0, 0.8, 0.9), nom="pot")
    ob.tore((-0.34, 0.0, 0.0), 0.12, 0.03, m_c, rotation=(0.0, math.pi / 2, 0.0), nom="anse_1")
    ob.tore((0.34, 0.0, 0.0), 0.12, 0.03, m_c, rotation=(0.0, math.pi / 2, 0.0), nom="anse_2")



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
