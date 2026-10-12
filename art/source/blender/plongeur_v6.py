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
from mathutils import Matrix, Vector

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
    "bois": ["#6a3e1e", "#b77a36", "#e9a964"],
}
# matière -> famille de la palette
MATIERES = {
    "laiton": "laiton", "toile": "beige", "cuir": "cuir", "caoutchouc": "violet", "bouteille": "violet",
    "acier": "metal", "verre": "verre", "corde": "corde", "bois": "bois",
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
POSE = {}              # surcharge des positions du squelette (nage) ; vide = pose idle validée
GARDER_PLIS = False      # idle animé : garde les plis fixes de l'idle quand la pose change (petits décalages)
HAUT_DZ = 0.0            # idle animé : buste, épaules et casque montent de HAUT_DZ (respiration), 0 = idle validée
HAUT_DX = 0.0            # creusage : décalage vers la droite du haut du corps (buste penché)
BULLE = None             # idle animé : (centre, rayon) d'une bulle qui sort du casque, None = pas de bulle
VERSION_NAGE = 1         # 1 = nage r03 validée ; 2 = corrigée (corde qui flotte derrière, cycle asymétrique)
ROTATION_CORDE = 0.0     # nage v2 : battement de la corde flottante (phase, en radians)
PIOCHE = None            # creusage : (main droite, main gauche) sur le manche, None = pas de pioche
INCLINAISON = 0.0        # nage : élévation de la tête au-dessus de l'horizontale, en degrés (0 = pas de nage, idle)
OMBRE_BRAS = False       # nage : ombre portée des bras sur le tronc (séparation par l'ombre, pas par la couleur)
PIVOT_NAGE = (0.0, 0.0, 0.92)   # centre de rotation du corps incliné (les hanches)


def pose_de(nom):
    """Position d'une articulation : la pose en cours si elle la surcharge, sinon la pose idle."""
    return Vector(POSE[nom]) if nom in POSE else Vector(SQUELETTE[nom][0])


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
    for nom, (_, rayon) in SQUELETTE.items():
        v = bm.verts.new(tuple(pose_de(nom)))
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
    segments = [(pose_de(a), pose_de(b), etiquette(a, b)) for a, b in ARETES]
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


def tube_entre(a, b, rayon, mat, nom, cotes=8):
    """Tube droit de rayon constant entre les points a et b (manche de la pioche), faces plates."""
    a, b = Vector(a), Vector(b)
    axe = (b - a).normalized()
    t = axe.cross(Vector((0.0, 1.0, 0.0)))
    t.normalize()
    v = axe.cross(t).normalized()
    bm = bmesh.new()
    anneaux = []
    for p in (a, b):
        anneaux.append([bm.verts.new(p + rayon * (math.cos(2 * math.pi * k / cotes) * t
                                                   + math.sin(2 * math.pi * k / cotes) * v))
                        for k in range(cotes)])
    for k in range(cotes):
        bm.faces.new((anneaux[0][k], anneaux[0][(k + 1) % cotes], anneaux[1][(k + 1) % cotes], anneaux[1][k]))
    bm.faces.new(anneaux[0][::-1])
    bm.faces.new(anneaux[1])
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    o.data.materials.append(mat)
    return o


def boite_orientee(centre, axes, demi, mat, nom):
    """Pavé orienté : axes = (u, v, w) unitaires, demi = demi-tailles le long de chaque axe (tête de pioche)."""
    u, v, w = axes
    bm = bmesh.new()
    sommets = []
    for k in range(8):
        sx = 1 if k & 1 else -1
        sy = 1 if k & 2 else -1
        sz = 1 if k & 4 else -1
        sommets.append(bm.verts.new(Vector(centre) + u * sx * demi[0] + v * sy * demi[1] + w * sz * demi[2]))
    for quad in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)):
        bm.faces.new([sommets[i] for i in quad])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    o.data.materials.append(mat)
    return o


