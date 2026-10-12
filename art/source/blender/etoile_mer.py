"""
etoile_mer.py - étoile de mer (prop, biome recif_peu_profond, M3), construit dans Blender.

Pièces : cinq bras coniques dans le plan. Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/etoile_mer.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "etoile_mer"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_e = ob.materiau("etoile_m", "palmes", bandes=(1, 2, 3, 4), rugosite=0.6)
    ob.sphere((0.0, 0.0, 0.0), 0.12, m_e, nom="centre")
    for k in range(5):
        a = k * 2 * math.pi / 5 + math.pi / 2
        ob.cone((math.cos(a) * 0.28, 0.0, math.sin(a) * 0.28), 0.1, 0.42, m_e, rotation=(0.0, -a + math.pi / 2, 0.0), nom=f"bras_{k + 1}")



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
