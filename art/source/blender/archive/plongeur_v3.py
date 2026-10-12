"""
plongeur_v3.py - le plongeur de LES CLOCHES DE VAREKH, refait pour une vue de trois quarts (M4, nouvel angle).

Conception « face d'abord » : modèle symétrique, face tournée vers -Y, pensé pour être lu de trois quarts
(azimut 30 à 45°, élévation 10 à 20°). Casque de scaphandrier en laiton avec hublot, combinaison kaki,
gros gants et grosses bottes presque noirs, bouteilles dans le dos, tuyau de corde devant. Proportions de
dessin animé : grosse tête, tronc court, membres courts et épais (au moins 4 px de large). Les membres sont
écartés du corps dès la construction : épaules plus larges que le tronc, bras sur les côtés, hanches écartées.

Aucun modèle ni rig téléchargé : primitives Blender (sphères, tubes, anneaux), squelette simple, poids par
distance. L'ancien modèle (profil) est archivé dans art/source/blender/archive/ et n'est pas réutilisé.

    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur_v3.py

Variables d'environnement (tests) : PLONGEUR_AZIMUT (défaut 35), PLONGEUR_ELEVATION (défaut 15),
PLONGEUR_IDENTITE=1 (carte d'identité : une image plate par partie), PLONGEUR_IDENTITE_IMAGES, PLONGEUR_IMAGES
(numéros d'image à rendre), PLONGEUR_RES (640 = 8 x 80 px), PLONGEUR_ECHANTILLONS, PLONGEUR_SORTIE.
Unité : 1 px du rendu final = PX unités ; une case de 80 px = 80 px.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SORTIE = os.environ.get("PLONGEUR_SORTIE", os.path.join(ROOT, "art", "rendu", "plongeur_v3"))
BLEND = os.path.join(HERE, "plongeur_v3.blend")

RES = int(os.environ.get("PLONGEUR_RES", "640"))
ECHANTILLONS = int(os.environ.get("PLONGEUR_ECHANTILLONS", "64"))
AZIMUT = float(os.environ.get("PLONGEUR_AZIMUT", "35"))          # angle depuis la face (-Y) vers +X
ELEVATION = float(os.environ.get("PLONGEUR_ELEVATION", "15"))   # au-dessus de l'horizontale
PX = 0.0466                                                       # unités de monde par pixel du rendu final
LARGEUR_CADRE = 80 * PX * 1.085                                  # une case de 80 px ; le tangage de 15° ajoute ~3 px : silhouette 46 à 48 px
SOUPLESSE = 0.10                                                  # transition des poids entre deux os
IMAGES = {f: f"idle_{f:02d}" for f in range(1, 7)}                # numéro d'image -> nom (étape 1 : idle)
FRAMES = [int(v) for v in os.environ.get("PLONGEUR_IMAGES", ",".join(str(f) for f in IMAGES)).split(",") if v.strip()]

PAL = json.load(open(os.path.join(ROOT, "art", "palette.json"), encoding="utf-8"))["rampes"]


def couleur_lin(rampe, i):
    """Couleur linéaire (Blender) d'un ton de la palette du projet."""
    h = PAL[rampe][i].lstrip("#")
    srgb = [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def materiau(nom, rampe, i, rugosite=0.55, emission=0.0, bandes=(1, 2, 3, 4)):
    """Matériau à paliers : Principled -> Shader to RGB -> rampe en paliers (tons de la palette) -> Emission."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    if emission:
        rgb = couleur_lin(rampe, i)
        em = arbre.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        em.inputs["Strength"].default_value = emission
        arbre.links.new(em.outputs["Emission"], sortie.inputs["Surface"])
        return m
    rgb = couleur_lin(rampe, i)
    principled = arbre.nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    principled.inputs["Roughness"].default_value = rugosite
    lumiere = arbre.nodes.new("ShaderNodeShaderToRGB")
    paliers = arbre.nodes.new("ShaderNodeValToRGB")
    paliers.color_ramp.interpolation = "CONSTANT"
    el = paliers.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    positions = ([0.0, 0.18, 0.42] if len(bandes) == 3 else [0.0, 0.16, 0.34, 0.56])[:len(bandes)]
    for k, (pos, idx) in enumerate(zip(positions, bandes)):
        c = couleur_lin(rampe, idx)
        if k == 0:
            el[0].position = pos
            el[0].color = (c[0], c[1], c[2], 1.0)
        else:
            nouveau = el.new(pos)
            nouveau.color = (c[0], c[1], c[2], 1.0)
    emission_nd = arbre.nodes.new("ShaderNodeEmission")
    emission_nd.inputs["Strength"].default_value = 1.0
    arbre.links.new(principled.outputs["BSDF"], lumiere.inputs["Shader"])
    arbre.links.new(lumiere.outputs["Color"], paliers.inputs["Fac"])
    arbre.links.new(paliers.outputs["Color"], emission_nd.inputs["Color"])
    arbre.links.new(emission_nd.outputs["Emission"], sortie.inputs["Surface"])
    return m


# ------------------------------------------------------------------ primitives
def sphere(centre, rayon, mat, echelle=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=rayon, location=centre)
    o = bpy.context.active_object
    o.scale = echelle
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def tube(a, b, rayon, mat, cotes=14):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=cotes, radius=rayon, depth=d.length, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.normalized().to_track_quat("Z", "Y")
    o.data.materials.append(mat)
    return o


def anneau(centre, grand_r, petit_r, mat, echelle=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=grand_r, minor_radius=petit_r,
                                     major_segments=40, minor_segments=12, location=centre)
    o = bpy.context.active_object
    o.scale = echelle
    o.data.materials.append(mat)
    return o


def P(*v):
    """Pixels du rendu final -> unités de monde."""
    return tuple(x * PX for x in v)


# ------------------------------------------------------------------ carte d'identité
# Nom de matériau -> (groupe de la carte, couleur plate). Un groupe = une partie mesurable.
GROUPES_ID = {
    "tronc": ("tronc", "#ff0000"), "tete": ("tete", "#ffd400"), "cadre": ("tete", "#ffd400"),
    "hublot_verre": ("tete", "#ffd400"), "cadre_gris": ("tete", "#ffd400"), "hublot_reflet": ("tete", "#ffd400"),
    "collerette": ("collerette", "#40ffb0"), "boucle": ("ceinture", "#7a3cff"),
    "ceinture": ("ceinture", "#7a3cff"), "tuyau": ("tuyau", "#00e0ff"),
    "bouteilles": ("bouteilles", "#ff7f00"), "palmes": ("palmes", "#ff00c8"),
    "bras_g": ("bras_g", "#00ff00"), "bras_d": ("bras_d", "#005000"),
    "jambe_g": ("jambe_g", "#0000ff"), "jambe_d": ("jambe_d", "#000090"),
    "gant_g": ("gant_g", "#a0ff00"), "gant_d": ("gant_d", "#00a070"),
    "botte_g": ("botte_g", "#ff0080"), "botte_d": ("botte_d", "#ff80c0"),
}
GROUPES = ["tronc", "tete", "collerette", "ceinture", "tuyau", "bouteilles", "palmes",
           "bras_g", "bras_d", "jambe_g", "jambe_d", "gant_g", "gant_d", "botte_g", "botte_d"]


def lin_hex(h):
    rgb = [int(h.lstrip("#")[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]


def materiau_plat(nom, h):
    m = bpy.data.materials.new("id_" + nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    em = arbre.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin_hex(h), 1.0)
    em.inputs["Strength"].default_value = 1.0
    arbre.links.new(em.outputs["Emission"], sortie.inputs["Surface"])
    return m


def rendre_identite(scene, corps, images):
    """Carte d'identité : image complète en couleurs plates, puis une image par groupe (les autres faces
    supprimées de copies du modèle). Écrit la palette d'identité pour la pixelisation."""
    dossier = os.path.join(SORTIE, "identite")
    os.makedirs(dossier, exist_ok=True)
    couleurs, noms_slots = {}, []
    for i, mat in enumerate(list(corps.data.materials)):
        groupe, h = GROUPES_ID[mat.name]
        couleurs[groupe] = h
        noms_slots.append(groupe)
        corps.data.materials[i] = materiau_plat(groupe, h)
    with open(os.path.join(SORTIE, "identite_palette.json"), "w", encoding="utf-8") as fichier:
        json.dump({"rampes": {g: [couleurs[g]] for g in GROUPES}}, fichier, indent=1)
    for f in images:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(dossier, IMAGES[f] + ".png")
        bpy.ops.render.render(write_still=True)
    corps.hide_render = True
    for g in GROUPES:
        copie = corps.copy()
        copie.data = corps.data.copy()
        scene.collection.objects.link(copie)
        bm = bmesh.new()
        bm.from_mesh(copie.data)
        perdues = [fc for fc in bm.faces if noms_slots[fc.material_index] != g]
        bmesh.ops.delete(bm, geom=perdues, context="FACES")
        bm.to_mesh(copie.data)
        bm.free()
        copie.hide_render = False
        dossier_g = os.path.join(SORTIE, "parties", g)
        os.makedirs(dossier_g, exist_ok=True)
        for f in images:
            scene.frame_set(f)
            scene.render.filepath = os.path.join(dossier_g, IMAGES[f] + ".png")
            bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(copie, do_unlink=True)
    print("IDENTITE_OK", len(GROUPES), "groupes", len(images), "images")


