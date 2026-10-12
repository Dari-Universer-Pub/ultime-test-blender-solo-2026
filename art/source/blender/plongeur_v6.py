"""
plongeur_v6.py - scaphandrier « dessin animé » (héros v6), construit de zéro dans Blender et rendu DIRECTEMENT
à la taille finale (112 px, héros de 70 à 74 px), méthode Dead Cells.

Forme : un seul corps continu (tronc, bras, jambes) généré par le modificateur Skin sur un squelette de lignes,
lissé, puis découpé en pièces pour la carte d'identité ; pièces rigides qui recouvrent les jonctions (casque,
collerette, ceinture, bouteille, corde, gants, bottes). Pas de chapelet de boules.
Détails PEINTS dans les attributs de face, pas modélisés : boulons, reflets, plis, manchettes, semelle,
torsion de la corde.
Lumière : une seule, haut-gauche ; rampes CONSTANTES de 3 ou 4 tons par matière ; contour froid cyan sur le
bord droit. Émission seule : pas de spéculaire, pas de réflexion d'environnement.

    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v6.py
Variables : PLONGEUR_SORTIE (défaut art/rendu/plongeur_v6), PLONGEUR_IDENTITE=1 (cartes d'identité).
"""
import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ID = "plongeur_v6"
SORTIE = os.environ.get("PLONGEUR_SORTIE", os.path.join(ROOT, "art", "rendu", ID))
BLEND = os.path.join(HERE, ID + ".blend")
RES = int(os.environ.get("PLONGEUR_RES", "112"))
IDENTITE = os.environ.get("PLONGEUR_IDENTITE") == "1"
AZIMUT = 35.0
ELEVATION = 15.0
CIBLE = Vector((0.0, 0.05, 1.35))
CADRE = float(os.environ.get("PLONGEUR_CADRE", "4.5"))

# ------------------------------------------------------------------ palette (25 couleurs)
# Chaque matière a une rampe de 3 ou 4 tons, du plus sombre au plus clair. Ombres vers le bleu-violet,
# lumières vers le jaune chaud. Aucun noir pur, aucun blanc pur.
PALETTE = {
    "laiton": ["#3d2b4e", "#8a5a2a", "#d19a2e", "#ffe08a"],
    "beige": ["#4f4468", "#8f7a80", "#c9ab88", "#efdcb0"],
    "cuir": ["#2a1a30", "#5c3024", "#8e5530"],
    "violet": ["#17123a", "#2c2366", "#4b3fa0"],
    "metal": ["#2a2e52", "#5a6490", "#a8b6d6"],
    "verre": ["#060d18", "#0e2a4c", "#1b4a70"],
    "reflet": ["#d8f4fa"],
    "corde": ["#4e3e4a", "#9a7444", "#e0be80"],
    "contour": ["#120c28", "#3c3a7a"],
}
# matière -> famille de la palette
MATIERES = {
    "laiton": "laiton", "toile": "beige", "cuir": "cuir", "caoutchouc": "violet", "bouteille": "violet",
    "acier": "metal", "verre": "verre", "corde": "corde",
}
# seuils des paliers sur m = (normale . lumière + 1) / 2 : 4 tons ou 3 tons
SEUILS = {4: [0.0, 0.42, 0.62, 0.80], 3: [0.0, 0.45, 0.72]}
LUMIERE = Vector((-0.30, -0.60, 0.90)).normalized()     # lumière unique, haut-gauche
DROITE = Vector((math.cos(math.radians(AZIMUT)), math.sin(math.radians(AZIMUT)), 0.0))  # bord droit à l'écran
DECALAGE_OMBRE = 0.22        # un pli (OMB = 1) décale la lecture d'un palier vers l'ombre
SEUIL_CONTOUR_DROIT = 0.80   # contour froid sur le bord droit

# codes des détails peints (attribut DET) -> ton exact de la palette
CODES = [  # (code, famille, index du ton)
    (0.20, "metal", 1),     # boulon
    (0.40, "reflet", 0),    # reflet net de la vitre (2 px)
    (0.60, "laiton", 3),    # reflet en arc sur le laiton
    (0.80, "cuir", 0),      # couture, manchette, semelle
    (0.95, "metal", 2),     # métal clair (cadre)
]
RAMPE_CODES = [0.10, 0.30, 0.50, 0.70, 0.90]   # bornes des paliers de détail (CONSTANT)


