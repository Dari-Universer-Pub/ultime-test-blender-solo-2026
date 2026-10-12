"""
anemone.py - anémone de mer (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : pied sphérique et tentacules coniques. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/anemone.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "anemone"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 1.3


def construire():
    m_p = ob.materiau("anemone_pied", "palmes", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_t = ob.materiau("anemone_tentacule", "recif", bandes=(2, 3, 4, 4), rugosite=0.5)
    ob.sphere((0.0, 0.0, -0.3), 0.2, m_p, echelle=(1.0, 1.0, 0.6), nom="pied")
    for k in range(8):
        a = k * math.pi / 4
        ob.cone((math.cos(a) * 0.2, 0.0, -0.22 + math.sin(a) * 0.2), 0.05, 0.4, m_t, rotation=(0.0, a - math.pi / 2, 0.0), nom=f"tentacule_{k + 1}")



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