# ------------------------------------------------------------------ squelette (pixels du rendu final)
# Repère : face tournée vers -Y, X vers la droite du personnage, Z vers le haut, pieds vers z = 0.
OS_REPOS_PX = {
    "buste": ((0, 0, 14), (0, 0, 30), None),
    "tete": ((0, 0, 30), (0, 0, 40), "buste"),
}
for _s, _x in (("g", -1.0), ("d", 1.0)):
    OS_REPOS_PX.update({
        f"bras_{_s}_1": ((_x * 8.5, 0, 27), (_x * 12.5, -1, 18), "buste"),
        f"bras_{_s}_2": ((_x * 12.5, -1, 18), (_x * 14, -2, 10), f"bras_{_s}_1"),
        f"jambe_{_s}_1": ((_x * 4.8, 0, 14), (_x * 5.5, 0, 7.6), "buste"),
        f"jambe_{_s}_2": ((_x * 5.5, 0, 7.6), (_x * 5.8, 0, 3.4), f"jambe_{_s}_1"),
    })
OS_REPOS = {nom: (P(*a), P(*b), parent) for nom, (a, b, parent) in OS_REPOS_PX.items()}


def construire_squelette():
    bpy.ops.object.armature_add(location=(0.0, 0.0, 0.0))
    sq = bpy.context.active_object
    sq.name = "Squelette"
    arm = sq.data
    bpy.ops.object.mode_set(mode="EDIT")
    for eb in list(arm.edit_bones):
        arm.edit_bones.remove(eb)
    for nom, (tete, queue, parent) in OS_REPOS.items():
        eb = arm.edit_bones.new(nom)
        eb.head = tete
        eb.tail = queue
        if parent:
            eb.parent = arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    return sq