def srgb(hexa):
    """Couleur hexadécimale sRGB -> linéaire (fonction exacte) : une couleur plate ressort à l'identique."""
    h = hexa.lstrip("#")

    def lin(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(lin(int(h[k:k + 2], 16)) for k in (0, 2, 4))


def _rampe_constante(rampe, paliers):
    """Remplit une rampe CONSTANT avec (position, couleur hexa) ; retire les arrêts par défaut."""
    rampe.color_ramp.interpolation = "CONSTANT"
    elements = rampe.color_ramp.elements
    while len(elements) > 1:
        elements.remove(elements[-1])
    pos, hexa = paliers[0]
    elements[0].position = pos
    elements[0].color = (*srgb(hexa), 1.0)
    for pos, hexa in paliers[1:]:
        e = elements.new(pos)
        e.color = (*srgb(hexa), 1.0)


def materiau_dc(nom, famille):
    """Rampe de SA matière (ton choisi par la lumière), détail peint par DET, décalage d'ombre par OMB,
    contour cyan sur le bord droit. Émission seule."""
    tons = PALETTE[famille]
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    n = arbre.nodes
    lien = arbre.links
    geo = n.new("ShaderNodeNewGeometry")
    # lumière : produit scalaire normale . lumière, ramené à [0, 1]
    dot = n.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = tuple(LUMIERE)
    m01 = n.new("ShaderNodeMapRange")
    m01.inputs["From Min"].default_value = -1.0
    m01.inputs["From Max"].default_value = 1.0
    m01.inputs["To Min"].default_value = 0.0
    m01.inputs["To Max"].default_value = 1.0
    # pli : OMB = 1 décale le palier vers l'ombre
    att_ombre = n.new("ShaderNodeAttribute")
    att_ombre.attribute_type = "GEOMETRY"
    att_ombre.attribute_name = "OMB"
    decal = n.new("ShaderNodeMath")
    decal.operation = "MULTIPLY"
    decal.inputs[1].default_value = DECALAGE_OMBRE
    moins = n.new("ShaderNodeMath")
    moins.operation = "SUBTRACT"
    lien.new(geo.outputs["Normal"], dot.inputs[0])
    lien.new(dot.outputs["Value"], m01.inputs["Value"])
    lien.new(att_ombre.outputs["Fac"], decal.inputs[0])
    lien.new(m01.outputs["Result"], moins.inputs[0])
    lien.new(decal.outputs["Value"], moins.inputs[1])
    # rampe de la matière
    rampe = n.new("ShaderNodeValToRGB")
    seuils = SEUILS[len(tons)] if len(tons) in SEUILS else SEUILS[3]
    _rampe_constante(rampe, [(s, tons[i]) for i, s in enumerate(seuils)])
    lien.new(moins.outputs["Value"], rampe.inputs["Fac"])
    # détails peints : masque (DET >= 0.1) et couleur du code
    att_det = n.new("ShaderNodeAttribute")
    att_det.attribute_type = "GEOMETRY"
    att_det.attribute_name = "DET"
    masque = n.new("ShaderNodeValToRGB")
    _rampe_constante(masque, [(0.0, "#000000"), (0.1, "#ffffff")])
    couleur_det = n.new("ShaderNodeValToRGB")
    paliers = [(RAMPE_CODES[i], PALETTE[fam][idx]) for i, (code, fam, idx) in enumerate(CODES)]
    _rampe_constante(couleur_det, paliers)
    lien.new(att_det.outputs["Fac"], masque.inputs["Fac"])
    lien.new(att_det.outputs["Fac"], couleur_det.inputs["Fac"])
    # contour froid : bord droit de l'écran (produit scalaire normale . droite), hors détails
    dot_droite = n.new("ShaderNodeVectorMath")
    dot_droite.operation = "DOT_PRODUCT"
    dot_droite.inputs[1].default_value = tuple(DROITE)
    seuil = n.new("ShaderNodeValToRGB")
    _rampe_constante(seuil, [(0.0, "#000000"), (SEUIL_CONTOUR_DROIT, "#ffffff")])
    hors_det = n.new("ShaderNodeMath")
    hors_det.operation = "SUBTRACT"
    hors_det.inputs[0].default_value = 1.0      # 1 - masque : le contour n'écrase pas un détail peint
    cyan = n.new("ShaderNodeRGB")
    cyan.outputs[0].default_value = (*srgb(PALETTE["verre"][1]), 1.0)
    rim = n.new("ShaderNodeMath")
    rim.operation = "MULTIPLY"
    lien.new(geo.outputs["Normal"], dot_droite.inputs[0])
    lien.new(dot_droite.outputs["Value"], seuil.inputs["Fac"])
    lien.new(masque.outputs["Color"], hors_det.inputs[1])
    lien.new(seuil.outputs["Color"], rim.inputs[0])
    lien.new(hors_det.outputs["Value"], rim.inputs[1])
    # mélange : rampe de la matière -> détail (DET) -> contour cyan (bord droit)
    melange_det = n.new("ShaderNodeMix")
    melange_det.data_type = "RGBA"
    lien.new(masque.outputs["Color"], melange_det.inputs["Factor"])
    lien.new(rampe.outputs["Color"], melange_det.inputs[6])
    lien.new(couleur_det.outputs["Color"], melange_det.inputs[7])
    melange_rim = n.new("ShaderNodeMix")
    melange_rim.data_type = "RGBA"
    lien.new(rim.outputs["Value"], melange_rim.inputs["Factor"])
    lien.new(melange_det.outputs[2], melange_rim.inputs[6])
    lien.new(cyan.outputs["Color"], melange_rim.inputs[7])
    emission = n.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    sortie = n.new("ShaderNodeOutputMaterial")
    lien.new(melange_rim.outputs[2], emission.inputs["Color"])
    lien.new(emission.outputs["Emission"], sortie.inputs["Surface"])
    return m


def materiaux():
    return {nom: materiau_dc(nom, famille) for nom, famille in MATIERES.items()}


# ------------------------------------------------------------------ outils de forme
def _appliquer(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def _lisser(o):
    for p in o.data.polygons:
        p.use_smooth = True


def _subdiviser(o, niveau=1):
    s = o.modifiers.new("lissage", "SUBSURF")
    s.levels = niveau
    s.render_levels = niveau
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=s.name)


def ellipsoide(centre, rayon, echelle, mat, nom, rotation_dir=None, niveau=1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rayon, segments=48, ring_count=24, location=centre)
    o = bpy.context.object
    o.name = nom
    o.scale = echelle
    _appliquer(o)
    if rotation_dir is not None:
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(rotation_dir).normalized())
        _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    if niveau:
        _subdiviser(o, niveau)
    return o


