"""
tortue_de_corail.py - tortue de corail du récif peu profond (biome recif_peu_profond, M3), construite dans Blender.

Carapace bombée couverte de coraux, plastron pâle, tête avec œil et bec sombre, quatre palmes et petite
queue. Aucun modèle ni rig téléchargé : sphères, cônes et ellipsoïdes, reliés à des charnières.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/tortue_de_corail.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : les palmes avant et arrière battent en alternance (boucle), corps qui se balance
    attaque_01..04 : geste d'avertissement : tête relevée et tendue, palmes écartées
    mort_01..06    : la tortue coule lentement, tête qui tombe, palmes qui pendent
Essais rapides : TORTUE_IMAGES=1,9 (numéros d'image Blender), TORTUE_ECHANTILLONS=24.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "tortue_de_corail"
SORTIE = os.environ.get("CREATURE_SORTIE", os.path.join(ob.ROOT, "art", "rendu", ID))
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("TORTUE_ECHANTILLONS", "64"))
APERCU = {int(v) for v in os.environ.get("TORTUE_IMAGES", "").split(",") if v.strip()}
LARGEUR_CADRE = 1.3     # unités de monde sur la largeur de l'image (64 px)
CENTRE_CADRE_X = 0.05

PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18

# coraux de la carapace : (x, z, rotation Y en radians) ; ils pointent vers le haut et vers l'extérieur
CORAUX = ((-0.30, 0.20, -0.5), (-0.10, 0.22, -0.2), (0.10, 0.22, 0.1), (0.28, 0.19, 0.45))


def construire(scene):
    m_carapace = ob.materiau("tortue_carapace", "recif", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_plastron = ob.materiau("tortue_plastron", "sable", bandes=(2, 3, 4, 4), rugosite=0.6)
    m_corail = ob.materiau("tortue_corail", "palmes", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_corail_rose = ob.materiau("tortue_corail_rose", "recif", bandes=(2, 3, 4, 4), rugosite=0.5)
    m_palme = ob.materiau("tortue_palme", "bouteille", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_tete = ob.materiau("tortue_tete", "bouteille", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_bec = ob.materiau("tortue_bec", "caoutchouc", bandes=(1, 2, 3, 3), rugosite=0.5)

    corps = ob.sphere((0.0, 0.0, 0.02), 0.5, m_carapace, echelle=(0.72, 0.52, 0.62), nom="carapace")
    plastron = ob.sphere((0.0, 0.0, -0.14), 0.5, m_plastron, echelle=(0.64, 0.46, 0.14), nom="plastron")
    ob.parent(plastron, corps)

    # coraux : petits cônes sur le dos, alternance orange et rose
    for k, (x, z, rot) in enumerate(CORAUX):
        mat = m_corail if k % 2 == 0 else m_corail_rose
        c = ob.cone((x, 0.0, z), 0.07, 0.16, mat, rotation=(0.0, rot, 0.0), nom=f"corail_{k + 1}")
        ob.parent(c, corps)

    # tête : charnière à l'avant ; œil et bec sont enfants de la tête
    charniere_tete = ob.pivot(scene, "charniere_tete", (0.34, 0.0, 0.02), corps)
    tete = ob.sphere((0.44, -0.02, 0.04), 0.13, m_tete, echelle=(1.0, 0.95, 0.9), nom="tete")
    ob.parent(tete, charniere_tete)
    bec = ob.cone((0.57, 0.0, 0.02), 0.06, 0.11, m_bec, rotation=(0.0, math.radians(90), 0.0), nom="bec")
    ob.parent(bec, charniere_tete)
    ob.oeil((0.50, -0.12, 0.09), 0.045, charniere_tete, pupille=0.6, nom="oeil")

    # palmes avant (près de la caméra) et arrière, sur des charnières
    palme_avant = ob.pivot(scene, "charniere_palme_avant", (0.26, -0.28, -0.10), corps)
    pa = ob.sphere((0.26, -0.28, -0.10), 0.5, m_palme, echelle=(0.28, 0.05, 0.09), nom="palme_avant")
    pa.rotation_euler = (0.0, math.radians(-30), 0.0)
    ob.parent(pa, palme_avant)
    palme_arriere = ob.pivot(scene, "charniere_palme_arriere", (-0.26, -0.26, -0.12), corps)
    par = ob.sphere((-0.26, -0.26, -0.12), 0.5, m_palme, echelle=(0.20, 0.05, 0.07), nom="palme_arriere")
    par.rotation_euler = (0.0, math.radians(20), 0.0)
    ob.parent(par, palme_arriere)

    # petite queue
    queue = ob.cone((-0.42, 0.0, -0.04), 0.06, 0.14, m_bec, rotation=(0.0, math.radians(-90), 0.0), nom="queue")
    ob.parent(queue, corps)
    return {"corps": corps, "tete": charniere_tete, "pa": palme_avant, "par": palme_arriere}


def animer(p):
    """Clés : nage 1-8 (boucle), attaque 9-12 (tête relevée), mort 13-18 (coulée)."""
    corps, tete, pa, par = p["corps"], p["tete"], p["pa"], p["par"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        ob.cle(pa, f, rot=(0.0, 0.55 * math.sin(t), 0.0))
        ob.cle(par, f, rot=(0.0, 0.55 * math.sin(t + math.pi), 0.0))
        ob.cle(corps, f, rot=(0.0, 0.0, 0.0), loc=(0.0, 0.0, 0.02 + 0.015 * math.sin(t)))
        ob.cle(tete, f, rot=(0.0, 0.0, 0.0))
    # attaque : la tête se relève et s'avance, les palmes avant s'écartent
    for f, rt, ra in ((9, -0.25, -0.45), (10, -0.45, -0.75), (11, -0.40, -0.70), (12, -0.20, -0.40)):
        ob.cle(tete, f, rot=(0.0, rt, 0.0))
        ob.cle(pa, f, rot=(0.0, ra, 0.0))
        ob.cle(par, f, rot=(0.0, 0.0, 0.0))
    # mort : la tortue s'enfonce, la tête tombe, les palmes pendent
    for f, z, rt, ra in ((13, 0.00, 0.10, 0.20), (14, -0.03, 0.20, 0.35), (15, -0.07, 0.30, 0.50),
                         (16, -0.10, 0.36, 0.60), (17, -0.12, 0.40, 0.70), (18, -0.13, 0.42, 0.75)):
        ob.cle(corps, f, rot=(0.0, 0.0, 0.0), loc=(0.0, 0.0, 0.02 + z))
        ob.cle(tete, f, rot=(0.0, rt, 0.0))
        ob.cle(pa, f, rot=(0.0, ra, 0.0))
        ob.cle(par, f, rot=(0.0, -ra * 0.5, 0.0))


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
