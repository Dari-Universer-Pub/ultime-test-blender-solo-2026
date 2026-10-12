"""
plongeur_v5_dc.py - scaphandrier rendu DIRECTEMENT à la taille finale (112 px, héros de 72 px), méthode « Dead Cells ».

Le modèle est lu sous une lumière plate par paliers : chaque matière (laiton, toile, caoutchouc, cuir, verre,
acier, corde, bouteille) a une rampe de 3 ou 4 tons de la palette, choisie par l'orientation de la surface
par rapport à la lumière haut-gauche. Pas de spéculaire, pas de réflexion d'environnement, pas de filtre.
Les détails sont peints par face dans un attribut (DET : code de palette), pas en géométrie.

    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v5_dc.py
Variables : PLONGEUR_SORTIE, PLONGEUR_RES (112), PLONGEUR_CADRE (4.5), PLONGEUR_ECHANTILLONS (1),
PLONGEUR_IDENTITE=1 (carte d'identité des matières et des membres).
"""
import math
import os
import re
import json
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ID = "plongeur_v5_dc"
SORTIE = os.environ.get("PLONGEUR_SORTIE", os.path.join(ROOT, "art", "rendu", ID))
BLEND = os.path.join(HERE, ID + ".blend")
RES = int(os.environ.get("PLONGEUR_RES", "112"))
ECHANTILLONS = int(os.environ.get("PLONGEUR_ECHANTILLONS", "1"))
AZIMUT = 35.0       # depuis la face vers +X
ELEVATION = 15.0
CIBLE = Vector((0.0, 0.1, 1.55))
CADRE = float(os.environ.get("PLONGEUR_CADRE", "4.5"))   # largeur du cadre (unités) : tuyau au-dessus du casque
IDENTITE = os.environ.get("PLONGEUR_IDENTITE") == "1"    # carte d'identité des membres (pixelisation)


