"""
tuileset_biome.py - tuileset autotile à 47 cases d'un biome (M3), construit dans Blender.

Pour chaque configuration de voisinage (règle « blob 47 ») : une tuile est une dalle de matière
(bruit + paliers de la palette) dont les coins sont biseautés là où il n'y a pas de voisin, et
échancrés là où deux voisins se rejoignent sans leur coin diagonal. Le script refait toutes les
tuiles de zéro et écrit :
    art/rendu/tuileset/<biome>/tuile_01.png ... tuile_47.png     (128 px, pixelisées ensuite à 16 px)
Variable d'environnement : BIOME = radeau_surface | recif_peu_profond.
Lancement :  BIOME=recif_peu_profond /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/tuileset_biome.py
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_blender as ob  # noqa: E402

BIOME = os.environ.get("BIOME", "recif_peu_profond")
RAMPE = {"radeau_surface": "ocre", "recif_peu_profond": "recif"}[BIOME]
ROOT = ob.ROOT
SORTIE = os.path.join(ROOT, "art", "rendu", "tuileset", BIOME)
RES = 128
ECHANTILLONS = int(os.environ.get("TUILE_ECHANTILLONS", "24"))
C = 0.24      # taille des chanfreins et des échancrures (fraction de la case)

# bits du voisinage : N=1 NE=2 E=4 SE=8 S=16 SW=32 W=64 NW=128
N, NE, E, SE, S, SW, W, NW = 1, 2, 4, 8, 16, 32, 64, 128


def reduire(m):
    """Règle blob 47 : un coin diagonal ne compte que si ses deux côtés voisins sont présents."""
    if not (m & N) or not (m & E):
        m &= ~NE
    if not (m & S) or not (m & E):
        m &= ~SE
    if not (m & S) or not (m & W):
        m &= ~SW
    if not (m & N) or not (m & W):
        m &= ~NW
    return m


def masques_47():
    return sorted({reduire(m) for m in range(256)})


def contour(m):
    """Points (u, v) du contour de la tuile, dans le sens horaire, pour un masque réduit."""
    h = 0.5
    # coins dans le sens horaire : haut-gauche, haut-droite, bas-droite, bas-gauche
    coins = [
        # (x, y), voisins des deux côtés, diagonale, point sur le côté d'arrivée, point sur le côté de départ
        ((-h, h), (m & N, m & W), (m & NW), (-h + C, h), (-h, h - C)),
        ((h, h), (m & N, m & E), (m & NE), (h, h - C), (h - C, h)),
        ((h, -h), (m & S, m & E), (m & SE), (h - C, -h), (h, -h + C)),
        ((-h, -h), (m & S, m & W), (m & SW), (-h, -h + C), (-h + C, -h)),
    ]
    pts = []
    for (x, y), (e1, e2), d, arrivee, depart in coins:
        sx = 1 if x > 0 else -1
        sy = 1 if y > 0 else -1
        if e1 and e2:
            if d:
                pts.append((x, y))
            else:      # coin rentrant : petite échancrure
                pts.extend([(x - sx * C, y), (x - sx * C, y - sy * C), (x, y - sy * C)])
        else:          # coin extérieur : chanfrein
            pts.extend([arrivee, depart])
    return pts


def dalle(masque, nom):
    """Crée une dalle : polygone dans le plan XZ, épaisseur le long de Y, biseau léger."""
    m = bpy.data.meshes.new(nom)
    o = bpy.data.objects.new(nom, m)
    bpy.context.collection.objects.link(o)
    bm = bmesh.new()
    pts = contour(masque)
    verts = [bm.verts.new((u, 0.0, v)) for u, v in pts]
    bm.faces.new(verts)
    bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    bmesh.ops.translate(bm, verts=[v for v in bm.verts if abs(v.co.y) > 1e-6], vec=(0.0, 0.42, 0.0))
    bm.normal_update()
    bm.to_mesh(m)
    bm.free()
    o.data.materials.append(ob.materiau_matiere(nom, RAMPE))
    mod = o.modifiers.new("biseau", "BEVEL")
    mod.width = 0.03
    mod.segments = 2
    return o


def main():
    os.makedirs(SORTIE, exist_ok=True)
    masques = masques_47()
    assert len(masques) == 47, len(masques)
    for k, masque in enumerate(masques, 1):
        scene = ob.scene_vide()
        dalle(masque, f"tuile_{k:02d}")
        ob.eclairer(scene)
        ob.camera(scene, 1.2, centre=(0.0, 0.0, 0.0))
        ob.reglages(scene, RES, echantillons=ECHANTILLONS)
        chemin = os.path.join(SORTIE, f"tuile_{k:02d}.png")
        scene.render.filepath = chemin
        ob.rendre(scene, chemin)
    with open(os.path.join(SORTIE, "masques.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(f"tuile_{k:02d} {m}" for k, m in enumerate(masques, 1)) + "\n")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ob.HERE, f"tuileset_{BIOME}.blend"))


main()
