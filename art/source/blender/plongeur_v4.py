"""
plongeur_v4.py - scaphandrier de dessin animé, construit de zéro dans Blender (v4, refonte complète).

Étape 1 (ce fichier) : rendu HAUTE RÉSOLUTION sans pixelisation, trois quarts de face (azimut 35°,
élévation 15°), éclairage principal haut-gauche, contre-jour doux, fond transparent.
Modélisation : sphères et cylindres ÉTIRÉS, biseautés (Bevel) et lissés (Subdivision), déplacement
par bruit (plis de toile), tores pour les anneaux, boulons par instances (objets liés au même maillage),
cordon torsadé par trois courbes hélicoïdales biseautées. Matériaux PBR (laiton métallique, toile mate,
cuir, caoutchouc, verre). Aucun modèle ni rig téléchargé.

    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v4.py

Variables : PLONGEUR_SORTIE (dossier de rendu), PLONGEUR_RES (défaut 768), PLONGEUR_ECHANTILLONS (défaut 64).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ID = "plongeur_v4"
SORTIE = os.environ.get("PLONGEUR_SORTIE", os.path.join(ROOT, "art", "rendu", ID))
BLEND = os.path.join(HERE, ID + ".blend")
RES = int(os.environ.get("PLONGEUR_RES", "768"))
ECHANTILLONS = int(os.environ.get("PLONGEUR_ECHANTILLONS", "64"))
AZIMUT = 35.0       # depuis la face vers +X
ELEVATION = 15.0
CIBLE = Vector((0.0, 0.1, 1.55))
CADRE = 3.9         # largeur du cadre en unités (ortho) : place le tuyau au-dessus du casque


def srgb(hexa):
    """Couleur hexadécimale sRGB -> linéaire (Blender travaille en linéaire)."""
    h = hexa.lstrip("#")
    return tuple((int(h[k:k + 2], 16) / 255.0) ** 2.2 for k in (0, 2, 4))


# ------------------------------------------------------------------ matériaux PBR
def materiau(nom, hexa, metal=0.0, rugosite=0.6):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    r, g, bl = srgb(hexa)
    b.inputs["Base Color"].default_value = (r, g, bl, 1.0)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rugosite
    return m


def materiaux():
    return {
        "laiton": materiau("laiton", "#c99a3a", metal=1.0, rugosite=0.26),
        "acier": materiau("acier", "#7b8a92", metal=1.0, rugosite=0.34),
        "verre": materiau("verre", "#1c5566", rugosite=0.04),
        "kaki": materiau("kaki", "#8c7c52", rugosite=0.86),
        "kaki_sombre": materiau("kaki_sombre", "#5f5538", rugosite=0.86),
        "gant": materiau("gant", "#2b3170", rugosite=0.42),
        "manchette": materiau("manchette", "#1c1830", rugosite=0.5),
        "botte": materiau("botte", "#15122a", rugosite=0.5),
        "genouillere": materiau("genouillere", "#1d1a33", rugosite=0.55),
        "cuir": materiau("cuir", "#5a2f18", rugosite=0.5),
        "corde": materiau("corde", "#cbb88c", rugosite=0.72),
        "bouteille": materiau("bouteille", "#2e2c6a", rugosite=0.2),
    }


# ------------------------------------------------------------------ outils de forme
def _appliquer(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def _lisser(o):
    for p in o.data.polygons:
        p.use_smooth = True


def _modifieurs(o, biseau=0.0, niveau=2, plis=0.0):
    if biseau > 0.0:
        b = o.modifiers.new("biseau", "BEVEL")
        b.width = biseau
        b.segments = 4
    s = o.modifiers.new("lissage", "SUBSURF")
    s.levels = 1
    s.render_levels = niveau
    if plis > 0.0:
        t = bpy.data.textures.new(o.name + "_plis", "CLOUDS")
        t.noise_scale = 0.22
        d = o.modifiers.new("plis", "DISPLACE")
        d.texture = t
        d.strength = plis
        d.mid_level = 0.5


def ellipsoide(centre, rayon, echelle, mat, biseau=0.0, plis=0.0, nom="forme"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rayon, segments=40, ring_count=20, location=centre)
    o = bpy.context.object
    o.name = nom
    o.scale = echelle
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _modifieurs(o, biseau, 2, plis)
    return o


def capsule(a, b, rayon, mat, nom="membre", plis=0.0):
    """Membre : cylindre orienté de a vers b, à bouts arrondis (biseau large)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=rayon, depth=d.length, vertices=28, location=(a + b) / 2)
    o = bpy.context.object
    o.name = nom
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized())
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _modifieurs(o, rayon * 0.72, 2, plis)
    return o