def tore(centre, grand_r, petit_r, mat, nom, rotation=(0.0, 0.0, 0.0), echelle=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=grand_r, minor_radius=petit_r, major_segments=72,
                                     minor_segments=16, location=centre, rotation=rotation)
    o = bpy.context.object
    o.name = nom
    o.scale = echelle
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    _subdiviser(o, 1)
    return o


def boite(centre, taille, mat, nom, biseau=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centre)
    o = bpy.context.object
    o.name = nom
    o.scale = taille
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    if biseau > 0.0:
        b = o.modifiers.new("biseau", "BEVEL")
        b.width = biseau
        b.segments = 3
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=b.name)
    _subdiviser(o, 1)
    return o


def cylindre(centre, rayon, longueur, mat, nom, rotation=(0.0, 0.0, 0.0), biseau=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=rayon, depth=longueur, vertices=40, location=centre,
                                        rotation=rotation)
    o = bpy.context.object
    o.name = nom
    _appliquer(o)
    o.data.materials.append(mat)
    _lisser(o)
    if biseau > 0.0:
        b = o.modifiers.new("arrondi", "BEVEL")
        b.width = biseau
        b.segments = 4
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=b.name)
    _subdiviser(o, 1)
    return o


# ------------------------------------------------------------------ peinture (attributs de face)
def _attribut(me, nom):
    if nom not in me.attributes:
        me.attributes.new(nom, "FLOAT", "FACE")
    return me.attributes[nom].data


