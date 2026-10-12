"""
oursin_bombe.py - oursin bombe du récif peu profond (biome recif_peu_profond, M3), construit dans Blender.

Sphère épineuse couleur de bronze, piquants longs et fins en étoile. Il reste immobile sur la roche :
les mouvements sont légers (flottement, piquants qui frémissent), puis il se hérisse et s'affaisse.
Aucun modèle ni rig téléchargé : une sphère et des cônes, les piquants étant des enfants de la sphère.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/oursin_bombe.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : flottement très léger, piquants qui frémissent (boucle)
    attaque_01..04 : il se hérisse : piquants allongés, corps gonflé (avertissement)
    mort_01..06    : piquants qui s'affaissent, corps qui s'enfonce et roule
Essais rapides : OURSIN_IMAGES=1,9 (numéros d'image Blender), OURSIN_ECHANTILLONS=24.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

ID = "oursin_bombe"
SORTIE = os.environ.get("CREATURE_SORTIE", os.path.join(ob.ROOT, "art", "rendu", ID))
BLEND = os.path.join(ob.HERE, ID + ".blend")
RES = 512
ECHANTILLONS = int(os.environ.get("OURSIN_ECHANTILLONS", "64"))
APERCU = {int(v) for v in os.environ.get("OURSIN_IMAGES", "").split(",") if v.strip()}
LARGEUR_CADRE = 2.0     # unités de monde sur la largeur de l'image (64 px)

PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18
RAYON_CORPS = 0.40
LONGUEUR_PIQUANT = 0.30
NB_PIQUANTS = 14


def directions(n):
    """n directions réparties sur une sphère (spirale de Fibonacci), en unités."""
    dirs = []
    for k in range(n):
        z = 1.0 - 2.0 * (k + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        phi = k * math.pi * (3.0 - math.sqrt(5.0))
        dirs.append(Vector((r * math.cos(phi), r * math.sin(phi), z)).normalized())
    return dirs


def construire(scene):
    m_corps = ob.materiau("oursin_corps", "cuivre", bandes=(1, 2, 3, 4), rugosite=0.4)
    m_piquant = ob.materiau("oursin_piquant", "cuivre", bandes=(2, 3, 4, 4), rugosite=0.35)

    corps = ob.sphere((0.0, 0.0, 0.0), RAYON_CORPS, m_corps, nom="corps")
    # œil : globe blanc et pupille noire sur la face visible, côté caméra
    ob.oeil((0.12, -0.36, 0.12), 0.075, corps, pupille=0.6, nom="oeil")
    piquants = []
    for k, d in enumerate(directions(NB_PIQUANTS)):
        centre = d * (RAYON_CORPS + LONGUEUR_PIQUANT / 2.0)
        pq = ob.cone(centre, 0.045, LONGUEUR_PIQUANT, m_piquant, nom=f"piquant_{k + 1:02d}")
        # l'axe +Z du cône suit la direction radiale
        pq.rotation_mode = "QUATERNION"
        pq.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(d)
        ob.parent(pq, corps)
        piquants.append(pq)
    return {"corps": corps, "piquants": piquants}


def animer(p):
    """Nage 1-8 (boucle), attaque 9-12 (hérissé), mort 13-18 (affaissé)."""
    corps, piquants = p["corps"], p["piquants"]
    for f in range(1, 9):
        t = 2.0 * math.pi * (f - 1) / 8.0
        ob.cle(corps, f, loc=(0.0, 0.0, 0.03 * math.sin(t)))
        for k, pq in enumerate(piquants):
            ob.cle(pq, f, echelle=(1.0, 1.0, 1.0 + 0.06 * math.sin(t + k * 0.9)))
    for f, gonfle, allonge in ((9, 1.04, 1.70), (10, 1.08, 2.30), (11, 1.07, 2.20), (12, 1.03, 1.80)):
        ob.cle(corps, f, echelle=(gonfle, gonfle, gonfle))
        for pq in piquants:
            ob.cle(pq, f, echelle=(1.0, 1.0, allonge))
    for f, s_, plat, descente in ((13, 1.00, 1.00, 0.00), (14, 1.04, 0.90, -0.03), (15, 1.10, 0.75, -0.07),
                                  (16, 1.15, 0.65, -0.10), (17, 1.18, 0.58, -0.12), (18, 1.18, 0.55, -0.12)):
        ob.cle(corps, f, echelle=(s_, s_, s_ * plat), loc=(0.0, 0.0, descente))
        for pq in piquants:
            ob.cle(pq, f, echelle=(1.0, 1.0, 1.0 - 0.6 * (f - 13) / 5.0))


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