def tore(centre, grand_r, petit_r, mat, rotation=(0.0, 0.0, 0.0), echelle=(1.0, 1.0, 1.0), nom="anneau"):
    bpy.ops.mesh.primitive_torus_add(major_radius=grand_r, minor_radius=petit_r, major_segments=56,
                                     minor_segments=16, location=centre, rotation=rotation)
    o = bpy.context.object
    o.name = nom
    o.scale = echelle
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _modifieurs(o, 0.0, 2, 0.0)
    return o


def boite(centre, taille, mat, biseau=0.04, rotation=(0.0, 0.0, 0.0), nom="boite"):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centre, rotation=rotation)
    o = bpy.context.object
    o.name = nom
    o.scale = taille
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _modifieurs(o, biseau, 2, 0.0)
    return o


def cylindre(centre, rayon, longueur, mat, rotation=(0.0, 0.0, 0.0), biseau=0.03, nom="tube"):
    bpy.ops.mesh.primitive_cylinder_add(radius=rayon, depth=longueur, vertices=32, location=centre,
                                        rotation=rotation)
    o = bpy.context.object
    o.name = nom
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _modifieurs(o, biseau, 2, 0.0)
    return o


def orienter(o, direction):
    """Aligne l'axe Z d'un objet (torus, cylindre) sur une direction."""
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(direction).normalized())
    return o


def instancier(master, positions, scene, nom):
    """Boulons par instances : chaque copie partage le même maillage (pas de duplication de géométrie)."""
    objets = []
    for k, p in enumerate(positions):
        o = bpy.data.objects.new(f"{nom}_{k}", master.data)
        o.location = p
        scene.collection.objects.link(o)
        objets.append(o)
    return objets


# ------------------------------------------------------------------ cordon torsadé
def chemin_catmull(points, n_par_segment):
    """Courbe lisse (Catmull-Rom) passant par les points de contrôle."""
    pts = [Vector(p) for p in points]
    pts = [pts[0]] + pts + [pts[-1]]
    sortie = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n_par_segment):
            t = k / n_par_segment
            t2, t3 = t * t, t * t * t
            sortie.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    sortie.append(Vector(pts[-2]))
    return sortie


def cordon(points, rayon_helice, rayon_fil, torsions, scene, mat, nom="cordon"):
    """Trois brins en hélice autour du chemin : un cordon torsadé (courbes biseautées)."""
    chemin = chemin_catmull(points, 24)
    n = len(chemin)
    objets = []
    for k in range(3):
        brin = []
        for i, p in enumerate(chemin):
            a = chemin[max(i - 1, 0)]
            b = chemin[min(i + 1, n - 1)]
            t = (b - a).normalized()
            nrm = t.cross(Vector((0.0, 0.0, 1.0)))
            if nrm.length < 1e-4:
                nrm = t.cross(Vector((1.0, 0.0, 0.0)))
            nrm.normalize()
            bn = t.cross(nrm).normalized()
            phi = 2.0 * math.pi * torsions * i / n + 2.0 * math.pi * k / 3.0
            brin.append(p + rayon_helice * (math.cos(phi) * nrm + math.sin(phi) * bn))
        c = bpy.data.curves.new(f"{nom}_{k}", "CURVE")
        c.bevel_depth = rayon_fil
        c.bevel_resolution = 3
        c.use_fill_caps = True
        s = c.splines.new("POLY")
        s.points.add(len(brin) - 1)
        for j, p in enumerate(brin):
            s.points[j].co = (p.x, p.y, p.z, 1.0)
        s.use_smooth = True
        c.materials.append(mat)
        o = bpy.data.objects.new(f"{nom}_{k}", c)
        scene.collection.objects.link(o)
        objets.append(o)
    return objets