def distance_segment(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


def poids_par_distance(corps, sq):
    """Chaque sommet suit les os proches (3 au maximum), poids décroissants avec la distance."""
    segments = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in sq.data.bones}
    groupes = {nom: corps.vertex_groups.new(name=nom) for nom in segments}
    for v in corps.data.vertices:
        ds = {nom: distance_segment(v.co, a, b) for nom, (a, b) in segments.items()}
        dmin = min(ds.values())
        poids = {n: max(0.0, 1.0 - (d - dmin) / SOUPLESSE) ** 2 for n, d in ds.items()}
        top = sorted(poids.items(), key=lambda kv: -kv[1])[:3]
        tot = sum(w for _, w in top)
        for n, w in top:
            if w > 0:
                groupes[n].add([v.index], w / tot, "REPLACE")
    mod = corps.modifiers.new("Squelette", "ARMATURE")
    mod.object = sq
    corps.parent = sq


# ------------------------------------------------------------------ modèle
def construire_modele():
    m_tronc = materiau("tronc", "kaki", 1, 0.5, bandes=(0, 1, 2))                       # tronc : kaki médian
    m_bras = {s: materiau(f"bras_{s}", "kaki", 3, 0.5, bandes=(2, 3, 3)) for s in "gd"}  # manches : kaki le plus clair
    m_jambe = {s: materiau(f"jambe_{s}", "kaki", 0, 0.6, bandes=(0, 0, 1)) for s in "gd"}  # jambes : kaki foncé
    m_gant = {s: materiau(f"gant_{s}", "gant", 1, 0.6, bandes=(0, 1, 2)) for s in "gd"}  # gants : presque noirs
    m_botte = {s: materiau(f"botte_{s}", "gant", 0, 0.6, bandes=(0, 0, 1)) for s in "gd"}  # bottes : presque noires
    m_laiton = materiau("tete", "laiton", 2, 0.25, bandes=(1, 2, 3, 3))                  # casque laiton doré
    m_cadre = materiau("cadre", "laiton", 0, 0.3, bandes=(0, 0, 1, 1))                   # cadre et boulons : bronze sombre
    m_verre = materiau("hublot_verre", "verre", 2, 0.08, bandes=(1, 2, 2, 3))            # hublot : cyan sombre
    m_cadre_gris = materiau("cadre_gris", "metal", 2, 0.3, bandes=(1, 2, 3, 3))          # cadre épais gris
    m_reflet = materiau("hublot_reflet", "verre", 5, 0.05, bandes=(3, 4, 5, 5))          # reflet clair
    m_ceinture = materiau("ceinture", "cuivre", 2, 0.7, bandes=(1, 2, 2, 3))             # ceinture brune
    m_boucle = materiau("boucle", "laiton", 3, 0.25, bandes=(2, 3, 3, 3))                # boucle laiton
    m_tuyau = materiau("tuyau", "cuivre", 3, 0.5, bandes=(1, 2, 3, 4))                   # tuyau de corde
    m_bout = materiau("bouteilles", "bouteille", 2, 0.4, bandes=(1, 2, 3, 4))            # bouteilles de dos
    m_palme = materiau("palmes", "bouteille", 3, 0.45, bandes=(1, 2, 3, 4))

    pieces = []
    # casque : sphère, hublot sur la face, cadre bronze, boulons, anneau de cou
    pieces.append(sphere(P(0, 0, 39), 9 * PX, m_laiton))
    pieces.append(sphere(P(0, -7.8, 39), 5.0 * PX, m_verre))
    pieces.append(sphere(P(-2.1, -10.8, 41.8), 1.0 * PX, m_reflet))
    cadre = anneau(P(0, -8.6, 39), 6.2 * PX, 1.5 * PX, m_cadre_gris)
    cadre.rotation_euler = (math.pi / 2, 0.0, 0.0)
    pieces.append(cadre)
    for b in ((-7.6, -3.6, 38), (7.6, -3.6, 38), (0, -8.4, 46)):
        pieces.append(sphere(P(*b), 1.1 * PX, m_cadre))
    # collerette en laiton clair entre casque et tronc : bande de 3 px, avec trois boulons sur le devant
    m_collerette = materiau("collerette", "laiton", 3, 0.25, bandes=(2, 3, 3, 3))
    pieces.append(tube(P(0, 0, 29.2), P(0, 0, 32.2), 6.9 * PX, m_collerette, cotes=24))
    for b in ((-4.0, -5.7, 30.7), (0.0, -7.0, 30.7), (4.0, -5.7, 30.7)):
        pieces.append(sphere(P(*b), 1.2 * PX, m_cadre))
    # tronc court et bassin (plus étroits que les épaules)
    pieces.append(sphere(P(0, 0, 23), 7 * PX, m_tronc, (0.89, 0.65, 1.0)))
    pieces.append(sphere(P(0, 0, 14.5), 5.6 * PX, m_tronc, (1.0, 0.75, 0.6)))
    pieces.append(anneau(P(0, 0, 17.2), 7.3 * PX, 1.4 * PX, m_ceinture))
    pieces.append(sphere(P(0, -8.6, 17.2), 1.6 * PX, m_boucle, (1.0, 0.55, 1.0)))             # boucle sur le devant, qui sort de la ceinture
    # bouteilles de dos et tuyau de corde devant
    for s in (-1.0, 1.0):
        pieces.append(tube(P(3.2 * s, 4.2, 13), P(3.2 * s, 4.2, 30), 2.2 * PX, m_bout))
    for a_, b_ in ((P(4.5, -6.0, 33), P(6.2, -6.4, 24)), (P(6.2, -6.4, 24), P(4.0, -6.2, 17))):
        pieces.append(tube(a_, b_, 1.7 * PX, m_tuyau))
    # bras, gants, jambes, bottes, palmes : symétriques
    for s, x in (("g", -1.0), ("d", 1.0)):
        a1, b1 = OS_REPOS_PX[f"bras_{s}_1"][0], OS_REPOS_PX[f"bras_{s}_1"][1]
        a2, b2 = OS_REPOS_PX[f"bras_{s}_2"][0], OS_REPOS_PX[f"bras_{s}_2"][1]
        pieces.append(sphere(P(*a1), 2.7 * PX, m_bras[s]))
        pieces.append(tube(P(*a1), P(*b1), 2.5 * PX, m_bras[s]))
        pieces.append(sphere(P(*b1), 2.6 * PX, m_bras[s]))
        pieces.append(tube(P(*a2), P(*b2), 2.3 * PX, m_bras[s]))
        pieces.append(sphere(P(b2[0] + x * 0.5, b2[1], b2[2] - 1.5), 3.4 * PX, m_gant[s], (1.0, 1.0, 1.1)))   # moufle plus petite
        pieces.append(anneau(P(b2[0], b2[1], b2[2] + 2.0), 3.2 * PX, 0.9 * PX, m_gant[s]))
        a1, b1 = OS_REPOS_PX[f"jambe_{s}_1"][0], OS_REPOS_PX[f"jambe_{s}_1"][1]
        a2, b2 = OS_REPOS_PX[f"jambe_{s}_2"][0], OS_REPOS_PX[f"jambe_{s}_2"][1]
        pieces.append(tube(P(*a1), P(*b1), 3.2 * PX, m_jambe[s]))
        pieces.append(sphere(P(*b1), 3.2 * PX, m_jambe[s]))
        pieces.append(tube(P(*a2), P(*b2), 2.9 * PX, m_jambe[s]))
        pieces.append(sphere(P(b2[0] + x * 0.8, -2.5, 3.3), 4.0 * PX, m_botte[s], (1.1, 1.6, 0.75)))   # bottes écartées
        pieces.append(anneau(P(b2[0], b2[1], b2[2] + 1.8), 3.0 * PX, 0.9 * PX, m_botte[s]))
        pieces.append(sphere(P(x * 7.0, -7.2, 1.6), 3.0 * PX, m_palme, (1.3, 0.8, 0.35)))

    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    corps = bpy.context.active_object
    corps.name = "Plongeur"
    return corps