def peindre(o, predicat, code):
    """DET = code de détail là où le prédicat (centre de face, monde) est vrai."""
    masque = _attribut(o.data, "DET")
    M = o.matrix_world
    n = 0
    for f in o.data.polygons:
        if predicat(M @ f.center):
            masque[f.index].value = code
            n += 1
    return n


def plier(o, predicat):
    """OMB = 1 : pli, le palier de lumière est décalé vers l'ombre."""
    pli = _attribut(o.data, "OMB")
    M = o.matrix_world
    n = 0
    for f in o.data.polygons:
        if predicat(M @ f.center):
            pli[f.index].value = 1.0
            n += 1
    print("pli", o.name, n, flush=True)
    return n


C_BOULON = 0.20
C_REFLET_VERRE = 0.40
C_REFLET_LAITON = 0.60
C_COUTURE = 0.80
C_METAL_CLAIR = 0.95


def anneau(centre, axe_u, axe_v, rayon, angles, demi, cote):
    """Prédicat : points d'un anneau proches des angles donnés, sur la moitié demandée."""
    def predicat(p):
        d = p - Vector(centre)
        u, v = d.dot(Vector(axe_u)), d.dot(Vector(axe_v))
        r, a = math.hypot(u, v), math.atan2(v, u)
        return abs(r - rayon) < 0.05 and cote(p) and min(abs((a - t + math.pi) % (2 * math.pi) - math.pi)
                                                        for t in angles) < demi
    return predicat


# ------------------------------------------------------------------ corps continu (Skin)
# squelette : nom -> (position, rayon en x, rayon en y). Le tronc est court et rond, bras et jambes courts.
SQUELETTE = {
    "bassin": ((0.0, 0.0, 0.92), (0.36, 0.28)),
    "taille": ((0.0, 0.0, 1.06), (0.37, 0.30)),
    "poitrine": ((0.0, 0.0, 1.27), (0.48, 0.40)),
    "cou": ((0.0, 0.0, 1.44), (0.26, 0.24)),
    "epaule_g": ((-0.42, 0.0, 1.27), (0.21, 0.21)),
    "epaule_d": ((0.42, 0.0, 1.27), (0.21, 0.21)),
    "coude_g": ((-0.70, -0.12, 1.02), (0.19, 0.19)),
    "coude_d": ((0.70, -0.12, 1.02), (0.19, 0.19)),
    "poignet_g": ((-0.80, -0.18, 0.78), (0.165, 0.165)),
    "poignet_d": ((0.80, -0.18, 0.78), (0.165, 0.165)),
    "hanche_g": ((-0.22, 0.0, 0.84), (0.25, 0.25)),
    "hanche_d": ((0.22, 0.0, 0.84), (0.25, 0.25)),
    "genou_g": ((-0.24, -0.06, 0.44), (0.24, 0.23)),
    "genou_d": ((0.24, -0.06, 0.44), (0.24, 0.23)),
    "cheville_g": ((-0.26, 0.0, 0.16), (0.20, 0.20)),
    "cheville_d": ((0.26, 0.0, 0.16), (0.20, 0.20)),
}
ARETES = [("bassin", "taille"), ("taille", "poitrine"), ("poitrine", "cou"),
          ("poitrine", "epaule_g"), ("epaule_g", "coude_g"), ("coude_g", "poignet_g"),
          ("poitrine", "epaule_d"), ("epaule_d", "coude_d"), ("coude_d", "poignet_d"),
          ("bassin", "hanche_g"), ("hanche_g", "genou_g"), ("genou_g", "cheville_g"),
          ("bassin", "hanche_d"), ("hanche_d", "genou_d"), ("genou_d", "cheville_d")]


PROFONDEUR_CORPS = 1.3   # échelle en y du corps lissé (section ovale du Skin -> tronc rond)


def plier_manche(o, a, b, rayon):
    """Pli longitudinal d'une manche : faces du devant (proches de la direction avant), sur le tiers central."""
    axe = (b - a)
    M = o.matrix_world
    pli = _attribut(o.data, "OMB")
    n = 0
    for f in o.data.polygons:
        p = M @ f.center
        t = max(0.0, min(1.0, (p - a).dot(axe) / axe.length_squared))
        q = a + axe * t
        d = p - q
        r = d.length
        if r < 1e-6 or not (0.10 < t < 0.90) or abs(r - rayon) > 0.05:
            continue
        devant = Vector((0.0, -1.0, 0.0))
        devant = devant - axe.normalized() * devant.dot(axe.normalized())
        if (d.normalized().dot(devant.normalized())) > 0.95:
            pli[f.index].value = 1.0
            n += 1
    return n