def srgb(hexa):
    """Couleur hexadécimale sRGB -> linéaire (Blender travaille en linéaire) : fonction exacte de l'sRGB,
    pour qu'une couleur plate ressorte à l'identique au rendu (la carte d'identité compare des couleurs exactes)."""
    h = hexa.lstrip("#")
    def lin(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(lin(int(h[k:k + 2], 16)) for k in (0, 2, 4))


# ------------------------------------------------------------------ matériaux PBR
# ------------------------------------------------------------------ palette et lumière plate
# 8 tons par famille (du plus sombre au plus clair) : 8 x 8 + 2 contours = 66 couleurs (64 à 96)
DC_PALETTE = {
    "laiton": ["#3a2506", "#5e3d0a", "#8a5a12", "#b07a1e", "#d09a2c", "#e8b84a", "#f6d874", "#fff0a8"],
    "toile": ["#3e3026", "#5f4c3a", "#8a7054", "#b29673", "#cdb48e", "#e2cfa8", "#f1e4c4", "#fbf4e0"],
    "cuir": ["#2a1409", "#4a2412", "#6e3a1c", "#94532c", "#b87040", "#d48a58", "#e8a77a", "#f5c49c"],
    "caoutchouc": ["#0c0a1e", "#16133a", "#221d52", "#2f2a6a", "#3e3885", "#5149a0", "#6a63b8", "#8a84cc"],
    "verre": ["#040d14", "#081a26", "#0f2c3c", "#17415a", "#22607a", "#3486a0", "#5aaec4", "#c8eef6"],
    "acier": ["#1a2026", "#262e36", "#34404a", "#46545f", "#5c6b77", "#748592", "#93a2ad", "#bccad2"],
    "corde": ["#4a4128", "#6a5c38", "#8c7a4e", "#ae9a64", "#c9b47e", "#dccb9a", "#eee2bc", "#fbf6e2"],
    "bouteille": ["#0e0a22", "#17133a", "#211d52", "#2d2868", "#3c3680", "#4f4898", "#6a64b0", "#8c88c8"],
    "contour": ["#120c0a", "#1f1714"],
}
# matière -> (famille, tons utilisés du plus sombre au plus clair) : 3 ou 4 paliers par matière
DC_MATIERES = {
    "laiton": ("laiton", [1, 3, 5, 7]),
    "acier": ("acier", [1, 3, 5, 6]),
    "verre": ("verre", [0, 2, 4, 6]),
    "kaki": ("toile", [2, 4, 5, 7]),
    "kaki_sombre": ("toile", [1, 3, 4, 6]),
    "gant": ("caoutchouc", [1, 3, 5, 7]),
    "manchette": ("caoutchouc", [0, 1, 2, 4]),
    "botte": ("caoutchouc", [0, 1, 2, 3]),
    "genouillere": ("caoutchouc", [0, 2, 3, 4]),
    "cuir": ("cuir", [1, 3, 4, 6]),
    "corde": ("corde", [1, 3, 5, 7]),
    "bouteille": ("bouteille", [1, 3, 5, 7]),
}
LUMIERE_HG = Vector((-0.27, -0.66, 0.90)).normalized()   # lumière unique, haut-gauche (monde)
SEUILS = [0.0, 0.3, 0.55, 0.8]                              # paliers sur (produit scalaire normal.lumière + 1) / 2


def materiau_dc(nom, famille, indices):
    """Matériau à paliers : orientation de la surface -> rampe CONSTANTE de tons de la palette -> émission.
    Un attribut de sommet DET (code de détail peint) remplace la rampe là où il est posé."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    geo = arbre.nodes.new("ShaderNodeNewGeometry")
    dot = arbre.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = tuple(LUMIERE_HG)
    plage = arbre.nodes.new("ShaderNodeMapRange")
    plage.inputs["From Min"].default_value = -1.0
    plage.inputs["From Max"].default_value = 1.0
    plage.inputs["To Min"].default_value = 0.0
    plage.inputs["To Max"].default_value = 1.0
    rampe = arbre.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.interpolation = "CONSTANT"
    tons = DC_PALETTE[famille]
    elements = rampe.color_ramp.elements
    elements[0].position = SEUILS[0]
    elements[0].color = (*srgb(tons[indices[0]]), 1.0)
    for pos, idx in zip(SEUILS[1:len(indices)], indices[1:]):
        e = elements.new(pos)
        e.color = (*srgb(tons[idx]), 1.0)
    # détail peint : DET porte un CODE (voir DETAIL_CODE). Une rampe CONSTANT ne sort que ses paliers :
    # une arête entre deux codes donne un autre ton de la palette, jamais une teinte intermédiaire.
    att_detail = arbre.nodes.new("ShaderNodeAttribute")
    att_detail.attribute_type = "GEOMETRY"
    att_detail.attribute_name = "DET"
    masque = arbre.nodes.new("ShaderNodeValToRGB")
    masque.color_ramp.interpolation = "CONSTANT"
    masque.color_ramp.elements[0].position = 0.0
    masque.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    masque.color_ramp.elements[1].position = 0.1
    masque.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    couleur_detail = arbre.nodes.new("ShaderNodeValToRGB")
    couleur_detail.color_ramp.interpolation = "CONSTANT"
    # la rampe par défaut a deux arrêts (noir, blanc) : on les retire tous avant de poser les paliers
    while len(couleur_detail.color_ramp.elements) > 1:
        couleur_detail.color_ramp.elements.remove(couleur_detail.color_ramp.elements[-1])
    paliers = [(0.1, DETAIL_COULEUR["acier"]), (0.4, DETAIL_COULEUR["verre_clair"]),
               (0.7, DETAIL_COULEUR["toile_ombre"]), (0.9, DETAIL_COULEUR["laiton"])]
    couleur_detail.color_ramp.elements[0].position = paliers[0][0]
    couleur_detail.color_ramp.elements[0].color = (*srgb(paliers[0][1]), 1.0)
    for pos, hexa in paliers[1:]:
        e = couleur_detail.color_ramp.elements.new(pos)
        e.color = (*srgb(hexa), 1.0)
    melange = arbre.nodes.new("ShaderNodeMix")
    melange.data_type = "RGBA"
    emission = arbre.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    arbre.links.new(geo.outputs["Normal"], dot.inputs[0])
    arbre.links.new(dot.outputs["Value"], plage.inputs["Value"])
    arbre.links.new(plage.outputs["Result"], rampe.inputs["Fac"])
    arbre.links.new(att_detail.outputs["Fac"], masque.inputs["Fac"])
    arbre.links.new(att_detail.outputs["Fac"], couleur_detail.inputs["Fac"])
    arbre.links.new(masque.outputs["Color"], melange.inputs["Factor"])
    arbre.links.new(rampe.outputs["Color"], melange.inputs[6])
    arbre.links.new(couleur_detail.outputs["Color"], melange.inputs[7])
    arbre.links.new(melange.outputs[2], emission.inputs["Color"])
    arbre.links.new(emission.outputs["Emission"], sortie.inputs["Surface"])
    return m


def materiaux():
    return {cle: materiau_dc(cle, famille, idx) for cle, (famille, idx) in DC_MATIERES.items()}


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
                nb, amp = plis[0], plis[1]
                zones = plis[2] if len(plis) > 2 else None
                if zones is None:
                    g = 1.0
                else:
                    # plis localisés : seulement autour des positions données (fraction du chemin)
                    u = i / max(n - 1, 1)
                    g = max(math.exp(-((u - c) / 0.08) ** 2) for c in zones)
                rk = r * (1.0 - amp * g * (0.5 + 0.5 * math.cos(nb * th)) ** 5)
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


# ------------------------------------------------------------------ détails peints (textures)
# couleur exacte de chaque détail (tons de la palette) et code écrit dans l'attribut DET
DETAIL_COULEUR = {"acier": "#748592", "verre_clair": "#c8eef6", "toile_ombre": "#5f4c3a", "laiton": "#8a5a12"}
DETAIL_CODE = {"acier": 0.25, "verre_clair": 0.55, "toile_ombre": 0.80, "laiton": 0.95}
ACIER_DETAIL = DETAIL_CODE["acier"]
VERRE_CLAIR = DETAIL_CODE["verre_clair"]
TOILE_OMBRE = DETAIL_CODE["toile_ombre"]
LAITON_DETAIL = DETAIL_CODE["laiton"]


def boulons_sur_anneau(centre, axe_u, axe_v, rayon, angles, demi, cote):
    """Prédicat : points d'un anneau (tore) proches des angles donnés, sur la moitié demandée."""
    def predicat(p):
        r, a = _anneau_angle(p, centre, axe_u, axe_v)
        return abs(r - rayon) < 0.05 and cote(p) and min(_proche_angle(a, t) for t in angles) < demi
    return predicat


def peindre(o, predicat, code):
    """Peint un détail dans la surface sans géométrie : DET = code du détail là où le prédicat (centre de
    la face, position monde) est vrai.
    L'attribut est PAR FACE (pas par sommet) : pas d'interpolation, donc une arête nette entre deux
    détails ou entre un détail et la matière, sans teinte intermédiaire."""
    me = o.data
    if "DET" not in me.attributes:
        me.attributes.new("DET", "FLOAT", "FACE")
    masque = me.attributes["DET"].data
    M = o.matrix_world
    n = 0
    for f in me.polygons:
        if predicat(M @ f.center):
            masque[f.index].value = code
            n += 1
    return n


def peindre_ligne(o, zone, cle_groupe, cle_tri, code):
    """Trace un trait d'1 face : dans chaque groupe de faces (cle_groupe) qui tombe dans la zone, on ne
    peint que la face la plus proche de la ligne (cle_tri minimal). Un trait fait ainsi une seule rangée
    de faces, donc 1 px à la taille finale, même quand les faces sont plus larges que le trait."""
    me = o.data
    if "DET" not in me.attributes:
        me.attributes.new("DET", "FLOAT", "FACE")
    masque = me.attributes["DET"].data
    M = o.matrix_world
    meilleurs = {}
    for f in me.polygons:
        c = M @ f.center
        if not zone(c):
            continue
        g = cle_groupe(c)
        if g not in meilleurs or cle_tri(c) < meilleurs[g][0]:
            meilleurs[g] = (cle_tri(c), f.index)
    for _, idx in meilleurs.values():
        masque[idx].value = code
    return len(meilleurs)


def _anneau_angle(p, centre, axe_u, axe_v):
    """Rayon et angle d'un point dans le plan d'un anneau (centre, deux axes orthonormés)."""
    d = p - Vector(centre)
    u, v = d.dot(axe_u), d.dot(axe_v)
    return math.hypot(u, v), math.atan2(v, u)


def _proche_angle(a, b):
    return abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)


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
    vitre = ellipsoide((0.0, -0.50, 1.90), 0.30, (1.0, 0.2, 1.0), m["verre"], nom="hublot_verre")
    cadre = tore((0.0, -0.56, 1.90), 0.315, 0.05, cadre_fer, rotation=(math.pi / 2, 0.0, 0.0), nom="hublot_cadre")
    # grille (deux barres verticales, une horizontale) et reflet : PEINTS dans la face avant de la vitre
    peindre(vitre, lambda p: p.y < -0.46 and (min(abs(p.x - 0.12), abs(p.x + 0.12)) < 0.035 and abs(p.z - 1.90) < 0.24
                                              or abs(p.z - 1.90) < 0.035 and abs(p.x) < 0.24), ACIER_DETAIL)
    peindre(vitre, lambda p: p.y < -0.46 and (p.x + 0.13) ** 2 + (p.z - 2.05) ** 2 < 0.06 ** 2, VERRE_CLAIR)
    # six boulons du cadre avant : peints sur l'anneau, à 60 degrés
    peindre(cadre, boulons_sur_anneau((0.0, -0.56, 1.90), Vector((1, 0, 0)), Vector((0, 0, 1)), 0.315,
                                      [k * math.pi / 3 for k in range(6)], 0.09, lambda p: p.y < -0.56), LAITON_DETAIL)
    # --- petit hublot rond sur le côté : cadre laiton, quatre boulons peints
    cote = tore((0.49, -0.18, 1.82), 0.12, 0.03, m["laiton"], rotation=(0.0, math.pi / 2, 0.0), nom="hublot_cote_cadre")
    cylindre((0.485, -0.18, 1.82), 0.10, 0.03, m["verre"], rotation=(0.0, math.pi / 2, 0.0), biseau=0.0,
             nom="hublot_cote_verre")
    peindre(cote, boulons_sur_anneau((0.49, -0.18, 1.82), Vector((0, 1, 0)), Vector((0, 0, 1)), 0.12,
                                     [k * math.pi / 2 for k in range(4)], 0.12, lambda p: p.x > 0.49), LAITON_DETAIL)
    # --- collerette laiton, entre casque et combinaison ; douze boulons peints sur le dessus
    collerette = tore((0.0, 0.0, 1.36), 0.47, 0.075, m["laiton"], nom="collerette")
    peindre(collerette, boulons_sur_anneau((0.0, 0.0, 1.36), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.47,
                                           [k * math.pi / 6 for k in range(12)], 0.09, lambda p: p.z > 1.40),
            LAITON_DETAIL)

    # --- torse court et arrondi, toile kaki avec plis, fermeture centrale, bassin
    # tonneau plein et lisse : une seule surface (bassin, ventre, poitrine), section élargie en X
    torse = membre([(0.0, 0.0, 0.74), (0.0, 0.0, 1.04), (0.0, 0.0, 1.34)], [0.46, 0.62, 0.44], m["kaki"],
                   "torse", nseg=16, cotes=72, plis=(7, 0.09))
    torse.scale = (1.15, 0.84, 1.0)
    _appliquer(torse)
    # fermeture à glissière et coutures : PEINTES sur la toile (pas de géométrie)
    # un trait par rangée de faces : fermeture au centre, coutures de part et d'autre, couture à la taille
    # fermeture : les deux faces du centre (x ~ 0), soit ~2 px : une seule face de 1 px saute au rendu
    peindre(torse, lambda p: p.y < -0.30 and 0.78 < p.z < 1.30 and abs(p.x) < 0.03, ACIER_DETAIL)
    for signe in (-1.0, 1.0):
        peindre_ligne(torse, lambda p, sg=signe: p.y < -0.30 and 0.78 < p.z < 1.30 and abs(abs(p.x) - 0.09) < 0.05,
                      lambda p: round(p.z / 0.0375), lambda p: abs(abs(p.x) - 0.09), TOILE_OMBRE)
    peindre_ligne(torse, lambda p: abs(p.z - 1.24) < 0.06, lambda p: round(math.atan2(p.y, p.x) / 0.09),
                  lambda p: abs(p.z - 1.24), TOILE_OMBRE)
    # --- ceinture de cuir brun, boucle métallique
    # ceinture de cuir plus large (bande de 0,14), coutures sur ses bords, boucle métallique
    tore((0.0, 0.0, 1.0), 0.66, 0.05, m["cuir"], echelle=(1.07, 0.84, 1.4), nom="ceinture")
    for z in (0.94, 1.06):
        tore((0.0, 0.0, z), 0.68, 0.009, m["kaki_sombre"], echelle=(1.07, 0.84, 1.0), nom="couture_ceinture")
    boite((0.0, -0.60, 1.0), (0.17, 0.05, 0.15), m["laiton"], biseau=0.015, nom="boucle")

    # --- bras courts et épais, manchettes sombres, gros gants caoutchouc avec pouce
    for s in (-1.0, 1.0):
        epaule = (0.58 * s, 0.0, 1.16)
        coude = (0.90 * s, -0.12, 0.96)
        poignet = (0.96 * s, -0.15, 0.74)
        # bras : plus longs et arrondis, plis de toile à l'épaule et au coude, manche qui s'évase vers le poignet
        membre([epaule, coude, poignet], [0.15, 0.135, 0.145], m["kaki"], "bras", nseg=12,
               plis=(5, 0.18, [0.10, 0.52]))
        d = (Vector(poignet) - Vector(coude)).normalized()
        # manchette de toile : la fin de la manche, avec une bande sombre ; elle prolonge le bras
        membre([Vector(poignet) - d * 0.14, Vector(poignet) + d * 0.02], [0.16, 0.17],
               m["manchette"], "manchette", nseg=2)
        # gant en mitaine : l'éllipsoïde part du poignet, son bord recouvre le bord de la manchette
        gant_c = Vector(poignet) + d * 0.12
        gant = ellipsoide(gant_c, 0.20, (1.0, 0.92, 1.22), m["gant"], biseau=0.02, nom="gant")
        gant.rotation_mode = "QUATERNION"
        gant.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(d)
        # couture de manche juste au-dessus de la manchette
        couture = tore(Vector(poignet) - d * 0.09, 0.207, 0.009, m["kaki_sombre"], nom="couture_manche")
        orienter(couture, d)
        # pouce : un petit doigt du côté intérieur et devant, qui fait la mitaine
        pouce_c = gant_c + Vector((-0.13 * s, -0.11, 0.02))
        ellipsoide(pouce_c, 0.075, (0.9, 1.15, 0.8), m["gant"], nom="pouce")

    # --- jambes courtes, genouillères sombres, grosses bottes lourdes
    for s in (-1.0, 1.0):
        hanche = (0.24 * s, 0.0, 0.78)
        genou = (0.30 * s, -0.02, 0.46)
        cheville = (0.31 * s, 0.0, 0.22)
        membre([hanche, genou, cheville], [0.23, 0.19, 0.17], m["kaki"], "jambe")
        # manchette sombre entre la jambe et la botte (bande de 2 px)
        membre([(0.31 * s, 0.0, 0.31), (0.31 * s, 0.0, 0.26)], [0.19, 0.19], m["manchette"], "manchette_botte", nseg=2)
        # genouillère : plaque arrondie collée à l'avant du genou (enfoncée de 2 cm dans la jambe)
        # genouillère : plaque bombée, enfoncée dans le genou (son bord rentre dans la jambe)
        ellipsoide((genou[0], -0.21, genou[2]), 0.15, (0.93, 0.46, 1.0), m["genouillere"],
                   biseau=0.03, nom="genouillere")
        ellipsoide((0.34 * s, -0.07, 0.11), 0.22, (1.0, 1.35, 0.7), m["botte"], biseau=0.03, nom="botte")

    # --- bouteille de plongée violet-bleu, derrière l'épaule gauche (lointaine)
    # bouteille : dépasse derrière l'épaule lointaine (gauche), penchée vers l'arrière ; son col reçoit la corde
    cylindre((-0.98, 0.50, 1.60), 0.16, 0.72, m["bouteille"], rotation=(0.0, -0.22, 0.0), biseau=0.06,
             nom="bouteille")
    cylindre((-1.07, 0.50, 2.01), 0.06, 0.12, m["bouteille"], rotation=(0.0, -0.22, 0.0), biseau=0.02,
             nom="col_bouteille")
    # valve en laiton au col : la corde s'y raccorde
    cylindre((-1.09, 0.50, 2.10), 0.045, 0.09, m["laiton"], rotation=(0.0, -0.22, 0.0), biseau=0.015,
             nom="valve")

    # --- tuyau d'air en corde torsadée, sortant du sommet du casque, grande boucle vers l'arrière
    # une seule corde épaisse : sort du sommet du casque, monte, fait une grande boucle lisse vers l'arrière,
    # puis redescend jusqu'au col de la bouteille (derrière l'épaule lointaine). Trois brins serrés.
    cordon([(0.0, 0.00, 2.40), (0.0, 0.22, 2.56), (0.0, 0.55, 2.58), (0.0, 0.88, 2.48), (0.0, 1.00, 2.22),
            (-0.14, 1.02, 2.04), (-0.46, 0.84, 1.96), (-0.84, 0.62, 2.00), (-1.04, 0.50, 2.06)],
           rayon_helice=0.030, rayon_fil=0.040, torsions=6.0, scene=scene, mat=m["corde"], nom="tuyau_air")


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
    scene.render.filter_size = 0.0          # filtre de pixel à zéro : aucun flou, aucun antialiasing
    scene.render.dither_intensity = 0.0     # pas de tramage : seules les couleurs de la palette sortent


