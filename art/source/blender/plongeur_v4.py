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

import bmesh
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
        "verre": materiau("verre", "#0a2a3c", rugosite=0.03),   # vitre sombre bleutée
        "reflet": materiau("reflet", "#eafcff", rugosite=0.05),  # reflet clair sur la vitre
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


def membre(points, rayons, mat, nom, nseg=14, cotes=28, plis=None):
    """Membre continu : UNE surface balayée le long d'un chemin lisse (coude ou genou arrondi), rayon
    interpolé entre les points de contrôle. Pas de sphère ni de jointure : une seule surface, puis subdivision."""
    chemin = chemin_catmull(points, nseg)
    n = len(chemin)
    rayons_ech = []
    for i in range(n):
        j = min(i // nseg, len(points) - 2)
        t = (i - j * nseg) / nseg
        t = t * t * (3 - 2 * t)
        rayons_ech.append(rayons[j] + (rayons[j + 1] - rayons[j]) * t)
    rayons_ech[-1] = rayons[-1]
    bm = bmesh.new()
    anneaux = []
    normale_prec = None
    for i, p in enumerate(chemin):
        a = chemin[max(i - 1, 0)]
        b = chemin[min(i + 1, n - 1)]
        tangente = (b - a).normalized()
        if normale_prec is None:
            nrm = tangente.cross(Vector((0.0, 0.0, 1.0)))
            if nrm.length < 1e-4:
                nrm = tangente.cross(Vector((1.0, 0.0, 0.0)))
            nrm.normalize()
        else:
            nrm = normale_prec - tangente * normale_prec.dot(tangente)
            nrm.normalize()
        normale_prec = nrm
        bn = tangente.cross(nrm).normalized()
        r = rayons_ech[i]
        anneau = []
        for k in range(cotes):
            th = 2.0 * math.pi * k / cotes
            rk = r
            if plis:
                # plis de toile : creux doux et étroits, répartis autour de la section (pas de bosse)
                nb, amp = plis
                rk = r * (1.0 - amp * (0.5 + 0.5 * math.cos(nb * th)) ** 6)
            anneau.append(bm.verts.new(p + rk * (math.cos(th) * nrm + math.sin(th) * bn)))
        anneaux.append(anneau)
    for i in range(n - 1):
        A, B = anneaux[i], anneaux[i + 1]
        for k in range(cotes):
            bm.faces.new((A[k], A[(k + 1) % cotes], B[(k + 1) % cotes], B[k]))
    bm.faces.new(anneaux[0][::-1])
    bm.faces.new(anneaux[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    _lisser(o)
    _modifieurs(o, 0.0, 2, 0.0)
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
    # vitre posée DEVANT le casque (sa face avant dépasse celle du casque) : plus de casque qui perce le verre
    ellipsoide((0.0, -0.50, 1.90), 0.30, (1.0, 0.2, 1.0), m["verre"], nom="hublot_verre")
    tore((0.0, -0.56, 1.90), 0.315, 0.05, cadre_fer, rotation=(math.pi / 2, 0.0, 0.0), nom="hublot_cadre")
    # reflet : petite tache claire en haut à gauche de la vitre, posée juste devant elle
    ellipsoide((-0.13, -0.555, 2.05), 0.05, (1.0, 0.25, 0.9), m["reflet"], nom="reflet_vitre")
    for x in (-0.12, 0.12):
        cylindre((x, -0.60, 1.90), 0.018, 0.52, cadre_fer, biseau=0.0, nom="barre_v")
    cylindre((0.0, -0.60, 1.90), 0.018, 0.52, cadre_fer, rotation=(0.0, math.pi / 2, 0.0), biseau=0.0,
             nom="barre_h")
    boulon = ellipsoide((0.0, 0.0, 0.0), 0.028, (1.0, 1.0, 0.7), m["acier"], nom="boulon_modele")
    boulon.location = (0.0, 0.0, -10.0)
    # boulons posés sur la face avant du cadre (le centre du tore est à -0,47, son rayon de tube 0,05)
    cercle_hublot = [(0.315 * math.cos(k * math.pi / 4), -0.605, 1.90 + 0.315 * math.sin(k * math.pi / 4))
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
    # tonneau plein et lisse : une seule surface (bassin, ventre, poitrine), section élargie en X
    torse = membre([(0.0, 0.0, 0.84), (0.0, 0.0, 1.10), (0.0, 0.0, 1.36)], [0.42, 0.50, 0.44], m["kaki"],
                   "torse", nseg=10, cotes=40, plis=(7, 0.05))
    torse.scale = (1.12, 0.84, 1.0)
    _appliquer(torse)
    boite((0.0, -0.40, 1.12), (0.035, 0.03, 0.62), cadre_fer, biseau=0.0, nom="fermeture")
    # coutures horizontales fines, sur la toile
    tore((0.0, 0.0, 1.27), 0.52, 0.012, m["kaki_sombre"], echelle=(1.0, 0.84, 1.0), nom="couture")
    # --- ceinture de cuir brun, boucle métallique
    tore((0.0, 0.0, 1.0), 0.56, 0.058, m["cuir"], echelle=(1.05, 0.84, 1.0), nom="ceinture")
    boite((0.0, -0.47, 1.0), (0.14, 0.035, 0.11), m["laiton"], biseau=0.012, nom="boucle")

    # --- bras courts et épais, manchettes sombres, gros gants caoutchouc avec pouce
    for s in (-1.0, 1.0):
        epaule = (0.50 * s, 0.0, 1.20)
        coude = (0.74 * s, -0.10, 0.90)
        poignet = (0.80 * s, -0.14, 0.64)
        membre([epaule, coude, poignet], [0.19, 0.155, 0.145], m["kaki"], "bras")
        d = (Vector(poignet) - Vector(coude)).normalized()
        # manchette de toile : la fin de la manche, avec une bande sombre ; elle prolonge le bras
        membre([Vector(poignet) - d * 0.14, Vector(poignet) + d * 0.02], [0.160, 0.170],
               m["manchette"], "manchette", nseg=2)
        # gant en mitaine : l'éllipsoïde part du poignet, son bord recouvre le bord de la manchette
        gant_c = Vector(poignet) + d * 0.12
        gant = ellipsoide(gant_c, 0.17, (1.0, 0.92, 1.25), m["gant"], biseau=0.02, nom="gant")
        gant.rotation_mode = "QUATERNION"
        gant.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(d)
        # pouce : un petit doigt du côté intérieur et devant, qui fait la mitaine
        pouce_c = gant_c + Vector((-0.13 * s, -0.11, 0.02))
        ellipsoide(pouce_c, 0.075, (0.9, 1.15, 0.8), m["gant"], nom="pouce")

    # --- jambes courtes, genouillères sombres, grosses bottes lourdes
    for s in (-1.0, 1.0):
        hanche = (0.20 * s, 0.0, 0.84)
        genou = (0.24 * s, -0.02, 0.54)
        cheville = (0.26 * s, 0.0, 0.24)
        membre([hanche, genou, cheville], [0.21, 0.165, 0.14], m["kaki_sombre"], "jambe")
        # genouillère : plaque arrondie collée à l'avant du genou (enfoncée de 2 cm dans la jambe)
        ellipsoide((genou[0], genou[1] - 0.165, genou[2]), 0.13, (1.0, 0.4, 0.95), m["genouillere"],
                   biseau=0.02, nom="genouillere")
        ellipsoide((0.27 * s, -0.07, 0.13), 0.2, (0.95, 1.4, 0.72), m["botte"], biseau=0.03, nom="botte")

    # --- bouteille de plongée violet-bleu, derrière l'épaule gauche (lointaine)
    # bouteille : dépasse derrière l'épaule lointaine (gauche), penchée vers l'arrière ; son col reçoit la corde
    cylindre((-0.86, 0.45, 1.55), 0.14, 0.66, m["bouteille"], rotation=(0.0, -0.25, 0.0), biseau=0.05,
             nom="bouteille")
    cylindre((-0.955, 0.45, 1.92), 0.05, 0.12, m["bouteille"], rotation=(0.0, -0.25, 0.0), biseau=0.02,
             nom="col_bouteille")

    # --- tuyau d'air en corde torsadée, sortant du sommet du casque, grande boucle vers l'arrière
    # une seule corde épaisse : sort du sommet du casque, monte, fait une grande boucle lisse vers l'arrière,
    # puis redescend jusqu'au col de la bouteille (derrière l'épaule lointaine). Trois brins serrés.
    cordon([(0.0, 0.05, 2.40), (0.03, 0.30, 2.86), (0.0, 0.80, 3.10), (-0.10, 1.25, 2.85), (-0.22, 1.42, 2.25),
            (-0.45, 1.20, 1.85), (-0.66, 0.78, 1.95), (-0.95, 0.45, 2.02)],
           rayon_helice=0.095, rayon_fil=0.085, torsions=7.0, scene=scene, mat=m["corde"], nom="tuyau_air")


# ------------------------------------------------------------------ scène
def eclairer(scene):
    """Clé douce haut-gauche (grande source, reflets du laiton en haut à gauche) et lumière de contour
    douce côté opposé. Les sources sont des surfaces carrées : ombres et reflets doux, pas de tranchant."""
    def surface(nom, direction_vers_lumiere, distance, taille, energie, teinte):
        l = bpy.data.lights.new(nom, "AREA")
        l.energy = energie
        l.color = teinte
        l.shape = "SQUARE"
        l.size = taille
        o = bpy.data.objects.new(nom, l)
        scene.collection.objects.link(o)
        d = Vector(direction_vers_lumiere).normalized()
        o.location = CIBLE + d * distance
        o.rotation_mode = "QUATERNION"
        # une surface émet le long de son -Z : on la tourne vers le centre de la scène
        o.rotation_quaternion = Vector((0.0, 0.0, -1.0)).rotation_difference(-d)
    surface("clef_haut_gauche", (-0.50, -0.40, 1.00), 6.0, 3.0, 260.0, (1.0, 0.93, 0.80))
    surface("contour_doux", (0.6, 0.7, 0.45), 6.0, 4.0, 70.0, (0.66, 0.82, 1.0))
    monde = bpy.data.worlds.new("monde")
    monde.use_nodes = True
    fond = monde.node_tree.nodes["Background"]
    fond.inputs["Color"].default_value = (0.42, 0.46, 0.50, 1.0)
    fond.inputs["Strength"].default_value = 0.7
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
