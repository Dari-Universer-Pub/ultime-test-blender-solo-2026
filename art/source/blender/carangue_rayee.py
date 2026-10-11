"""
carangue_rayee.py - carangue rayée du récif peu profond (biome recif_peu_profond, M3), construite dans Blender.

Corps haut et comprimé, bandes sombres verticales, nageoire dorsale effilée, queue fourchue.
Aucun modèle ni rig téléchargé : sphères aplaties, cônes et disques, reliés à des charnières.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/carangue_rayee.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : battement de queue, corps qui ondule (boucle)
    attaque_01..04 : geste d'avertissement : dorsale dressée, corps gonflé et tourné vers la caméra
    mort_01..06    : le corps roule sur le flanc, dorsale qui s'affaisse
Essais rapides : CARANGUE_IMAGES=1,9 (numéros d'image Blender), CARANGUE_ECHANTILLONS=24.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "carangue_rayee"
SORTIE = os.environ.get("CREATURE_SORTIE", os.path.join(ob.ROOT, "art", "rendu", ID))
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("CARANGUE_ECHANTILLONS", "64"))
APERCU = {int(v) for v in os.environ.get("CARANGUE_IMAGES", "").split(",") if v.strip()}
LARGEUR_CADRE = 2.0     # unités de monde sur la largeur de l'image (64 px)

PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18
BANDES_X = (-0.30, -0.02, 0.26)     # positions des bandes sombres le long du corps


def construire(scene):
    m_corps = ob.materiau("carangue_corps", "metal", bandes=(1, 2, 3, 5), rugosite=0.3)
    m_bande = ob.materiau("carangue_bande", "caoutchouc", bandes=(1, 2, 3, 4), rugosite=0.45)
    m_nageoire = ob.materiau("carangue_nageoire", "lampe", bandes=(1, 2, 3, 4), rugosite=0.5)

    corps = ob.sphere((0.0, 0.0, 0.0), 0.5, m_corps, echelle=(1.10, 0.50, 0.84), nom="corps")

    # bandes verticales : fines pièces sombres posées devant le flanc (côté caméra, y négatif)
    for k, x in enumerate(BANDES_X):
        bande = ob.sphere((x, -0.22, 0.0), 0.5, m_bande, echelle=(0.07, 0.07, 0.62), nom=f"bande_{k + 1}")
        ob.parent(bande, corps)

    # nageoire dorsale effilée : longue, basse, dressée à l'arrière du dos
    charniere_dorsale = ob.pivot(scene, "charniere_dorsale", (0.05, 0.0, 0.36), corps)
    dorsale = ob.sphere((0.0, 0.0, 0.40), 0.5, m_nageoire, echelle=(0.85, 0.03, 0.24), nom="dorsale")
    dorsale.rotation_euler = (0.0, math.radians(14), 0.0)
    ob.parent(dorsale, charniere_dorsale)

    # queue fourchue sur une charnière arrière
    charniere_queue = ob.pivot(scene, "charniere_queue", (-0.58, 0.0, 0.0), corps)
    lobe_haut = ob.cone((-0.79, 0.0, 0.12), 0.085, 0.38, m_nageoire,
                        rotation=(0.0, math.radians(-58), 0.0), nom="lobe_queue_haut")
    lobe_bas = ob.cone((-0.79, 0.0, -0.12), 0.085, 0.38, m_nageoire,
                       rotation=(0.0, math.radians(-122), 0.0), nom="lobe_queue_bas")
    ob.parent(lobe_haut, charniere_queue)
    ob.parent(lobe_bas, charniere_queue)

    # œil : petite sphère claire sur le flanc avant
    oeil = ob.sphere((0.38, -0.30, 0.08), 0.05, ob.materiau("carangue_oeil", "metal", bandes=(4, 5, 5, 5), rugosite=0.2),
                     nom="oeil")
    ob.parent(oeil, corps)
    return {"corps": corps, "dorsale": charniere_dorsale, "queue": charniere_queue}


def animer(p):
    """Clés de rotation autour de l'axe Y (plan de la caméra) : nage 1-8 (boucle), attaque 9-12, mort 13-18."""
    corps, dorsale, queue = p["corps"], p["dorsale"], p["queue"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        ob.cle(queue, f, rot=(0.0, 0.45 * math.sin(t), 0.0))
        ob.cle(corps, f, rot=(0.0, 0.06 * math.sin(t + 0.6), 0.0))
        ob.cle(dorsale, f, rot=(0.0, 0.0, 0.0))
    # attaque : dorsale dressée, corps tourné de trois quarts, queue raide
    for f, c, d, q in ((9, 0.10, -0.25, 0.10), (10, 0.25, -0.45, 0.0),
                       (11, 0.20, -0.40, 0.0), (12, 0.08, -0.20, 0.10)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(dorsale, f, rot=(0.0, d, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))
    # mort : roulement sur le flanc, dorsale qui s'affaisse
    for f, c, d, q in ((13, 0.00, 0.00, 0.00), (14, 0.30, 0.10, 0.20), (15, 0.80, 0.30, -0.15),
                       (16, 1.10, 0.50, 0.15), (17, 1.25, 0.70, -0.10), (18, 1.30, 0.80, 0.10)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(dorsale, f, rot=(0.0, d, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))


def main():
    scene = ob.scene_vide()
    p = construire(scene)
    animer(p)
    ob.eclairer(scene)
    ob.camera(scene, LARGEUR_CADRE, centre=(0.0, 0.0, 0.0))
    ob.reglages(scene, RES, echantillons=ECHANTILLONS)
    scene.frame_start = 1
    scene.frame_end = DERNIERE
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    ob.rendre_plan(scene, SORTIE, PLAN, apercu=APERCU or None)


main()