def fer_pioche(centre, axes, mat, nom, demi_barre=0.20, epaisseur=0.05, pointe=0.08):
    """Tête de pioche : une barre perpendiculaire au manche (axes = u, v, w), deux pointes aux extrémités.
    La barre fait 2 x demi_barre (10 à 14 px à l'échelle), les pointes ajoutent `pointe` de chaque côté."""
    u, v, w = axes
    c = Vector(centre)
    bm = bmesh.new()
    s = []
    for k in range(8):
        sx = 1 if k & 1 else -1
        sy = 1 if k & 2 else -1
        sz = 1 if k & 4 else -1
        s.append(bm.verts.new(c + u * sx * epaisseur + v * sy * epaisseur * 0.8 + w * sz * demi_barre))
    pa = bm.verts.new(c + w * (demi_barre + pointe))
    pb = bm.verts.new(c - w * (demi_barre + pointe))
    for quad in ((0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 5, 4), (2, 3, 7, 6)):
        bm.faces.new([s[i] for i in quad])
    for a, b in ((4, 5), (5, 7), (7, 6), (6, 4)):
        bm.faces.new((s[a], s[b], pa))
    for a, b in ((1, 0), (0, 2), (2, 3), (3, 1)):
        bm.faces.new((s[a], s[b], pb))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    o.data.materials.append(mat)
    return o


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
    for cote, sg in (("d", 1.0), ("g", -1.0)):
        plier_manche(parties["bras_" + cote], pose_de("epaule_" + cote), pose_de("coude_" + cote), 0.21)
    if GARDER_PLIS or not POSE:
        # plis fixes de l'idle (validée) ; en nage ils ne suivent pas la pose et sont omis (sauf idle animé)
        plier(parties["bras_d"], lambda p: 0.36 < p.x < 0.56 and p.y < -0.08 and 1.19 < p.z < 1.235)
        coude = pose_de("coude_d")
        plier(parties["bras_d"], lambda p: abs((p - coude).length - 0.17) < 0.02 and p.y < -0.02)
        genou = pose_de("genou_d")
        plier(parties["jambe_d"], lambda p: abs((p - genou).length - 0.21) < 0.02 and p.y < -0.05)
    torse = parties["torse"]
    plier(torse, lambda p: p.y < -0.18 and 0.04 < p.x < 0.36 and 1.095 < p.z < 1.125)
    # manchettes de cuir au poignet, plus loin que la mitaine
    for cote in ("g", "d"):
        P = pose_de("poignet_" + cote)
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
    for cote in ("g", "d"):
        P, E = pose_de("poignet_" + cote), pose_de("coude_" + cote)
        d = (P - E).normalized()
        centre = P + d * 0.13
        gant = ellipsoide(tuple(centre), 0.19, (1.0, 1.0, 1.2), m["caoutchouc"], "gant_" + cote,
                          rotation_dir=d, niveau=1)
        objets["gant_" + cote] = gant
        pouce = ellipsoide(tuple(centre + Vector((-0.12 * (1 if cote == "g" else -1), -0.10, 0.02))), 0.075,
                           (0.9, 1.15, 0.8), m["caoutchouc"], "pouce_" + cote, niveau=1)
        objets["pouce_" + cote] = pouce

    # --- bottes lourdes, bleu-violet sombre, semelle peinte
    for cote in ("g", "d"):
        cheville = pose_de("cheville_" + cote)
        botte = ellipsoide(tuple(cheville + Vector((0.0, -0.07, -0.01))), 0.24, (1.0, 1.40, 0.90), m["caoutchouc"],
                           "botte_" + cote, niveau=1)
        objets["botte_" + cote] = botte
        peindre(botte, lambda p: p.z < 0.06, C_COUTURE)

    # --- bouteille violette derrière l'épaule gauche, col et valve laiton
    bouteille = cylindre((-0.92, 0.12, 1.42), 0.15, 0.56, m["bouteille"], "bouteille", biseau=0.07)
    objets["bouteille"] = bouteille
    objets["valve"] = cylindre((-0.92, 0.12, 1.74), 0.045, 0.10, m["laiton"], "valve")

    # --- corde torsadée : tube unique, une boucle courte du casque vers la valve
    chemin_corde = [(0.0, 0.02, 2.44), (0.02, 0.22, 2.62), (-0.36, 0.42, 2.66), (-0.78, 0.40, 2.38),
                    (-0.92, 0.13, 1.80)]
    if VERSION_NAGE == 2 and POSE:
        # nage v2 : la corde part de la valve et flotte derrière le dos, vers les pieds (côté opposé à la direction)
        ondule = 0.06 * math.sin(ROTATION_CORDE)
        chemin_corde += [(-0.98 + ondule, 0.36, 1.30), (-1.06 - ondule, 0.52, 0.80), (-1.10 + ondule, 0.58, 0.30)]
    chemin_corde = [(x + HAUT_DX, y, z + HAUT_DZ) for x, y, z in chemin_corde]
    tuyau = corde_torsadee(chemin_corde, 0.065, scene, m["corde"], "tuyau", cotes=6)
    objets["tuyau"] = tuyau
    # idle animé : la tête, le hublot, la collerette et la valve montent avec le buste (respiration)
    for nom in ("casque", "hublot_verre", "cadre_hublot", "collerette", "bouteille", "valve"):
        objets[nom].location.x += HAUT_DX
        objets[nom].location.z += HAUT_DZ
    if BULLE is not None:
        centre, rayon = BULLE
        objets["bulle"] = ellipsoide((centre[0] + HAUT_DX, centre[1], centre[2] + HAUT_DZ), rayon, (1.0, 1.0, 1.0),
                                     m["acier"], "bulle", niveau=1)

    # --- pioche (creusage) : manche clair, tête en acier à deux pointes ; une main (prête, anticipation)
    # ou deux mains sur le manche (frappe, impact, retour)
    if PIOCHE is not None:
        R = Vector(PIOCHE[0])
        if PIOCHE[1] is not None:
            L = Vector(PIOCHE[1])
            u = (R - L).normalized()
        else:
            u = Vector(PIOCHE[2]).normalized()
            L = R - u * 0.75                                 # point de prise virtuel : pioche tenue d'une main
        H = R + u * PIOCHE_TETE                               # tête au-delà de la main droite
        objets["pioche_manche"] = tube_entre(L - u * PIOCHE_BOUT, H, 0.05, m["bois"], "pioche_manche")
        w = u.cross(Vector((0.0, 1.0, 0.0))).normalized()
        v = u.cross(w).normalized()
        objets["pioche_tete"] = fer_pioche(H, (u, v, w), m["acier"], "pioche_tete")

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