# ------------------------------------------------------------------ carte d'identité (pixelisation)
GROUPE_COULEUR = {"tete": "#ffd400", "collerette": "#40ffb0", "tronc": "#ff0000", "tuyau": "#00e0ff",
                  "bouteille": "#ff7f00", "bras_g": "#00ff00", "bras_d": "#005000", "gant_g": "#a0ff00",
                  "gant_d": "#00a070", "jambe_g": "#0000ff", "jambe_d": "#000090", "botte_g": "#ff0080",
                  "botte_d": "#ff80c0"}


def groupe_objet(o):
    """Groupe de la carte d'identité d'un objet, d'après son nom (et son côté X pour les membres)."""
    base = re.sub(r"\.\d+$", "", o.name)
    if base.startswith(("boulon_hublot", "boulon_cote", "casque", "calotte", "raccord", "hublot", "barre")):
        return "tete"
    if base.startswith(("boulon_collerette", "collerette")):
        return "collerette"
    if base.startswith(("torse", "fermeture", "couture_fermeture", "couture_ceinture", "couture", "ceinture", "boucle")):
        return "tronc"
    if base.startswith(("tuyau_air",)):
        return "tuyau"
    if base.startswith(("bouteille", "col_bouteille", "valve")):
        return "bouteille"
    membre_groupe = None
    for prefixe, g in (("couture_manche", "bras"), ("manchette", "bras"), ("bras", "bras"),
                       ("gant", "gant"), ("pouce", "gant"), ("jambe", "jambe"), ("genouillere", "jambe"),
                       ("botte", "botte")):
        if base.startswith(prefixe):
            membre_groupe = g
            break
    if membre_groupe is None:
        return None
    # côté : moyenne X des sommets dans le monde (négatif = gauche, positif = droite)
    xs = [(o.matrix_world @ v.co).x for v in o.data.vertices]
    cote = "g" if sum(xs) / len(xs) < 0 else "d"
    return f"{membre_groupe}_{cote}"


