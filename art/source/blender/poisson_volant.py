"""
poisson_volant.py - poisson volant du radeau (biome radeau_surface, M3), construit dans Blender.

Corps sombre bleu-violet sur le dessus, ventre argenté, nageoires pectorales fines en forme d'ailes
de poisson (pas de grande aile pâle), œil lisible, queue fourchue orange, petit aileron dorsal.
Aucun modèle ni rig téléchargé : sphères, cônes et disques, reliés à des charnières et à des pivots.
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/poisson_volant.py

Images (512 px = 8 x 64 px, pixelisées ensuite) :
    nage_01..08    : battement de queue, nageoires qui vibrent (boucle)
    attaque_01..04 : bond hors de l'eau, corps cabré, nageoires déployées
    mort_01..06    : le corps reste horizontal et coule lentement, nageoires qui s'écartent
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
CENTRE_CADRE_X = -0.20  # la caméra regarde un peu vers la queue : le poisson tient la case

# plan des images : (numéro d'image Blender, nom du fichier)
PLAN = (
    [(f, f"nage_{f:02d}") for f in range(1, 9)]
    + [(8 + k, f"attaque_{k:02d}") for k in range(1, 5)]
    + [(12 + k, f"mort_{k:02d}") for k in range(1, 7)]
)
DERNIERE = 18


def construire(scene):
    """Pièces du poisson, avec leurs matériaux (rampes de art/palette.json)."""
    m_dos = ob.materiau("poisson_dos", "caoutchouc", bandes=(1, 2, 3, 4), rugosite=0.4)
    m_ventre = ob.materiau("poisson_ventre", "metal", bandes=(3, 4, 5, 5), rugosite=0.3)
    m_aile = ob.materiau("poisson_aile", "bulle", bandes=(2, 3, 4, 4), rugosite=0.5)
    m_queue = ob.materiau("poisson_queue", "palmes", bandes=(1, 2, 3, 4), rugosite=0.5)
    m_museau = ob.materiau("poisson_museau", "caoutchouc", bandes=(1, 2, 3, 3), rugosite=0.4)

    corps = ob.sphere((0.0, 0.0, 0.0), 0.5, m_dos, echelle=(1.25, 0.9, 0.7), nom="corps")

    # ventre argenté : une calotte claire sous le corps, visible sur le bord inférieur
    ventre = ob.sphere((0.02, -0.02, -0.22), 0.5, m_ventre, echelle=(1.00, 0.80, 0.14), nom="ventre")
    ob.parent(ventre, corps)

    # museau : petit cône pointé vers l'avant
    museau = ob.cone((0.66, 0.0, 0.0), 0.12, 0.20, m_museau, rotation=(0.0, math.radians(90), 0.0), nom="museau")
    ob.parent(museau, corps)

    # œil : blanc contrasté, pupille noire, côté caméra, sur la tête
    ob.oeil((0.40, -0.32, 0.10), 0.085, corps, pupille=0.62, nom="oeil")

    # aileron dorsal court
    dos = ob.cone((0.08, 0.0, 0.42), 0.10, 0.46, m_dos, nom="nageoire_dorsale")
    ob.parent(dos, corps)

    # queue fourchue : deux lobes dont la base est sur la charnière arrière du corps
    charniere_queue = ob.pivot(scene, "charniere_queue", (-0.62, 0.0, 0.0), corps)
    lobe_haut = ob.cone((-0.805, 0.0, 0.099), 0.14, 0.42, m_queue,
                        rotation=(0.0, math.radians(-62), 0.0), nom="lobe_queue_haut")
    lobe_bas = ob.cone((-0.805, 0.0, -0.099), 0.14, 0.42, m_queue,
                       rotation=(0.0, math.radians(-118), 0.0), nom="lobe_queue_bas")
    ob.parent(lobe_haut, charniere_queue)
    ob.parent(lobe_bas, charniere_queue)

    # nageoire pectorale : fine, en biais, comme une aile de poisson (pas un grand disque)
    charniere_aile = ob.pivot(scene, "charniere_aile", (0.12, -0.10, 0.06), corps)
    aile = ob.sphere((0.12, -0.10, 0.06), 0.5, m_aile, echelle=(0.82, 0.02, 0.10), nom="aile")
    aile.rotation_euler = (0.0, math.radians(-30), 0.0)
    ob.parent(aile, charniere_aile)
    return {"corps": corps, "queue": charniere_queue, "aile": charniere_aile}


def animer(p):
    """Clés de rotation autour de l'axe Y (plan de la caméra) : nage 1-8 (boucle), attaque 9-12, mort 13-18."""
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
    # mort : le corps reste presque horizontal et coule, les nageoires s'écartent, la queue pend
    for f, c, a, q, z in ((13, 0.00, 0.00, 0.00, 0.00), (14, 0.05, 0.15, 0.10, -0.03),
                          (15, 0.10, 0.30, -0.08, -0.07), (16, 0.14, 0.45, 0.06, -0.11),
                          (17, 0.16, 0.55, -0.04, -0.14), (18, 0.18, 0.60, 0.03, -0.16)):
        ob.cle(corps, f, rot=(0.0, c, 0.0), loc=(0.0, 0.0, z))
        ob.cle(aile, f, rot=(0.0, a, 0.0))
        ob.cle(queue, f, rot=(0.0, q, 0.0))


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
