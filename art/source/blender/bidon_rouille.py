"""
bidon_rouille.py - bidon d'acier rouillé du radeau (prop, biome radeau_surface, M3), construit dans Blender.

Corps cylindrique, deux cerclages, couvercle, traces de rouille (bande cuivre). Aucune source téléchargée.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/bidon_rouille.py
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "bidon_rouille"
SORTIE = os.path.join(ob.ROOT, "art", "rendu", ID)
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("PROP_ECHANTILLONS", "48"))
LARGEUR_CADRE = 2.0


def construire():
    m_acier = ob.materiau("bidon_acier", "metal", bandes=(0, 1, 2, 3), rugosite=0.5)
    m_rouille = ob.materiau("bidon_rouille_m", "cuivre", bandes=(1, 2, 3, 4), rugosite=0.7)
    ob.cylindre((0.0, 0.0, 0.0), 0.42, 0.9, m_acier, nom="corps")
    ob.cylindre((0.0, 0.0, 0.44), 0.30, 0.04, m_acier, nom="couvercle")
    for k, z in enumerate((-0.30, 0.30)):
        ob.cylindre((0.0, 0.0, z), 0.44, 0.07, m_rouille, nom=f"cerclage_{k + 1}")
    ob.cylindre((0.0, 0.0, -0.46), 0.36, 0.04, m_rouille, nom="fond")


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
