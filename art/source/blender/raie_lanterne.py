"""
raie_lanterne.py - raie lanterne de la fosse sombre (biome fosse_sombre, tranche 2, M4), construite dans Blender.

Disque plat et large qui plane au-dessus du fond : ailes arrondies (lobes avant et arrière), queue fine
terminée par un organe lumineux, œil lisible sur le dessus. Elle bat lentement des ailes (nage), les déploie
et allume son organe quand elle se sent menacée (attaque), puis s'affaisse en roulant sur le flanc (mort).
Aucun modèle ni rig téléchargé : sphères, cônes et ellipsoïdes, reliés à des charnières.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/raie_lanterne.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : battement lent des ailes, queue qui ondule (boucle)
    attaque_01..04 : ailes déployées, organe lumineux agrandi, descente vers le plongeur
    mort_01..06    : roulement sur le flanc, ailes qui pendent, organe qui s'éteint
Essais rapides : RAIE_IMAGES=1,9 (numéros d'image Blender), RAIE_ECHANTILLONS=24.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "raie_lanterne"
SORTIE = os.environ.get("CREATURE_SORTIE", os.path.join(ob.ROOT, "art", "rendu", ID))
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("RAIE_ECHANTILLONS", "64"))
APERCU = {int(v) for v in os.environ.get("RAIE_IMAGES", "").split(",") if v.strip()}
LARGEUR_CADRE = 2.4     # unités de monde sur la largeur de l'image (64 px) : la raie est grande
CENTRE_CADRE_X = -0.10

PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18


def construire(scene):
    m_dos = ob.materiau("raie_dos", "caoutchouc", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_ventre = ob.materiau("raie_ventre", "verre", bandes=(2, 3, 4, 5), rugosite=0.4)
    m_queue = ob.materiau("raie_queue", "caoutchouc", bandes=(1, 2, 2, 3), rugosite=0.5)
    m_lampe = ob.materiau("raie_organe", "lampe", bandes=(2, 3, 4, 4), rugosite=0.3)

    # disque : corps large et plat (plan de la caméra = XZ, épaisseur sur Y)
    corps = ob.sphere((0.0, 0.0, 0.0), 0.5, m_dos, echelle=(0.80, 0.20, 0.42), nom="corps")
    # ventre pâle sous le disque, côté caméra vers le bas
    ventre = ob.sphere((0.0, -0.05, -0.14), 0.5, m_ventre, echelle=(0.56, 0.12, 0.12), nom="ventre")
    ob.parent(ventre, corps)

    # ailes : lobes avant (tête) et arrière, qui battent sur le plan Z
    charniere_aile_av = ob.pivot(scene, "charniere_aile_avant", (0.30, 0.0, 0.0), corps)
    aile_av = ob.sphere((0.48, 0.0, 0.04), 0.5, m_dos, echelle=(0.42, 0.14, 0.72), nom="aile_avant")
    ob.parent(aile_av, charniere_aile_av)
    charniere_aile_ar = ob.pivot(scene, "charniere_aile_arriere", (-0.20, 0.0, 0.0), corps)
    aile_ar = ob.sphere((-0.36, 0.0, 0.02), 0.5, m_dos, echelle=(0.36, 0.14, 0.62), nom="aile_arriere")
    ob.parent(aile_ar, charniere_aile_ar)

    # œil : sur le dessus de la tête, côté caméra, blanc contrasté et pupille noire
    ob.oeil((0.52, -0.12, 0.10), 0.06, corps, pupille=0.6, nom="oeil")

    # organe lumineux à l'avant (bout du museau) : petite lampe qui s'allume
    organe = ob.sphere((0.66, -0.06, -0.02), 0.07, m_lampe, nom="organe_lumineux")
    ob.parent(organe, corps)

    # queue fine, sur une charnière arrière, terminée par un second organe
    charniere_queue = ob.pivot(scene, "charniere_queue", (-0.46, 0.0, 0.0), corps)
    queue = ob.cone((-0.80, 0.0, 0.0), 0.035, 0.66, m_queue,
                    rotation=(0.0, math.radians(90), 0.0), nom="queue")
    ob.parent(queue, charniere_queue)
    bout = ob.sphere((-1.16, 0.0, 0.0), 0.05, m_lampe, nom="bout_queue")
    ob.parent(bout, charniere_queue)
    return {"corps": corps, "aile_av": charniere_aile_av, "aile_ar": charniere_aile_ar,
            "queue": charniere_queue, "organe": organe}


def animer(p):
    """Clés : nage 1-8 (boucle), attaque 9-12 (ailes déployées), mort 13-18 (roulement)."""
    corps, aile_av, aile_ar, queue, organe = p["corps"], p["aile_av"], p["aile_ar"], p["queue"], p["organe"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        # battement : les ailes se relèvent et s'abaissent (échelle sur Z = plan de la caméra)
        ob.cle(aile_av, f, rot=(0.0, 0.25 * math.sin(t), 0.0))
        ob.cle(aile_ar, f, rot=(0.0, 0.25 * math.sin(t + 0.8), 0.0))
        ob.cle(queue, f, rot=(0.0, 0.30 * math.sin(t + 0.4), 0.0))
        ob.cle(corps, f, rot=(0.0, 0.0, 0.0), loc=(0.0, 0.0, 0.03 * math.cos(t)))
        ob.cle(organe, f, echelle=(1.0, 1.0, 1.0))
    # attaque : ailes déployées, organe allumé plus fort, descente vers le plongeur
    for f, c, ra, rq, s_org in ((9, -0.12, 0.45, 0.10, 1.6), (10, -0.22, 0.60, -0.10, 2.2),
                                (11, -0.20, 0.55, 0.10, 2.0), (12, -0.10, 0.45, 0.00, 1.6)):
        ob.cle(corps, f, rot=(0.0, c, 0.0), loc=(0.0, 0.0, -0.04))
        ob.cle(aile_av, f, rot=(0.0, ra, 0.0))
        ob.cle(aile_ar, f, rot=(0.0, -ra, 0.0))
        ob.cle(queue, f, rot=(0.0, rq, 0.0))
        ob.cle(organe, f, echelle=(s_org, s_org, s_org))
    # mort : la raie roule sur le flanc, les ailes pendent, l'organe s'éteint
    for f, roule, pend, s_org in ((13, 0.00, 0.00, 1.0), (14, 0.25, 0.20, 0.8), (15, 0.50, 0.35, 0.6),
                                  (16, 0.75, 0.50, 0.5), (17, 0.90, 0.60, 0.4), (18, 1.00, 0.65, 0.4)):
        ob.cle(corps, f, rot=(0.0, roule, 0.0), loc=(0.0, 0.0, -0.10 * roule))
        ob.cle(aile_av, f, rot=(0.0, pend, 0.0))
        ob.cle(aile_ar, f, rot=(0.0, -pend, 0.0))
        ob.cle(queue, f, rot=(0.0, 0.10 * roule, 0.0))
        ob.cle(organe, f, echelle=(s_org, s_org, s_org))


def main():
    scene = ob.scene_vide()
    p = construire(scene)
    animer(p)
    ob.eclairer(scene)
    ob.camera(scene, LARGEUR_CADRE, centre=(CENTRE_CADRE_X, 0.0, 0.0))
    ob.reglages(scene, RES, echantillons=ECHANTILLONS)
    scene.frame_start = 1
    scene.frame_end = DERNIERE
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    ob.rendre_plan(scene, SORTIE, PLAN, apercu=APERCU or None)


main()