def materiau_plat(nom, hexa):
    """Couleur plate (émission) : la carte d'identité relit une couleur exacte par partie."""
    m = bpy.data.materials.new("id_" + nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    em = arbre.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*srgb(hexa), 1.0)
    em.inputs["Strength"].default_value = 1.0
    arbre.links.new(em.outputs["Emission"], sortie.inputs["Surface"])
    return m


def rendre_fichier(scene, chemin):
    if os.path.exists(chemin):
        os.remove(chemin)
    scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(chemin):
        sys.exit("rendu absent : " + chemin)


MATIERE_COULEUR = {"laiton": "#ffd400", "acier": "#00b4ff", "verre": "#ff2bd6", "toile": "#00ff80",
                   "cuir": "#ff6a00", "caoutchouc": "#3a00ff", "corde": "#f0f0f0", "bouteille": "#9400ff"}


def matiere_objet(o):
    """Matière de chaque partie (laiton, acier, verre, toile, cuir, caoutchouc, corde, bouteille)."""
    base = re.sub(r"\.\d+$", "", o.name)
    if base.startswith(("hublot_verre", "hublot_cote_verre")):
        return "verre"
    if base.startswith(("casque", "calotte", "raccord", "collerette", "boulon_collerette", "boucle", "valve",
                        "hublot_cote_cadre")):
        return "laiton"
    if base.startswith(("hublot_cadre",)):
        return "acier"
    if base.startswith(("torse", "bras", "jambe", "couture")):
        return "toile"
    if base.startswith("ceinture"):
        return "cuir"
    if base.startswith(("gant", "pouce", "manchette", "genouillere", "botte")):
        return "caoutchouc"
    if base.startswith("tuyau_air"):
        return "corde"
    if base.startswith(("bouteille", "col_bouteille")):
        return "bouteille"
    return None