# ------------------------------------------------------------------ poses
def poser(sq, f, nom, rx=0.0, ry=0.0, rz=0.0, loc=None):
    """Rotation de l'os en trois axes (locaux) : rx = avant/arrière, rz = côté (écart des membres)."""
    pb = sq.pose.bones[nom]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (rx, ry, rz)
    pb.keyframe_insert("rotation_euler", frame=f)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=f)


def pose_idle(sq, f, t):
    """Pose debout de trois quarts : respiration, bras en A (écartés, coudes pliés), jambes écartées."""
    s = math.sin
    poser(sq, f, "buste", rx=0.0, ry=0.0, rz=0.0, loc=(0.0, 0.0, 0.35 * PX * s(t)))
    poser(sq, f, "tete", rx=0.0, ry=0.0, rz=0.0)
    for c, x, dph in (("g", -1.0, 0.0), ("d", 1.0, math.pi)):
        poser(sq, f, f"bras_{c}_1", rx=0.10 * s(t + dph), ry=0.0, rz=-x * 0.42)     # bras écartés, léger balancement
        poser(sq, f, f"bras_{c}_2", rx=0.35, ry=0.0, rz=-x * 0.10)                  # coude plié vers l'avant
        poser(sq, f, f"jambe_{c}_1", rx=0.03 * s(t + dph), ry=0.0, rz=x * 0.06)     # hanches écartées
        poser(sq, f, f"jambe_{c}_2", rx=0.10, ry=0.0, rz=0.0)                       # genou marqué