def _distance_segment(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def corps(scene, mat):
    """Un seul maillage continu (Skin + lissage), puis découpé en parties nommées pour la carte d'identité."""
    bm = bmesh.new()
    couche = bm.verts.layers.skin.verify()
    sommets = {}
    for nom, (pos, rayon) in SQUELETTE.items():
        v = bm.verts.new(pos)
        v[couche].radius = (rayon[0], rayon[0])     # section ronde : le rayon en y est réduit par le Skin
        sommets[nom] = v
    sommets["bassin"][couche].use_root = True
    for a, b in ARETES:
        bm.edges.new((sommets[a], sommets[b]))
    me = bpy.data.meshes.new("corps_brut")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("corps_brut", me)
    scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    skin = o.modifiers.new("squelette", "SKIN")
    sub = o.modifiers.new("lissage", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=skin.name)
    bpy.ops.object.modifier_apply(modifier=sub.name)
    # le Skin écrase la section en profondeur (y) : on la rétablit pour un tronc rond
    o.scale = (1.0, PROFONDEUR_CORPS, 1.0)
    _appliquer(o)
    _lisser(o)
    # découpe : chaque face va au segment d'os le plus proche (torse, bras, jambes)
    def etiquette(a, b):
        # épaules et bassin appartiennent au tronc ; seuls coude, poignet, genou, cheville définissent un membre
        for cote in ("g", "d"):
            if any(n.endswith("_" + cote) and n.split("_")[0] in ("coude", "poignet") for n in (a, b)):
                return "bras_" + cote
            if any(n.endswith("_" + cote) and n.split("_")[0] in ("genou", "cheville") for n in (a, b)):
                return "jambe_" + cote
        return "torse"
    segments = [(Vector(SQUELETTE[a][0]), Vector(SQUELETTE[b][0]), etiquette(a, b)) for a, b in ARETES]
    parties = {"torse": [], "bras_g": [], "bras_d": [], "jambe_g": [], "jambe_d": []}
    for f in o.data.polygons:
        c = f.center
        meilleur = min(segments, key=lambda sg: _distance_segment(c, sg[0], sg[1]))
        parties[meilleur[2]].append(f.index)
    objets = {}
    for nom, indices in parties.items():
        morceau = bmesh.new()
        morceau.from_mesh(o.data)
        garder = set(indices)
        jeter = [f for f in morceau.faces if f.index not in garder]
        bmesh.ops.delete(morceau, geom=jeter, context="FACES")
        me_p = bpy.data.meshes.new(nom)
        morceau.to_mesh(me_p)
        morceau.free()
        p = bpy.data.objects.new(nom, me_p)
        scene.collection.objects.link(p)
        me_p.materials.append(mat)
        _lisser(p)
        objets[nom] = p
    bpy.data.objects.remove(o, do_unlink=True)
    return objets


def corde_torsadee(points, rayon, scene, mat, nom, cotes=16, nseg=14):  # cotes=6 : torsion lisible à 3 px
    """Corde en un seul tube le long d'un chemin lisse, torsion PEINTE : bandes en hélice par OMB."""
    pts = [Vector(p) for p in points]
    pts = [pts[0]] + pts + [pts[-1]]
    chemin = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(nseg):
            t = k / nseg
            t2, t3 = t * t, t * t * t
            chemin.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    chemin.append(pts[-2])
    bm = bmesh.new()
    anneaux = []
    normale = None
    n = len(chemin)
    for i, p in enumerate(chemin):
        a = chemin[max(i - 1, 0)]
        b = chemin[min(i + 1, n - 1)]
        tg = (b - a).normalized()
        if normale is None:
            nrm = tg.cross(Vector((0.0, 0.0, 1.0)))
            if nrm.length < 1e-4:
                nrm = tg.cross(Vector((1.0, 0.0, 0.0)))
            nrm.normalize()
        else:
            nrm = normale - tg * normale.dot(tg)
            nrm.normalize()
        normale = nrm
        bn = tg.cross(nrm).normalized()
        anneaux.append([bm.verts.new(p + rayon * (math.cos(2 * math.pi * k / cotes) * nrm
                                                   + math.sin(2 * math.pi * k / cotes) * bn))
                        for k in range(cotes)])
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
    scene.collection.objects.link(o)
    _lisser(o)
    # torsion : chaque face appartient à un anneau i et à une position k ; bandes en hélice
    pli = _attribut(me, "OMB")
    for f in me.polygons:
        if len(f.vertices) != 4:
            continue
        i = f.index // cotes
        k = f.index % cotes
        if ((k + i * 1) % cotes) < cotes // 2:   # bandes en hélice, décalées d'un anneau à l'autre
            pli[f.index].value = 1.0
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    _subdiviser(o, 1)
    return o


# ------------------------------------------------------------------ scène
def construire(scene):
    m = materiaux()
    objets = {}
    # --- corps continu
    parties = corps(scene, m["toile"])
    objets.update(parties)
    for p in parties.values():
        p.data.materials.clear()
        p.data.materials.append(m["toile"])
    # quatre plis nets : deux sur le devant du tronc, un sur le haut de chaque manche (lignes d'une face)
    torse = parties["torse"]
    for sg in (-1.0, 1.0):
        plier(torse, lambda p, sg=sg: p.y < -0.20 and 0.84 < p.z < 1.32 and abs(p.x - sg * 0.07) < 0.075)
    plier_manche(parties["bras_d"], Vector((0.42, 0.0, 1.27)), Vector((0.70, -0.12, 1.02)), 0.21)
    plier_manche(parties["bras_g"], Vector((-0.42, 0.0, 1.27)), Vector((-0.70, -0.12, 1.02)), 0.21)
    # plis (anciens) sur le côté proche (+X, la caméra est côté +X)
    torse = parties["torse"]
    plier(parties["bras_d"], lambda p: 0.36 < p.x < 0.56 and p.y < -0.08 and 1.19 < p.z < 1.235)
    plier(torse, lambda p: p.y < -0.18 and 0.04 < p.x < 0.36 and 1.095 < p.z < 1.125)
    coude = Vector((0.70, -0.12, 1.02))
    plier(parties["bras_d"], lambda p: abs((p - coude).length - 0.17) < 0.02 and p.y < -0.02)
    genou = Vector((0.24, -0.06, 0.44))
    plier(parties["jambe_d"], lambda p: abs((p - genou).length - 0.21) < 0.02 and p.y < -0.05)
    # manchettes de cuir au poignet, plus loin que la mitaine
    for cote, poignet in (("g", (-0.80, -0.18, 0.78)), ("d", (0.80, -0.18, 0.78))):
        P = Vector(poignet)
        peindre(parties["bras_" + cote], lambda p, P=P: 0.12 < (p - P).length < 0.19, C_COUTURE)

    # --- casque laiton, grand hublot cerclé de métal, boulons et reflets peints
    casque = ellipsoide((0.0, 0.0, 1.92), 0.56, (1.0, 1.0, 0.94), m["laiton"], "casque", niveau=1)
    objets["casque"] = casque
    H = Vector((0.0, 0.0, 1.92))
    peindre(casque, lambda p: p.z > 1.90 and abs((p - H).normalized().dot(LUMIERE) - 0.86) < 0.05,
            C_REFLET_LAITON)
    hublot = ellipsoide((0.0, -0.52, 1.98), 0.30, (1.0, 0.22, 1.0), m["verre"], "hublot_verre", niveau=1)
    objets["hublot_verre"] = hublot
    peindre(hublot, lambda p: p.y < -0.48 and (p.x + 0.12) ** 2 + (p.z - 2.12) ** 2 < 0.045 ** 2, C_REFLET_VERRE)
    cadre = tore((0.0, -0.56, 1.98), 0.32, 0.055, m["acier"], "cadre_hublot", rotation=(math.pi / 2, 0.0, 0.0))
    objets["cadre_hublot"] = cadre
    peindre(cadre, anneau((0.0, -0.56, 1.98), (1, 0, 0), (0, 0, 1), 0.32,
                          [k * math.pi / 3 for k in range(6)], 0.09, lambda p: p.y < -0.56), C_BOULON)

    # --- collerette laiton et boulons du dessus
    collerette = tore((0.0, 0.0, 1.44), 0.50, 0.085, m["laiton"], "collerette")
    objets["collerette"] = collerette
    peindre(collerette, anneau((0.0, 0.0, 1.44), (1, 0, 0), (0, 1, 0), 0.50,
                               [k * math.pi / 6 for k in range(12)], 0.09, lambda p: p.z > 1.46), C_BOULON)

    # --- ceinture de cuir marron, boucle laiton
    ceinture = tore((0.0, 0.0, 1.02), 0.45, 0.06, m["cuir"], "ceinture", echelle=(1.0, 0.85, 1.0))
    objets["ceinture"] = ceinture
    objets["boucle"] = boite((0.0, -0.42, 1.02), (0.11, 0.04, 0.11), m["laiton"], "boucle", biseau=0.01)

    # --- gants en mitaine, bleu-violet sombre, avec pouce
    for cote, poignet, coude_p in (("g", (-0.80, -0.18, 0.78), (-0.70, -0.12, 1.02)),
                                   ("d", (0.80, -0.18, 0.78), (0.70, -0.12, 1.02))):
        P, E = Vector(poignet), Vector(coude_p)
        d = (P - E).normalized()
        centre = P + d * 0.13
        gant = ellipsoide(tuple(centre), 0.19, (1.0, 1.0, 1.2), m["caoutchouc"], "gant_" + cote,
                          rotation_dir=d, niveau=1)
        objets["gant_" + cote] = gant
        pouce = ellipsoide(tuple(centre + Vector((-0.12 * (1 if cote == "g" else -1), -0.10, 0.02))), 0.075,
                           (0.9, 1.15, 0.8), m["caoutchouc"], "pouce_" + cote, niveau=1)
        objets["pouce_" + cote] = pouce

    # --- bottes lourdes, bleu-violet sombre, semelle peinte
    for cote, s in (("g", -1.0), ("d", 1.0)):
        botte = ellipsoide((0.26 * s, -0.07, 0.15), 0.24, (1.0, 1.40, 0.90), m["caoutchouc"], "botte_" + cote,
                           niveau=1)
        objets["botte_" + cote] = botte
        peindre(botte, lambda p: p.z < 0.06, C_COUTURE)

    # --- bouteille violette derrière l'épaule gauche, col et valve laiton
    bouteille = cylindre((-0.92, 0.12, 1.42), 0.15, 0.56, m["bouteille"], "bouteille", biseau=0.07)
    objets["bouteille"] = bouteille
    objets["valve"] = cylindre((-0.92, 0.12, 1.74), 0.045, 0.10, m["laiton"], "valve")

    # --- corde torsadée : tube unique, une boucle courte du casque vers la valve
    tuyau = corde_torsadee([(0.0, 0.02, 2.44), (0.02, 0.22, 2.62), (-0.36, 0.42, 2.66), (-0.78, 0.40, 2.38),
                            (-0.92, 0.13, 1.80)], 0.065, scene, m["corde"], "tuyau", cotes=6)
    objets["tuyau"] = tuyau

    # --- scène
    for o in objets.values():
        if o.name not in scene.objects:
            scene.collection.objects.link(o)
    return objets


def eclairer(scene):
    """Une seule lumière, haut-gauche : les matières sont à émission seule, la lumière sert aux visuels
    de l'aperçu. Pas de spéculaire, pas de réflexion d'environnement."""
    l = bpy.data.lights.new("clef_haut_gauche", "AREA")
    l.energy = 120.0
    l.shape = "SQUARE"
    l.size = 3.0
    o = bpy.data.objects.new("clef_haut_gauche", l)
    scene.collection.objects.link(o)
    o.location = CIBLE + LUMIERE * 6.0
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0.0, 0.0, -1.0)).rotation_difference(-LUMIERE)
    monde = bpy.data.worlds.new("monde")
    monde.use_nodes = True
    monde.node_tree.nodes["Background"].inputs["Color"].default_value = (0.2, 0.2, 0.25, 1.0)
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
    scene.eevee.taa_render_samples = 1
    scene.render.filter_size = 0.0
    scene.render.dither_intensity = 0.0


