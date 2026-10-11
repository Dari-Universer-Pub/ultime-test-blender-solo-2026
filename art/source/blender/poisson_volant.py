"""
poisson_volant.py - poisson volant du radeau (biome radeau_surface, M3), construit dans Blender.

Aucun modèle ni rig téléchargé : le poisson est fait de sphères, de cônes et de disques, pièces
reliées à des charnières (objets vides) : queue, nageoires pectorales, corps.
Le script refait tout de zéro :
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/poisson_volant.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : battement de queue, ondulation, nageoires qui vibrent (boucle)
    attaque_01..04 : bond hors de l'eau, nageoires déployées, corps cabré
    mort_01..06    : retombée, corps qui bascule, nageoires qui s'affaissent
Essais rapides : POISSON_IMAGES=1,9 (numéros d'image Blender), POISSON_ECHANTILLONS=24.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "poisson_volant"
SORTIE = os.environ.get("CREATURE_SORTIE", os.path.join(ob.ROOT, "art", "rendu", ID))
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("POISSON_ECHANTILLONS", "64"))
APERCU = {int(v) for v in os.environ.get("POISSON_IMAGES", "").split(",") if v.strip()}
LARGEUR_CADRE = 1.8     # unités de monde sur la largeur de l'image (64 px)

# plan des images : (numéro d'image Blender, nom du fichier)
PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18


def construire(scene):
    """Pièces du poisson, avec leurs matériaux (rampes de art/palette.json)."""
    m_corps = ob.materiau("poisson_corps", "metal", bandes=(1, 2, 3, 5), rugosite=0.35)
    m_dos = ob.materiau("poisson_dos", "caoutchouc", bandes=(0, 1, 2, 3), rugosite=0.45)
    m_aile = ob.materiau("poisson_aile", "bulle", bandes=(0, 1, 2, 3), rugosite=0.5)
    m_queue = ob.materiau("poisson_queue", "palmes", bandes=(1, 2, 3, 4), rugosite=0.5)

    corps = ob.sphere((0.0, 0.0, 0.0), 0.5, m_corps, echelle=(1.25, 0.9, 0.5), nom="corps")
    dos = ob.cone((0.08, 0.0, 0.30), 0.10, 0.24, m_dos, nom="nageoire_dorsale")
    ob.parent(dos, corps)

    # queue fourchue : deux lobes dont la base est sur la charnière arrière du corps
    charniere_queue = ob.pivot(scene, "charniere_queue", (-0.62, 0.0, 0.0), corps)
    d_haut = (-0.88, 0.0, 0.47)     # direction du lobe haut (arrière, vers le haut)
    d_bas = (-0.88, 0.0, -0.47)     # direction du lobe bas (arrière, vers le bas)
    lobe_haut = ob.cone((-0.805, 0.0, 0.099), 0.14, 0.42, m_queue,
                        rotation=(0.0, math.radians(-62), 0.0), nom="lobe_queue_haut")
    lobe_bas = ob.cone((-0.805, 0.0, -0.099), 0.14, 0.42, m_queue,
                       rotation=(0.0, math.radians(-118), 0.0), nom="lobe_queue_bas")
    ob.parent(lobe_haut, charniere_queue)
    ob.parent(lobe_bas, charniere_queue)

    # nageoire pectorale : un grand disque en éventail (plan XZ, face à la caméra), sur une charnière
    charniere_aile = ob.pivot(scene, "charniere_aile", (0.18, 0.0, 0.30), corps)
    aile = ob.sphere((0.18, 0.0, 0.30), 0.5, m_aile, echelle=(0.80, 0.03, 0.52), nom="aile")
    aile.rotation_euler = (0.0, math.radians(-30), 0.0)
    ob.parent(aile, charniere_aile)
    return {"corps": corps, "queue": charniere_queue, "aile": charniere_aile}


def animer(p):
    """Clés de rotation autour de l'axe Y (le plan de la caméra) : nage 1-8 (boucle), attaque 9-12, mort 13-18."""
    corps, queue, aile = p["corps"], p["queue"], p["aile"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        ob.cle(queue, f, rot=(0.0, 0.42 * math.sin(t), 0.0))
        ob.cle(corps, f, rot=(0.0, 0.07 * math.sin(t + 0.6), 0.0))
        ob.cle(aile, f, rot=(0.0, 0.10 * math.sin(t), 0.0))
    # attaque : le corps se cabre, les nageoires se déploient
    for f, c, a, q in ((9, -0.25, -0.20, 0.35), (10, -0.55, -0.45, -0.35),
                       (11, -0.45, -0.40, 0.35), (12, -0.20, -0.20, 0.0)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(aile, f, rot=(0.0, a, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))
    # mort : retombée, le corps bascule, les nageoires s'affaissent
    for f, c, a, q in ((13, -0.20, 0.00, 0.00), (14, 0.10, 0.10, 0.25), (15, 0.55, 0.45, -0.25),
                       (16, 0.95, 0.70, 0.25), (17, 1.20, 0.85, -0.20), (18, 1.30, 0.95, 0.20)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(aile, f, rot=(0.0, a, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))


def main():
    scene = ob.scene_vide()
    p = construire(scene)
    animer(p)
    ob.eclairer(scene)
    ob.camera(scene, LARGEUR_CADRE, centre=(-0.20, 0.0, 0.0))
    ob.reglages(scene, RES, echantillons=ECHANTILLONS)
    scene.frame_start = 1
    scene.frame_end = DERNIERE
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    ob.rendre_plan(scene, SORTIE, PLAN, apercu=APERCU or None)


main()
