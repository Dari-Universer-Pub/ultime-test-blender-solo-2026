"""
carangue_rayee.py - carangue rayée du récif peu profond (biome recif_peu_profond, M3), construite dans Blender.

Silhouette de poisson : corps haut et comprimé, museau avec bouche, œil lisible, dorsale épineuse
(piquants) et dorsale molle distinctes, nageoire anale, pectorale, queue fourchue, trois rayures.
Aucun modèle ni rig téléchargé : sphères, cônes et disques, reliés à des charnières et à des pivots.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/carangue_rayee.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : battement de queue, corps qui ondule (boucle)
    attaque_01..04 : piquants de la dorsale qui se dressent, corps tourné et gueule ouverte
    mort_01..06    : le corps roule lentement sur le flanc, nageoires qui s'affaissent
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
LARGEUR_CADRE = 1.8     # unités de monde sur la largeur de l'image (64 px)
CENTRE_CADRE_X = -0.14  # la caméra regarde un peu vers la queue : le poisson tient la case

PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18
RAYURES_X = (-0.32, -0.08, 0.14)     # positions des rayures sombres le long du corps
PIQUANTS_X = (0.10, 0.00, -0.10, -0.20)   # piquants de la dorsale épineuse, de l'avant vers l'arrière


def construire(scene):
    m_corps = ob.materiau("carangue_corps", "metal", bandes=(1, 2, 3, 5), rugosite=0.3)
    m_rayure = ob.materiau("carangue_rayure", "caoutchouc", bandes=(1, 2, 3, 4), rugosite=0.45)
    m_nageoire = ob.materiau("carangue_nageoire", "lampe", bandes=(1, 2, 3, 4), rugosite=0.5)

    corps = ob.sphere((0.0, 0.0, 0.0), 0.5, m_corps, echelle=(1.10, 0.50, 0.84), nom="corps")

    # museau : petit cône pointé vers l'avant, avec une bouche sombre à son extrémité
    museau = ob.cone((0.60, 0.0, -0.02), 0.15, 0.24, m_corps, rotation=(0.0, math.radians(90), 0.0), nom="museau")
    ob.parent(museau, corps)
    
    # rayures verticales : pièces sombres posées devant le flanc (côté caméra, y négatif)
    for k, x in enumerate(RAYURES_X):
        rayure = ob.sphere((x, -0.22, 0.0), 0.5, m_rayure, echelle=(0.07, 0.07, 0.56), nom=f"rayure_{k + 1}")
        ob.parent(rayure, corps)

    # œil : blanc de la rampe metal, pupille noire, côté caméra, bien visible sur la tête
    ob.oeil((0.30, -0.25, 0.10), 0.095, corps, pupille=0.62, nom="oeil")

    # dorsale épineuse : quatre piquants dressés, placés sur le dos ; ils se dressent en attaque
    piquants = []
    for k, x in enumerate(PIQUANTS_X):
        pq = ob.cone((x, 0.0, 0.42), 0.055, 0.22, m_nageoire, rotation=(0.0, math.radians(-8), 0.0),
                     nom=f"piquant_dorsal_{k + 1}")
        ob.parent(pq, corps)
        piquants.append(pq)

    # dorsale molle : disque effilé à l'arrière, qui ondule
    charniere_molle = ob.pivot(scene, "charniere_dorsale_molle", (-0.22, 0.0, 0.34), corps)
    molle = ob.sphere((-0.22, 0.0, 0.34), 0.5, m_nageoire, echelle=(0.42, 0.025, 0.20), nom="dorsale_molle")
    molle.rotation_euler = (0.0, math.radians(18), 0.0)
    ob.parent(molle, charniere_molle)

    # nageoire anale : sous le corps, vers la queue
    anale = ob.sphere((-0.22, 0.0, -0.34), 0.5, m_nageoire, echelle=(0.36, 0.025, 0.16), nom="anale")
    anale.rotation_euler = (0.0, math.radians(-14), 0.0)
    ob.parent(anale, corps)

    # pectorale : petite nageoire sur le flanc
    pectorale = ob.sphere((0.14, -0.25, -0.10), 0.5, m_nageoire, echelle=(0.30, 0.02, 0.05), nom="pectorale")
    pectorale.rotation_euler = (0.0, math.radians(-38), 0.0)
    ob.parent(pectorale, corps)

    # queue fourchue sur une charnière arrière
    charniere_queue = ob.pivot(scene, "charniere_queue", (-0.58, 0.0, 0.0), corps)
    lobe_haut = ob.cone((-0.80, 0.0, 0.13), 0.10, 0.40, m_nageoire,
                        rotation=(0.0, math.radians(-58), 0.0), nom="lobe_queue_haut")
    lobe_bas = ob.cone((-0.80, 0.0, -0.13), 0.10, 0.40, m_nageoire,
                       rotation=(0.0, math.radians(-122), 0.0), nom="lobe_queue_bas")
    ob.parent(lobe_haut, charniere_queue)
    ob.parent(lobe_bas, charniere_queue)

    return {"corps": corps, "queue": charniere_queue, "molle": charniere_molle,
            "piquants": piquants, "pectorale": pectorale}


def animer(p):
    """Clés (rotation sur Y = plan de la caméra) : nage 1-8 (boucle), attaque 9-12, mort 13-18."""
    corps, queue, molle, piquants = p["corps"], p["queue"], p["molle"], p["piquants"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        ob.cle(queue, f, rot=(0.0, 0.45 * math.sin(t), 0.0))
        ob.cle(corps, f, rot=(0.0, 0.06 * math.sin(t + 0.6), 0.0))
        ob.cle(molle, f, rot=(0.0, 0.10 * math.sin(t + 1.0), 0.0))
        for pq in piquants:
            ob.cle(pq, f, echelle=(1.0, 1.0, 1.0))
    # attaque : piquants dressés (plus longs), corps tourné de trois quarts, gueule ouverte
    for f, c, q, dress in ((9, 0.10, 0.10, 1.35), (10, 0.25, 0.00, 1.65),
                           (11, 0.20, 0.00, 1.60), (12, 0.08, 0.10, 1.35)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))
        ob.cle(molle, f, rot=(0.0, -0.20, 0.0))
        for pq in piquants:
            ob.cle(pq, f, echelle=(1.0, 1.0, dress))
    # mort : roulement lent sur le flanc, nageoires qui s'affaissent
    for f, c, m, q in ((13, 0.00, 0.00, 0.00), (14, 0.20, 0.25, 0.20), (15, 0.45, 0.45, -0.15),
                       (16, 0.70, 0.60, 0.10), (17, 0.85, 0.75, -0.08), (18, 0.95, 0.85, 0.05)):
        ob.cle(corps, f, rot=(0.0, c, 0.0))
        ob.cle(molle, f, rot=(0.0, m, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))
        for pq in piquants:
            ob.cle(pq, f, echelle=(1.0, 1.0, 1.0 - 0.3 * (f - 13) / 5.0))


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
