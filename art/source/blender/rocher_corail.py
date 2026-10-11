"""
rocher_corail.py - rocher couvert de corail (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : bloc de roche et bosses de corail. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/rocher_corail.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "rocher_corail"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_r = ob.materiau("rocher_roche", "roche", bandes=(1, 2, 3, 4), rugosite=0.9)
    m_c = ob.materiau("rocher_corail", "recif", bandes=(2, 3, 4, 4), rugosite=0.6)
    ob.sphere((0.0, 0.0, 0.0), 0.42, m_r, echelle=(1.0, 0.9, 0.8), nom="bloc")
    for k, (x, z) in enumerate(((-0.2, 0.3), (0.12, 0.34), (0.3, 0.12))):
        ob.sphere((x, 0.0, z), 0.12, m_c, nom=f"bosse_{k + 1}")



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