# ------------------------------------------------------------------ cartes d'identité
GROUPE_COULEUR = {"tete": "#ffd400", "collerette": "#40ffb0", "tronc": "#ff0000", "tuyau": "#00e0ff",
                  "bouteille": "#ff7f00", "bras_g": "#00ff00", "bras_d": "#005000", "gant_g": "#a0ff00",
                  "gant_d": "#00a070", "jambe_g": "#0000ff", "jambe_d": "#000090", "botte_g": "#ff0080",
                  "botte_d": "#ff80c0"}
MATIERE_COULEUR = {"laiton": "#ffd400", "acier": "#00b4ff", "verre": "#ff2bd6", "toile": "#00ff80",
                   "cuir": "#ff6a00", "caoutchouc": "#3a00ff", "corde": "#f0f0f0", "bouteille": "#9400ff"}


def _base(o):
    return re.sub(r"\.\d+$", "", o.name)


def groupe_objet(o):
    b = _base(o)
    if b in ("casque", "hublot_verre", "cadre_hublot", "valve"):
        return "tete" if b != "valve" else "bouteille"
    if b == "collerette":
        return "collerette"
    if b in ("torse", "ceinture", "boucle"):
        return "tronc"
    if b == "tuyau":
        return "tuyau"
    if b == "bouteille":
        return "bouteille"
    if b in ("bras_g", "bras_d", "jambe_g", "jambe_d", "botte_g", "botte_d", "gant_g", "gant_d"):
        return b
    if b in ("pouce_g", "pouce_d"):
        return "gant_" + b[-1]
    return None