# ------------------------------------------------------------------ construction du scaphandrier
def construire(scene):
    m = materiaux()
    cadre_fer = m["acier"]

    # --- casque : grande sphère laiton patiné, calotte légèrement aplatie sur le dessus
    ellipsoide((0.0, 0.0, 1.86), 0.52, (1.0, 1.0, 1.0), m["laiton"], nom="casque")
    ellipsoide((0.0, 0.0, 2.27), 0.20, (1.0, 1.0, 0.45), m["laiton"], nom="calotte")
    cylindre((0.0, 0.02, 2.42), 0.085, 0.13, m["laiton"], nom="raccord_sommet")
    # --- grand hublot avant : verre bleuté, cadre gris épais, grille de barres, boulons
    ellipsoide((0.0, -0.44, 1.90), 0.30, (1.0, 0.24, 1.0), m["verre"], nom="hublot_verre")
    tore((0.0, -0.47, 1.90), 0.315, 0.05, cadre_fer, rotation=(math.pi / 2, 0.0, 0.0), nom="hublot_cadre")
    for x in (-0.12, 0.12):
        cylindre((x, -0.52, 1.90), 0.018, 0.52, cadre_fer, biseau=0.0, nom="barre_v")
    cylindre((0.0, -0.52, 1.90), 0.018, 0.52, cadre_fer, rotation=(0.0, math.pi / 2, 0.0), biseau=0.0,
             nom="barre_h")
    boulon = ellipsoide((0.0, 0.0, 0.0), 0.028, (1.0, 1.0, 0.7), m["acier"], nom="boulon_modele")
    boulon.location = (0.0, 0.0, -10.0)
    # boulons posés sur la face avant du cadre (le centre du tore est à -0,47, son rayon de tube 0,05)
    cercle_hublot = [(0.315 * math.cos(k * math.pi / 4), -0.515, 1.90 + 0.315 * math.sin(k * math.pi / 4))
                     for k in range(8)]
    instancier(boulon, cercle_hublot, scene, "boulon_hublot")
    # --- petit hublot rond sur le côté : cadre laiton
    tore((0.49, -0.18, 1.82), 0.12, 0.03, m["laiton"], rotation=(0.0, math.pi / 2, 0.0), nom="hublot_cote_cadre")
    cylindre((0.485, -0.18, 1.82), 0.10, 0.03, m["verre"], rotation=(0.0, math.pi / 2, 0.0), biseau=0.0,
             nom="hublot_cote_verre")
    cercle_cote = [(0.49, -0.18 + 0.15 * math.cos(k * math.pi / 3), 1.82 + 0.15 * math.sin(k * math.pi / 3))
                   for k in range(6)]
    instancier(boulon, cercle_cote, scene, "boulon_cote")
    # --- collerette laiton avec rangée de boulons, entre casque et combinaison
    tore((0.0, 0.0, 1.36), 0.47, 0.075, m["laiton"], nom="collerette")
    anneau_boulons = [(0.47 * math.cos(k * 2 * math.pi / 12), 0.47 * math.sin(k * 2 * math.pi / 12), 1.435)
                      for k in range(12)]
    instancier(boulon, anneau_boulons, scene, "boulon_collerette")

    # --- torse court et arrondi, toile kaki avec plis, fermeture centrale, bassin
    ellipsoide((0.0, 0.0, 1.12), 0.5, (0.56, 0.42, 0.42), m["kaki"], plis=0.035, nom="torse")
    ellipsoide((0.0, 0.0, 0.84), 0.46, (1.0, 0.72, 0.42), m["kaki_sombre"], plis=0.03, nom="bassin")
    boite((0.0, -0.42, 1.12), (0.035, 0.03, 0.66), cadre_fer, biseau=0.0, nom="fermeture")
    # --- ceinture de cuir brun, boucle métallique
    tore((0.0, 0.0, 1.0), 0.5, 0.06, m["cuir"], echelle=(1.05, 0.82, 1.0), nom="ceinture")
    boite((0.0, -0.44, 1.0), (0.14, 0.035, 0.11), m["laiton"], biseau=0.012, nom="boucle")

    # --- bras courts et épais, manchettes sombres, gros gants caoutchouc avec pouce
    for s in (-1.0, 1.0):
        epaule = (0.52 * s, 0.0, 1.18)
        coude = (0.74 * s, -0.08, 0.90)
        poignet = (0.80 * s, -0.14, 0.64)
        ellipsoide(epaule, 0.19, (1.0, 1.0, 1.0), m["kaki"], nom="epaule")
        capsule(epaule, coude, 0.165, m["kaki"], nom="bras_sup", plis=0.02)
        capsule(coude, poignet, 0.15, m["kaki"], nom="avant_bras", plis=0.02)
        direction = Vector(poignet) - Vector(coude)
        cuff = tore(Vector(poignet) + direction.normalized() * 0.03, 0.158, 0.04, m["manchette"], nom="manchette")
        orienter(cuff, direction)
        paume = (poignet[0] + 0.03 * s, poignet[1] - 0.10, poignet[2] - 0.20)
        ellipsoide(paume, 0.21, (0.92, 0.82, 1.12), m["gant"], biseau=0.02, nom="gant")
        ellipsoide((paume[0] - 0.12 * s, paume[1] - 0.14, paume[2] + 0.02), 0.085, (0.9, 1.15, 0.8),
                   m["gant"], nom="pouce")

    # --- jambes courtes, genouillères sombres, grosses bottes lourdes
    for s in (-1.0, 1.0):
        hanche = (0.20 * s, 0.0, 0.84)
        genou = (0.24 * s, -0.02, 0.54)
        cheville = (0.26 * s, 0.0, 0.24)
        capsule(hanche, genou, 0.19, m["kaki_sombre"], nom="cuisse", plis=0.025)
        ellipsoide((genou[0], genou[1] - 0.2, genou[2]), 0.16, (1.0, 0.5, 1.0), m["genouillere"], nom="genouillere")
        capsule(genou, cheville, 0.16, m["kaki_sombre"], nom="tibia", plis=0.02)
        ellipsoide((0.27 * s, -0.07, 0.13), 0.2, (0.95, 1.4, 0.72), m["botte"], biseau=0.03, nom="botte")

    # --- bouteille de plongée violet-bleu, derrière l'épaule gauche (lointaine)
    cylindre((-0.66, 0.36, 1.50), 0.13, 0.62, m["bouteille"], rotation=(0.0, -0.12, 0.0), biseau=0.05,
             nom="bouteille")
    cylindre((-0.66, 0.36, 1.86), 0.05, 0.12, m["bouteille"], rotation=(0.0, -0.12, 0.0), biseau=0.02,
             nom="col_bouteille")

    # --- tuyau d'air en corde torsadée, sortant du sommet du casque, grande boucle vers l'arrière
    cordon([(0.0, 0.05, 2.40), (0.06, 0.22, 2.84), (0.0, 0.66, 3.10), (-0.02, 1.06, 2.90), (0.0, 1.26, 2.36),
            (0.05, 1.10, 1.80), (0.22, 0.80, 1.38), (0.46, 0.46, 1.16)],
           rayon_helice=0.055, rayon_fil=0.032, torsions=5.0, scene=scene, mat=m["corde"], nom="tuyau_air")