def animer(sq):
    for f in FRAMES:
        pose_idle(sq, f, 2 * math.pi * (f - 1) / 6)


# ------------------------------------------------------------------ scène
def camera(scene):
    """Caméra orthographique : face tournée vers -Y ; AZIMUT depuis la face vers +X (0 = face, 90 = profil +X)."""
    cam = bpy.data.cameras.new("Camera")
    cam.type = "ORTHO"
    cam.ortho_scale = LARGEUR_CADRE
    o = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(o)
    az, el = math.radians(AZIMUT), math.radians(ELEVATION)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cible = Vector((0.0, 0.0, 24 * PX))                                  # centre de la silhouette (z = 24 px)
    o.location = cible + d * 10.0
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (-d).normalized().to_track_quat("-Z", "Y")
    scene.camera = o


def eclairer(scene):
    lum = bpy.data.lights.new("Soleil", "SUN")
    lum.energy = 3.0
    o = bpy.data.objects.new("Soleil", lum)
    scene.collection.objects.link(o)
    o.location = (4.0, -6.0, 8.0)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((-0.4, 0.6, -0.8)).normalized().to_track_quat("-Z", "Y")


def reglages_rendu(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RES
    scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    try:
        scene.eevee.taa_render_samples = ECHANTILLONS
    except AttributeError:
        pass


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    corps = construire_modele()
    sq = construire_squelette()
    poids_par_distance(corps, sq)
    animer(sq)
    eclairer(scene)
    camera(scene)
    reglages_rendu(scene)
    scene.frame_start = 1
    scene.frame_end = max(FRAMES)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    if os.environ.get("PLONGEUR_IDENTITE"):
        images = [int(v) for v in os.environ.get("PLONGEUR_IDENTITE_IMAGES", ",".join(str(f) for f in FRAMES)).split(",")]
        rendre_identite(scene, corps, images)
        return
    os.makedirs(SORTIE, exist_ok=True)
    for f in FRAMES:
        chemin = os.path.join(SORTIE, IMAGES[f] + ".png")
        if os.path.exists(chemin):
            os.remove(chemin)
        scene.frame_set(f)
        scene.render.filepath = chemin
        bpy.ops.render.render(write_still=True)
        print("RENDU", IMAGES[f])


main()