# ------------------------------------------------------------------ nage (huit images, plan de l'écran)
CRAWL = {"centre": 0.5, "amplitude": 0.35, "coude": 0.5, "phase_glisse": 0.35,
         "jambe_centre": 0.15, "jambe": 0.25,   # nage retenue : r03 (bras latéraux), jambes d'origine
         "asymetrie": 0.35}                      # nage v2 seulement : brise la symétrie aller-retour du cycle


def pose_crawl(k, n=8, roulis=70.0):
    """Nage de l'image k sur n. Les bras et les jambes battent dans le plan frontal du corps (X-Z) :
    un bras passe au-dessus du tronc pendant que l'autre tire vers le bas, et réciproquement ; les jambes
    battent en alternance. Le corps est roulé de `roulis` degrés (incliner) : ce plan devient le plan de
    l'écran, la tête part à droite, le visage reste tourné vers la caméra. Phase asymétrique avec glisse :
    les huit images sont toutes différentes."""
    global INCLINAISON
    INCLINAISON = roulis
    global ROTATION_CORDE
    phi = 2.0 * math.pi * k / n
    warp = phi + CRAWL["phase_glisse"] * math.sin(phi)
    if VERSION_NAGE == 2:
        # partie paire de la phase : image k et image n-k ne sont plus des miroirs (cycle non symétrique)
        warp += CRAWL["asymetrie"] * (1.0 - math.cos(phi))
        ROTATION_CORDE = phi + 0.8
    pose = {}
    for cote, s_, decal in (("d", 1.0, 0.0), ("g", -1.0, math.pi)):
        p = warp + decal
        theta = math.pi * (CRAWL["centre"] + CRAWL["amplitude"] * math.cos(p))   # 0 pendant, pi/2 côté, pi au-dessus
        beta = CRAWL["coude"] * max(0.0, math.cos(p - 0.8))                       # coude plié en récupération
        epaule = Vector(SQUELETTE["epaule_" + cote][0])
        d_bras = Vector((s_ * math.sin(theta), 0.0, -math.cos(theta)))
        coude = epaule + d_bras * 0.39
        d_avant = Vector((s_ * math.sin(theta - beta), 0.0, -math.cos(theta - beta)))
        poignet = coude + d_avant * 0.27
        pose["coude_" + cote] = tuple(coude)
        pose["poignet_" + cote] = tuple(poignet)
    for cote, s_, decal in (("d", 1.0, 0.0), ("g", -1.0, math.pi)):
        q = (2.0 * warp if VERSION_NAGE == 2 else 2.0 * phi) + decal              # deux battements par cycle
        gamma = math.pi * (CRAWL["jambe_centre"] + CRAWL["jambe"] * math.cos(q))  # écart latéral des jambes
        flex = 0.25 * (1.0 + math.cos(q)) * 0.5                                    # genou plié quand la jambe monte
        hanche = Vector(SQUELETTE["hanche_" + cote][0])
        genou = hanche + Vector((s_ * math.sin(gamma), 0.0, -math.cos(gamma))) * 0.40
        cheville = genou + Vector((s_ * math.sin(gamma - flex), 0.0, -math.cos(gamma - flex))) * 0.28
        pose["genou_" + cote] = tuple(genou)
        pose["cheville_" + cote] = tuple(cheville)
    return pose