# ------------------------------------------------------------------ scène
def eclairer(scene):
    """Clef douce haut-gauche (sur le cadre : gauche = -X-Y, haut), contre-jour froid bas-droite."""
    def soleil(nom, direction_vers_lumiere, energie, teinte):
        l = bpy.data.lights.new(nom, "SUN")
        l.energy = energie
        l.color = teinte
        o = bpy.data.objects.new(nom, l)
        scene.collection.objects.link(o)
        o.rotation_mode = "QUATERNION"
        # un soleil émet le long de son -Z : on le tourne pour qu'il vienne de la direction voulue
        o.rotation_quaternion = Vector((0.0, 0.0, -1.0)).rotation_difference(
            -Vector(direction_vers_lumiere).normalized())
    soleil("clef_haut_gauche", (-0.27, -0.66, 0.90), 4.0, (1.0, 0.93, 0.80))
    soleil("contre_jour", (0.6, 0.7, 0.45), 0.8, (0.62, 0.80, 1.0))
    monde = bpy.data.worlds.new("monde")
    monde.use_nodes = True
    fond = monde.node_tree.nodes["Background"]
    fond.inputs["Color"].default_value = (0.42, 0.46, 0.50, 1.0)
    fond.inputs["Strength"].default_value = 0.9
    scene.world = monde


def camera(scene):
    cam = bpy.data.cameras.new("Camera")
    cam.type = "ORTHO"
    cam.ortho_scale = CADRE
    o = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(o)
    az, el = math.radians(AZIMUT), math.radians(ELEVATION)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    o.location = CIBLE + d * 10.0
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (-d).normalized().to_track_quat("-Z", "Y")
    scene.camera = o


def reglages(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RES
    scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.eevee.taa_render_samples = ECHANTILLONS


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    construire(scene)
    eclairer(scene)
    camera(scene)
    reglages(scene)
    os.makedirs(SORTIE, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    chemin = os.path.join(SORTIE, "hd_base.png")
    if os.path.exists(chemin):
        os.remove(chemin)
    scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(chemin):
        sys.exit("rendu absent : " + chemin)
    print("RENDU", chemin, os.path.getsize(chemin), "octets", flush=True)


main()