def passe_couleurs(objets, classer, couleurs):
    """Une couleur plate par classe : remplace les matériaux des parties. Renvoie {objet: classe}."""
    etiquettes = {}
    for o in objets:
        c = classer(o)
        if c is None:
            o.hide_render = True
            continue
        etiquettes[o] = c
        if o.data.users > 1:
            o.data = o.data.copy()
        o.data.materials.clear()
        o.data.materials.append(materiau_plat(c, couleurs[c]))
    return etiquettes


def rendre_identite(scene):
    """Deux cartes d'identité en couleurs plates : par MATIÈRE (quantification) et par GROUPE (membres)."""
    objets = [o for o in scene.objects if o.type in ("MESH", "CURVE")]
    # 1) matières
    dossier_m = os.path.join(SORTIE, "matiere")
    os.makedirs(dossier_m, exist_ok=True)
    passe_couleurs(objets, matiere_objet, MATIERE_COULEUR)
    with open(os.path.join(SORTIE, "matiere_palette.json"), "w", encoding="utf-8") as fichier:
        json.dump({"rampes": {g: [h] for g, h in MATIERE_COULEUR.items()}}, fichier, indent=1)
    rendre_fichier(scene, os.path.join(dossier_m, "idle_01.png"))
    # 2) groupes (membres) : image complète puis une image par groupe
    dossier = os.path.join(SORTIE, "identite")
    os.makedirs(dossier, exist_ok=True)
    groupes = passe_couleurs(objets, groupe_objet, GROUPE_COULEUR)
    with open(os.path.join(SORTIE, "identite_palette.json"), "w", encoding="utf-8") as fichier:
        json.dump({"rampes": {g: [h] for g, h in GROUPE_COULEUR.items()}}, fichier, indent=1)
    rendre_fichier(scene, os.path.join(dossier, "idle_01.png"))
    for g in sorted(set(groupes.values())):
        for o in objets:
            if o in groupes:
                o.hide_render = groupes[o] != g
        dossier_g = os.path.join(SORTIE, "parties", g)
        os.makedirs(dossier_g, exist_ok=True)
        rendre_fichier(scene, os.path.join(dossier_g, "idle_01.png"))
    for o in objets:
        if o in groupes:
            o.hide_render = False
    print("IDENTITE_OK", len(set(groupes.values())), "groupes", len(MATIERE_COULEUR), "matieres", flush=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    construire(scene)
    eclairer(scene)
    camera(scene)
    reglages(scene)
    os.makedirs(SORTIE, exist_ok=True)
    if IDENTITE:
        # pas de tramage ni d'anticrénelage au fond : chaque partie garde sa couleur exacte
        scene.render.dither_intensity = 0.0
        rendre_identite(scene)
        return
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    chemin = os.path.join(SORTIE, "dc_base.png")
    if os.path.exists(chemin):
        os.remove(chemin)
    scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(chemin):
        sys.exit("rendu absent : " + chemin)
    print("RENDU", chemin, os.path.getsize(chemin), "octets", flush=True)


main()