def incliner(scene, roulis):
    """Roulis du corps (racine : bassin, tout le squelette suit) autour de l'axe de profondeur Y, en degrés.
    La tête part vers la droite (+X), le visage et le hublot restent tournés vers la caméra. Caméra, lumière
    et orientation du modèle ne changent pas : seule la pose du corps tourne."""
    if not roulis:
        return
    centre = Vector(PIVOT_NAGE)
    rot = Matrix.Rotation(math.radians(roulis), 4, "Y")
    m = Matrix.Translation(Vector(CIBLE)) @ rot @ Matrix.Translation(-centre)
    for o in scene.objects:
        if o.type in ("MESH", "CURVE"):
            o.matrix_world = m @ o.matrix_world


def rendre_nage_images(dossier, n=8, incl=70.0, identite=False, images=None, rapide=False):
    """Rend les images de nage (couleur, ou carte d'identité de chaque image) dans dossier."""
    global SORTIE, INCLINAISON
    os.makedirs(dossier, exist_ok=True)
    for k in (images if images is not None else range(n)):
        POSE.clear()
        POSE.update(pose_crawl(k, n, incl))
        scene = construire_tout()          # le roulis est appliqué dans construire_tout
        if identite:
            dossier_k = os.path.join(dossier, "image_%02d" % (k + 1))
            os.makedirs(dossier_k, exist_ok=True)
            if rapide:
                rendre_membres_rapide(scene, dossier_k)
            else:
                ancienne = SORTIE
                SORTIE = dossier_k
                rendre_identite(scene)
                SORTIE = ancienne
        else:
            rendre_fichier(scene, os.path.join(dossier, "nage_%02d.png" % (k + 1)))
    POSE.clear()
    INCLINAISON = 0.0


# ------------------------------------------------------------------ idle animé (six images, même caméra)
RESPIRATION = 0.08      # m : 2 px à l'échelle du cadre (4,5 m sur 112 px) ; buste et épaules montent
BULLES_IDLE = {1: ((0.00, -0.14, 2.54), 0.07), 2: ((0.02, -0.18, 2.59), 0.085),   # images 2 à 6 (k = 1 à 5)
               3: ((0.04, -0.22, 2.64), 0.09), 4: ((0.06, -0.26, 2.68), 0.08),    # la bulle monte doucement, grossit, puis se dissout
               5: ((0.08, -0.30, 2.71), 0.06)}


def pose_idle(k, n=6):
    """Image k de l'idle animé. k = 0 : la pose idle validée, sans rien changer (c'est l'ancre).
    Sinon : buste, cou, épaules et bras montent de off = RESPIRATION (1 - cos) / 2, de 0 à 2 px, la taille de
    la moitié ; bassin et jambes restent. Une bulle sort du casque sur les images 2 à 5. Les plis de l'idle
    restent (GARDER_PLIS) pour que les images gardent le même modelé que l'ancre."""
    global GARDER_PLIS, HAUT_DZ, BULLE
    if k == 0:
        GARDER_PLIS, HAUT_DZ, BULLE = False, 0.0, None
        return {}
    off = RESPIRATION * (1.0 - math.cos(2.0 * math.pi * k / n)) / 2.0
    GARDER_PLIS, HAUT_DZ, BULLE = True, off, BULLES_IDLE.get(k)
    pose = {}
    for nom in ("poitrine", "cou", "epaule_g", "epaule_d", "coude_g", "coude_d", "poignet_g", "poignet_d"):
        pose[nom] = tuple(Vector(SQUELETTE[nom][0]) + Vector((0.0, 0.0, off)))
    pose["taille"] = tuple(Vector(SQUELETTE["taille"][0]) + Vector((0.0, 0.0, off * 0.5)))
    return pose