def matiere_objet(o):
    b = _base(o)
    if b in ("casque", "collerette", "boucle", "valve"):
        return "laiton"
    if b in ("hublot_verre",):
        return "verre"
    if b == "cadre_hublot":
        return "acier"
    if b in ("torse", "bras_g", "bras_d", "jambe_g", "jambe_d"):
        return "toile"
    if b == "ceinture":
        return "cuir"
    if b in ("gant_g", "gant_d", "pouce_g", "pouce_d", "botte_g", "botte_d"):
        return "caoutchouc"
    if b == "tuyau":
        return "corde"
    if b == "bouteille":
        return "bouteille"
    return None


def materiau_plat(nom, hexa):
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


def passe_couleurs(objets, classer, couleurs):
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


def rendre_fichier(scene, chemin):
    if os.path.exists(chemin):
        os.remove(chemin)
    scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(chemin):
        sys.exit("rendu absent : " + chemin)


def rendre_identite(scene):
    import json
    objets = [o for o in scene.objects if o.type in ("MESH", "CURVE")]
    os.makedirs(os.path.join(SORTIE, "matiere"), exist_ok=True)
    passe_couleurs(objets, matiere_objet, MATIERE_COULEUR)
    with open(os.path.join(SORTIE, "matiere_palette.json"), "w", encoding="utf-8") as f:
        json.dump({"rampes": {g: [h] for g, h in MATIERE_COULEUR.items()}}, f, indent=1)
    rendre_fichier(scene, os.path.join(SORTIE, "matiere", "idle_01.png"))
    os.makedirs(os.path.join(SORTIE, "identite"), exist_ok=True)
    groupes = passe_couleurs(objets, groupe_objet, GROUPE_COULEUR)
    with open(os.path.join(SORTIE, "identite_palette.json"), "w", encoding="utf-8") as f:
        json.dump({"rampes": {g: [h] for g, h in GROUPE_COULEUR.items()}}, f, indent=1)
    rendre_fichier(scene, os.path.join(SORTIE, "identite", "idle_01.png"))
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
    print("IDENTITE_OK", len(set(groupes.values())), "groupes", flush=True)


def construire_tout():
    """Refait la scène de zéro : tout ce qui n'est pas la caméra ou les réglages."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    construire(scene)
    eclairer(scene)
    camera(scene)
    reglages(scene)
    return scene


def main():
    scene = construire_tout()
    os.makedirs(SORTIE, exist_ok=True)
    if IDENTITE:
        rendre_identite(scene)
        return
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    rendre_fichier(scene, os.path.join(SORTIE, "dc_base.png"))
    print("RENDU", os.path.join(SORTIE, "dc_base.png"), flush=True)


if __name__ == "__main__":
    main()