def rendre_idle_images(dossier, n=6):
    """Rend les six images de l'idle animé (couleur brute) : idle_01.png ... idle_06.png."""
    global GARDER_PLIS, HAUT_DZ, BULLE
    os.makedirs(dossier, exist_ok=True)
    for k in range(n):
        POSE.clear()
        POSE.update(pose_idle(k, n))
        scene = construire_tout()
        rendre_fichier(scene, os.path.join(dossier, "idle_%02d.png" % (k + 1)))
    POSE.clear()
    GARDER_PLIS, HAUT_DZ, BULLE = False, 0.0, None


# ------------------------------------------------------------------ creusage (six images, le plongeur creuse vers la droite)
# Le plongeur creuse vers la DROITE (+X), comme dans le jeu. CREUSAGE[k] : L = main gauche (près du bas du manche),
# R = main droite (plus haut sur le manche), dx = décalage vers la droite du haut du corps (buste penché), penche = vers l'avant.
# Image 1 = ancre idle sans pioche. 2 prête (pioche basse à droite), 3 anticipation (levée derrière l'épaule droite,
# au-dessus du casque), 4 frappe (bras tendus, tête à droite à mi-hauteur), 5 impact (corps penché à droite, pioche au
# bout du bras), 6 retour (la pioche revient en arrière).
PIOCHE_BOUT = 0.40   # m : manche derrière le point de prise (longueur totale ~42 à 49 px)
PIOCHE_TETE = 0.55   # m : tête au-delà de la main droite
CREUSAGE = {  # une main (1 : prête sur l'épaule droite, 2 : anticipation, pioche levée) puis deux mains (3 à 5)
    1: {"R": (0.48, 0.05, 1.45), "u": (0.60, 0.00, -0.80), "dx": 0.00, "penche": 0.00},
    2: {"R": (0.45, 0.20, 1.90), "u": (0.50, 0.05, 0.87), "dx": -0.02, "penche": 0.04},
    3: {"R": (0.55, -0.45, 1.35), "L": (-0.40, -0.55, 1.25), "dx": 0.03, "penche": -0.03},
    4: {"R": (0.62, -0.48, 0.88), "L": (-0.20, -0.55, 1.50), "dx": 0.08, "penche": -0.08},
    5: {"R": (0.50, -0.20, 1.75), "L": (-0.42, -0.50, 1.25), "dx": 0.02, "penche": 0.02},
}


def bras_vers(S, cible, pole):
    """Coude et poignet pour que le gant arrive en `cible` (cinématique inverse à deux os, mêmes longueurs
    que pose_crawl). Le coude part dans la direction `pole`."""
    l1, l2 = 0.39, 0.27
    cible = Vector(cible)
    direction = (cible - S).normalized()
    W = cible - direction * 0.13                      # le gant est à 0,13 m du poignet
    D = min((W - S).length, l1 + l2 - 1e-3)
    axe = (W - S).normalized()
    a = (l1 * l1 - l2 * l2 + D * D) / (2.0 * D)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    perp = Vector(pole) - axe * Vector(pole).dot(axe)
    perp.normalize()
    return S + axe * a + perp * h, S + axe * D


def pose_creusage(k):
    """Image k du creusage (k = 0 : l'ancre idle, sans pioche). Une main (prête, anticipation) ou deux mains
    (frappe, impact, retour). Le haut du corps se décale de dx (buste penché à droite) et entraîne la tête, le
    hublot et la corde (HAUT_DX). Le bras non tenant la pioche reste au repos."""
    global PIOCHE, HAUT_DX
    if k == 0:
        PIOCHE, HAUT_DX = None, 0.0
        return {}
    c = CREUSAGE[k]
    dx, p = c["dx"], c["penche"]
    HAUT_DX = dx
    PIOCHE = (c["R"], c.get("L"), c.get("u"))
    pose = {}
    for nom in ("poitrine", "cou", "epaule_g", "epaule_d"):
        x, y, z = SQUELETTE[nom][0]
        pose[nom] = (x + dx, y + p, z)
    pose["taille"] = (dx * 0.5, 0.5 * p, 1.06)
    cotes = [("d", "R", (0.5, -0.8, -0.2))]
    if c.get("L") is not None:
        cotes.append(("g", "L", (-0.5, -0.8, -0.2)))
    for cote, cle, pole in cotes:
        coude, poignet = bras_vers(Vector(pose["epaule_" + cote]), c[cle], pole)
        pose["coude_" + cote] = tuple(coude)
        pose["poignet_" + cote] = tuple(poignet)
    return pose


def rendre_creusage_images(dossier, n=6, identite=False, rapide=False):
    """Rend les six images du creusage (couleur, ou carte d'identité de chaque image) dans dossier."""
    global PIOCHE, HAUT_DX, SORTIE
    os.makedirs(dossier, exist_ok=True)
    for k in range(n):
        POSE.clear()
        POSE.update(pose_creusage(k))
        scene = construire_tout()
        if identite:
            dossier_k = os.path.join(dossier, "image_%02d" % (k + 1))
            os.makedirs(dossier_k, exist_ok=True)
            if rapide:
                rendre_membres_rapide(scene, dossier_k)
            else:
                ancienne = SORTIE
                SORTIE = dossier_k
                rendre_identite(scene)
                SORTIE = ancienne
        else:
            rendre_fichier(scene, os.path.join(dossier, "creusage_%02d.png" % (k + 1)))
    POSE.clear()
    PIOCHE, HAUT_DX = None, 0.0


# ------------------------------------------------------------------ cartes d'identité
GROUPE_COULEUR ={"tete": "#ffd400", "collerette": "#40ffb0", "tronc": "#ff0000", "tuyau": "#00e0ff",
                  "bouteille": "#ff7f00", "bras_g": "#00ff00", "bras_d": "#005000", "gant_g": "#a0ff00",
                  "gant_d": "#00a070", "jambe_g": "#0000ff", "jambe_d": "#000090", "botte_g": "#ff0080",
                  "botte_d": "#ff80c0", "pioche": "#ff00ff"}
MATIERE_COULEUR = {"laiton": "#ffd400", "acier": "#00b4ff", "verre": "#ff2bd6", "toile": "#00ff80",
                   "cuir": "#ff6a00", "caoutchouc": "#3a00ff", "corde": "#f0f0f0", "bouteille": "#9400ff", "bois": "#ff8000"}


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
    if b.startswith("pioche"):
        return "pioche"
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
    if b == "pioche_manche":
        return "bois"
    if b == "pioche_tete":
        return "acier"
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


def rendre_membres_rapide(scene, dossier):
    """Carte d'identité rapide pour les essais : image complète et seules les parties des membres
    (bras, gants, jambes, bottes), soit neuf rendus au lieu de quinze."""
    import json
    objets = [o for o in scene.objects if o.type in ("MESH", "CURVE")]
    os.makedirs(os.path.join(dossier, "identite"), exist_ok=True)
    groupes = passe_couleurs(objets, groupe_objet, GROUPE_COULEUR)
    with open(os.path.join(dossier, "identite_palette.json"), "w", encoding="utf-8") as f:
        json.dump({"rampes": {g: [h] for g, h in GROUPE_COULEUR.items()}}, f, indent=1)
    rendre_fichier(scene, os.path.join(dossier, "identite", "idle_01.png"))
    for g in ("bras_d", "gant_d", "bras_g", "gant_g", "jambe_d", "botte_d", "jambe_g", "botte_g"):
        for o in objets:
            if o in groupes:
                o.hide_render = groupes[o] != g
        os.makedirs(os.path.join(dossier, "parties", g), exist_ok=True)
        rendre_fichier(scene, os.path.join(dossier, "parties", g, "idle_01.png"))
    for o in objets:
        if o in groupes:
            o.hide_render = False


def construire_tout():
    """Refait la scène de zéro : tout ce qui n'est pas la caméra ou les réglages."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    construire(scene)
    incliner(scene, INCLINAISON)
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
