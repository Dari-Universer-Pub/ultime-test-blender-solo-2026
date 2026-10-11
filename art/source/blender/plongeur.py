"""
plongeur.py - le plongeur de LES CLOCHES DE VAREKH (M0), construit de zero dans Blender.

Ce script refait tout : le modele (primitives assemblees en UN seul maillage), le squelette,
les poids des os (calcules par distance), les poses animees (nage 8 images, idle 6 images),
la camera orthographique fixe de profil, la lumiere, le rendu. Il ecrit :

    art/source/blender/plongeur.blend       la scene
    art/rendu/plongeur/nage_01.png ...      rendus 512 px, fond transparent (8 px par pixel final)
    art/rendu/plongeur/idle_01.png ...

Lancement (depuis la racine du projet) :
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/plongeur.py

Le plongeur regarde vers +X (vers la droite de l'image). Z est le haut. La camera est en -Y.
"""
import json
import math
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SORTIE = os.environ.get("PLONGEUR_SORTIE", os.path.join(ROOT, "art", "rendu", "plongeur"))   # test : autre dossier de sortie
BLEND = os.path.join(HERE, "plongeur.blend")

RES = int(os.environ.get("PLONGEUR_RES", "640"))            # 640 = 8 x 80 px (case de 80 px, plongeur de 46 à 48 px)
ECHANTILLONS = int(os.environ.get("PLONGEUR_ECHANTILLONS", "64"))
# Apercu : PLONGEUR_IMAGES="1,9" ne rend que ces images (le rendu final rend toutes les images)
APERCU = {int(v) for v in os.environ.get("PLONGEUR_IMAGES", "").split(",") if v.strip()}
NAGE, IDLE = 8, 6
LARGEUR_CADRE = 4.12    # unites de monde couvertes par la largeur de la case de 80 px : le plongeur y fait 46 a 48 px (59 %)
SOUPLESSE = 0.10        # largeur de la transition des poids entre deux os (unites de monde)

PAL = json.load(open(os.path.join(ROOT, "art", "palette.json"), encoding="utf-8"))["rampes"]


def couleur_lin(rampe, i):
    """Couleur lineaire (Blender) d'un ton de la palette du projet."""
    h = PAL[rampe][i].lstrip("#")
    srgb = [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def materiau(nom, rampe, i, rugosite=0.55, emission=0.0, bandes=(1, 2, 3, 4)):
    """Materiau a 4 tons (ombrage en paliers) : Principled -> Shader to RGB -> rampe en paliers -> Emission.
    Les paliers sont des tons de la palette (indices de la rampe), du plus sombre au plus clair."""
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
    positions = ([0.0, 0.18, 0.42] if len(bandes) == 3 else [0.0, 0.16, 0.34, 0.56])[:len(bandes)]   # seuils : 4 tons répartis sur la lumière (retouche 3)
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


# ------------------------------------------------------------------ squelette
# Positions au repos (debout, flottant), exprimées en PIXELS du rendu final : 1 px = PX unités de monde.
# Origine = hanche. Les os "g" sont du côté proche (-Y), les "d" du côté lointain.
# Proportions de dessin animé (M4, demande de Julien) : grosse tête (casque), tronc court, bras et jambes
# courts et épais, gros gants et grosses bottes. Hauteur totale 46 à 48 px.
PX = 0.0466
OS_REPOS_PX = {
    "hanche":   ((0, 0, -6), (0, 0, 0), None),
    "buste":    ((0, 0, 0), (0, 0, 9), "hanche"),
    "tete":     ((0, 0, 9), (1, 0, 18), "buste"),
}
for _c, _s in (("g", -1.0), ("d", 1.0)):
    _kx, _ax = (3, 4) if _c == "g" else (-2, -3)   # pas écarté : jambe proche en avant, lointaine en arrière
    _ex, _wx = (3, 6) if _c == "g" else (-2, -3)   # bras : coude et poignet vers l'avant (proche) ou l'arrière (lointain)
    OS_REPOS_PX.update({
        f"bras_{_c}_1": ((0, _s * 6, 6), (_ex, _s * 7, -3), "buste"),
        f"bras_{_c}_2": ((_ex, _s * 7, -3), (_wx, _s * 7, -10), f"bras_{_c}_1"),
        f"jambe_{_c}_1": ((0, _s * 3.5, -6), (_kx, _s * 3.5, -14), "hanche"),
        f"jambe_{_c}_2": ((_kx, _s * 3.5, -14), (_ax, _s * 3.5, -19), f"jambe_{_c}_1"),
        f"pied_{_c}": ((_ax, _s * 3.5, -19), (_ax + 4, _s * 3.5, -20), f"jambe_{_c}_2"),
    })
OS_REPOS = {nom: (tuple(v * PX for v in a), tuple(v * PX for v in b), parent)
            for nom, (a, b, parent) in OS_REPOS_PX.items()}


def P(*v):
    """Pixels du rendu final -> unités de monde."""
    return tuple(x * PX for x in v)


# Carte d'identité (mesure M4) : chaque matériau du modèle appartient à un groupe, rendu en couleur plate
# (sans ombrage) pour mesurer, image par image, quelle partie est visible. Nom de matériau -> (groupe, couleur).
GROUPES_ID = {
    "tronc": ("tronc", "#ff0000"), "tete": ("tete", "#ffd400"), "cadre_hublot": ("tete", "#ffd400"),
    "hublot_verre": ("tete", "#ffd400"), "ceinture": ("ceinture", "#7a3cff"), "tuyau": ("tuyau", "#00e0ff"),
    "bouteilles": ("bouteilles", "#ff7f00"), "palmes": ("palmes", "#ff00c8"), "lampe": ("lampe", "#ffffff"),
    "lampe_tube": ("lampe", "#ffffff"), "bras_proche": ("bras_proche", "#00ff00"),
    "bras_lointain": ("bras_lointain", "#005000"), "jambe_proche": ("jambe_proche", "#0000ff"),
    "jambe_lointaine": ("jambe_lointaine", "#000090"), "gant_proche": ("gant_proche", "#a0ff00"),
    "gant_lointain": ("gant_lointain", "#00a070"), "botte_proche": ("botte_proche", "#ff0080"),
    "botte_lointaine": ("botte_lointaine", "#ff80c0"),
}
GROUPES = ["tronc", "tete", "ceinture", "tuyau", "bouteilles", "palmes", "lampe", "bras_proche", "bras_lointain",
           "jambe_proche", "jambe_lointaine", "gant_proche", "gant_lointain", "botte_proche", "botte_lointaine"]


def construire_modele():
    # tronc et côté lointain : kaki intermédiaire, et kaki le plus foncé pour le lointain (net, pas noir)
    m_tronc = materiau("tronc", "kaki", 1, 0.5, bandes=(0, 1, 2))
    m_bras_proche = materiau("bras_proche", "kaki", 3, 0.5, bandes=(2, 3, 3))            # bras proche : le plus clair
    m_bras_lointain = materiau("bras_lointain", "kaki", 0, 0.6, bandes=(0, 0, 1))        # bras lointain : kaki foncé
    m_jambe_proche = materiau("jambe_proche", "kaki", 2, 0.5, bandes=(1, 2, 2))          # jambe proche : kaki clair
    m_jambe_lointaine = materiau("jambe_lointaine", "kaki", 0, 0.6, bandes=(0, 0, 1))    # jambe lointaine : kaki foncé
    m_laiton = materiau("tete", "laiton", 2, 0.25, bandes=(1, 2, 3, 3))                  # casque laiton doré
    m_verre = materiau("hublot_verre", "verre", 4, 0.08, bandes=(2, 3, 4, 5))            # hublot clair
    m_cadre = materiau("cadre_hublot", "laiton", 0, 0.3, bandes=(0, 0, 1, 1))            # cadre : bronze sombre
    m_gant_proche = materiau("gant_proche", "gant", 1, 0.6, bandes=(0, 1, 2))            # gants : bleu-violet très sombre
    m_gant_lointain = materiau("gant_lointain", "gant", 1, 0.6, bandes=(0, 1, 2))
    m_botte_proche = materiau("botte_proche", "gant", 1, 0.6, bandes=(0, 1, 2))          # bottes : idem
    m_botte_lointaine = materiau("botte_lointaine", "gant", 1, 0.6, bandes=(0, 1, 2))
    m_ceinture = materiau("ceinture", "gant", 1, 0.7, bandes=(0, 1, 2))                  # ceinture de lest
    m_metal = materiau("lampe_tube", "metal", 3, 0.35)
    m_tuyau = materiau("tuyau", "cuivre", 3, 0.5, bandes=(1, 2, 3, 4))                   # tuyau d'air : corde beige-brun
    m_bout = materiau("bouteilles", "bouteille", 2, 0.4, bandes=(1, 2, 3, 4))            # bouteilles de dos
    m_palme = materiau("palmes", "bouteille", 3, 0.45, bandes=(1, 2, 3, 4))
    m_lampe = materiau("lampe", "lampe", 3, 0.3, emission=2.0)

    pieces = []
    # casque en laiton : grosse sphère, hublot clair, cadre bronze face caméra, boulons, anneau de cou
    pieces.append(sphere(P(1, 0, 18), 9 * PX, m_laiton))
    pieces.append(sphere(P(7, 0, 19), 5.5 * PX, m_verre))
    cadre = anneau(P(7, -1, 19), 7 * PX, 1.5 * PX, m_cadre)
    cadre.rotation_euler = (math.pi / 2, 0.0, 0.0)
    pieces.append(cadre)
    for b in ((1, -8, 26), (5, -8, 12), (-4, -7, 19)):
        pieces.append(sphere(P(*b), 1.2 * PX, m_laiton))
    pieces.append(anneau(P(0, 0, 9), 6 * PX, 1.5 * PX, m_laiton))
    # tronc court, bassin, ceinture de lest
    pieces.append(sphere(P(0, 0, 3), 7 * PX, m_tronc, (1.0, 0.85, 1.0)))
    pieces.append(sphere(P(0, 0, -6), 6 * PX, m_tronc, (0.9, 0.8, 0.7)))
    pieces.append(anneau(P(0, 0, -2), 7.5 * PX, 1.5 * PX, m_ceinture))
    # bouteilles de dos et tuyau d'air (corde) : courbe à l'arrière
    for s in (-1.0, 1.0):
        pieces.append(tube(P(-6, s * 3, -4), P(-6, s * 3, 12), 2.5 * PX, m_bout))
    for a_, b_ in ((P(-5, 0, 24), P(-11, 0, 20)), (P(-11, 0, 20), P(-13, 0, 10)), (P(-13, 0, 10), P(-10, 0, -2)), (P(-10, 0, -2), P(-8, 0, -6))):
        pieces.append(tube(a_, b_, 1.8 * PX, m_tuyau))
    # lampe de casque, jaune et allumée
    pieces.append(tube(P(9, 0, 25), P(12, 0, 25), 0.8 * PX, m_metal))
    pieces.append(sphere(P(13, 0, 25), 2 * PX, m_lampe))
    # bras et jambes courts et épais, gros gants, grosses bottes, palmes
    for c, s in (("g", -1.0), ("d", 1.0)):
        m_bras = m_bras_proche if c == "g" else m_bras_lointain
        m_jambe = m_jambe_proche if c == "g" else m_jambe_lointaine
        m_gant = m_gant_proche if c == "g" else m_gant_lointain
        m_botte = m_botte_proche if c == "g" else m_botte_lointaine
        a1, b1 = OS_REPOS_PX[f"bras_{c}_1"][0], OS_REPOS_PX[f"bras_{c}_1"][1]
        a2, b2 = OS_REPOS_PX[f"bras_{c}_2"][0], OS_REPOS_PX[f"bras_{c}_2"][1]
        pieces.append(tube(P(*a1), P(*b1), 2.6 * PX, m_bras))
        pieces.append(tube(P(*a2), P(*b2), 2.4 * PX, m_bras))
        pieces.append(sphere(P(*b1), 2.6 * PX, m_bras))
        pieces.append(sphere(P(*b2), 4.5 * PX, m_gant))
        a1, b1 = OS_REPOS_PX[f"jambe_{c}_1"][0], OS_REPOS_PX[f"jambe_{c}_1"][1]
        a2, b2 = OS_REPOS_PX[f"jambe_{c}_2"][0], OS_REPOS_PX[f"jambe_{c}_2"][1]
        pieces.append(tube(P(*a1), P(*b1), 3.2 * PX, m_jambe))
        pieces.append(tube(P(*a2), P(*b2), 3.0 * PX, m_jambe))
        pieces.append(sphere(P(*b1), 3.2 * PX, m_jambe))
        pieces.append(sphere(P(7 if c == "g" else -4, s * 3.5, -19), 4 * PX, m_botte, (1.4, 1.0, 0.75)))
        pieces.append(sphere(P(10 if c == "g" else -1, s * 3.5, -21), 3 * PX, m_palme, (1.6, 0.9, 0.36)))

    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    corps = bpy.context.active_object
    corps.name = "Plongeur"
    return corps


def lin_hex(h):
    """Couleur hexadécimale sRGB -> linéaire (Blender), pour les matériaux plats de la carte d'identité."""
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


def rendre_identite(scene, corps, frames):
    """Carte d'identité : une image complète (couleurs plates), puis une image par groupe, seul sur la scène
    (les autres faces sont supprimées de copies du modèle). Écrit aussi la palette d'identité pour la pixelisation."""
    import bmesh
    dossier = os.path.join(SORTIE, "identite")
    os.makedirs(dossier, exist_ok=True)
    couleurs = {}
    noms_slots = []
    for i, mat in enumerate(list(corps.data.materials)):
        groupe, h = GROUPES_ID[mat.name]
        couleurs[groupe] = h
        noms_slots.append(groupe)
        corps.data.materials[i] = materiau_plat(groupe, h)
    with open(os.path.join(SORTIE, "identite_palette.json"), "w", encoding="utf-8") as fichier:
        json.dump({"rampes": {g: [couleurs[g]] for g in GROUPES}}, fichier, indent=1)
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(dossier, nom_image(f) + ".png")
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
        for f in frames:
            scene.frame_set(f)
            scene.render.filepath = os.path.join(dossier_g, nom_image(f) + ".png")
            bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(copie, do_unlink=True)
    print("IDENTITE_OK", len(GROUPES), "groupes", len(frames), "images")


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
    """Chaque sommet suit les os proches : poids decroissants avec la distance, 3 os au maximum."""
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


# ------------------------------------------------------------------ poses
def poser(sq, f, nom, rot=None, loc=None):
    """rot = (0, angle, 0) en degres-radians dans le plan de profil (X-Z).
    Dans Blender l'axe Y d'un os est sa longueur (torsion) : la flexion de profil est
    la rotation autour de l'axe Z local de l'os, d'ou le signe moins et la permutation."""
    pb = sq.pose.bones[nom]
    pb.rotation_mode = "XYZ"
    if rot is not None:
        pb.rotation_euler = (0.0, 0.0, -rot[1])
        pb.keyframe_insert("rotation_euler", frame=f)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=f)


def poser_profondeur(sq, f, nom, angle):
    """Rotation autour de l'axe X local de l'os : le membre balaie le plan de profondeur (Y-Z du corps).
    Dans une nage couchee, ce plan se projette a l'ecran sur l'axe du corps, donc le bras reste
    horizontal et ne passe jamais par la verticale."""
    pb = sq.pose.bones[nom]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (angle, 0.0, 0.0)
    pb.keyframe_insert("rotation_euler", frame=f)


# Cycle de nage en 8 images. Index 0 = preparation (bras ramenes sous le torse, jambes repliees),
# index 4 = glisse (bras allonges, jambes calmes). Table : elle donne l'anticipation et le temps de glisse.
BRAS_NAGE = [1.5, 1.3, 1.0, 0.7, 0.5, 0.6, 1.0, 1.4]     # rotation des bras (rad), sous le torse
JAMBES_NAGE = [0.15, 0.45, 0.60, 0.35, 0.10, 0.20, 0.50, 0.60]   # amplitude du battement (rad)


def pose_nage(sq, f, t):
    """Nage de profil, corps couché, tête vers +X. Sens des rotations des os : une rotation positive de l'os
    fait pointer le membre vers l'arrière-haut (vérifié sur la carte d'identité).
    Bras proche : balayage avant-bas, sous le casque (θ de 1,2 à 2,3 rad). Bras lointain : balayage vers le haut,
    au-dessus du tronc (θ de -1,8 à -1,2 rad). Jambes en ciseaux : la proche remonte vers l'arrière, la lointaine
    descend (θ = ∓(0,9 ± 0,25)), écart de plusieurs pixels, genou qui plie (M4, nage)."""
    s, c = math.sin, math.cos
    poser(sq, f, "hanche", rot=(0.0, 1.30 + 0.06 * s(t), 0.0), loc=(0.0, 0.0, 0.0))
    poser(sq, f, "buste", rot=(0.0, 0.22 * s(t + math.pi / 2), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.06 * s(t), 0.0))
    for c_, signe in (("g", 1.0), ("d", -1.0)):
        if c_ == "g":
            theta_bras = 1.85 - 0.45 * c(t)   # bras proche : tendu vers l'avant (2,3 rad), balayé vers le bas (1,4 rad)
        else:
            theta_bras = 1.35 - 0.15 * c(t)   # bras lointain : en opposition, vers le bas
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, theta_bras, 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, 0.3 if c_ == "g" else -0.2, 0.0))
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, -signe * (0.65 + 0.25 * s(t)), 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, -signe * (0.35 + 0.25 * c(t)), 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, -signe * 0.3 * s(t), 0.0))


def pose_idle(sq, f, t):
    """Flottement debout : bascule lente, bras qui se balancent, palmes qui frissonnent."""
    s = math.sin
    # respiration : la cage thoracique se souleve (buste 0,16 rad) et le corps monte-descend de 0,07 (2 px p-p a 0,062 u/px)
    poser(sq, f, "hanche", rot=(0.0, 0.05 * s(t), 0.0), loc=(0.0, 0.0, 0.07 * s(t)))
    poser(sq, f, "buste", rot=(0.0, 0.16 * s(t + 0.8), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.03 * s(t), 0.0))
    for c_, dephase in (("g", 0.0), ("d", math.pi)):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, 0.45 + 0.10 * s(t + dephase), 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, -0.10 + 0.10 * s(t + dephase + 0.6), 0.0))
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, 0.05 * s(t + dephase), 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, 0.05 * s(t + dephase + 0.5), 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, 0.18 * s(t + dephase), 0.0))


# Animations ajoutées en M3 : images 15 à 41, à la fin de la feuille (les images 1 à 14 ne bougent pas).
ANIMATIONS_M3 = [("creusage", 6), ("attaque", 6), ("saut", 4), ("degats", 3), ("mort", 8)]


def pose_creusage(sq, f, k, n):
    """Creusage : corps couché comme en nage, le bras droit frappe devant par va-et-vient."""
    t = 2 * math.pi * k / n
    s = math.sin
    poser(sq, f, "hanche", rot=(0.0, 1.30, 0.0), loc=(0.0, 0.0, 0.0))
    poser(sq, f, "buste", rot=(0.0, 0.10 * s(t), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.10, 0.0))
    poser(sq, f, "bras_d_1", rot=(0.0, 0.9 + 0.5 * s(t), 0.0))
    poser(sq, f, "bras_d_2", rot=(0.0, 0.5 + 0.35 * s(t + 0.4), 0.0))
    poser(sq, f, "bras_g_1", rot=(0.0, 0.8, 0.0))
    poser(sq, f, "bras_g_2", rot=(0.0, 0.3, 0.0))
    for c_, sg in (("g", 1.0), ("d", -1.0)):
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, sg * 0.35, 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, sg * 0.25, 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, sg * 0.2, 0.0))


ATTAQUE_BRAS = [-0.6, -0.2, 1.6, 2.0, 1.2, 0.5]   # préparation (bras en arrière), frappe, retour


def pose_attaque(sq, f, k, n):
    """Attaque : préparation (bras en arrière, avertissement), frappe vers l'avant, retour."""
    poser(sq, f, "hanche", rot=(0.0, 1.30, 0.0), loc=(0.0, 0.0, 0.0))
    poser(sq, f, "buste", rot=(0.0, 0.25 * math.sin(math.pi * k / n), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.10, 0.0))
    poser(sq, f, "bras_d_1", rot=(0.0, ATTAQUE_BRAS[k], 0.0))
    poser(sq, f, "bras_d_2", rot=(0.0, 0.3 + 0.4 * (ATTAQUE_BRAS[k] / 2.0), 0.0))
    poser(sq, f, "bras_g_1", rot=(0.0, 0.8, 0.0))
    poser(sq, f, "bras_g_2", rot=(0.0, 0.3, 0.0))
    for c_, sg in (("g", 1.0), ("d", -1.0)):
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, sg * (0.9 if k in (2, 3) else 0.3), 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, sg * 0.4, 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, sg * 0.2, 0.0))


SAUT_POSES = [0.9, -1.2, 0.4, 1.0]   # accroupi, poussée bras levés, apogée bras ouverts, réception


def pose_saut(sq, f, k, n):
    """Saut hors de l'eau : accroupi, poussée, apogée (corps étiré), réception accroupie."""
    hauteur = [-0.05, 0.12, 0.20, -0.08][k]
    poser(sq, f, "hanche", rot=(0.0, 0.05 * [1, 0, -1, 0][k], 0.0), loc=(0.0, 0.0, hauteur))
    poser(sq, f, "buste", rot=(0.0, 0.10 * [1, -1, 0, 1][k], 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.05, 0.0))
    for c_ in ("g", "d"):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, SAUT_POSES[k] if c_ == "g" else SAUT_POSES[k] * 0.8, 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, 0.2, 0.0))
    genou = [1.0, 0.5, 0.1, 0.9][k]
    for c_, sg in (("g", 1.0), ("d", -1.0)):
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, sg * genou, 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, sg * genou * 0.8, 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, sg * 0.2, 0.0))


def pose_degats(sq, f, k, n):
    """Dégâts : recul du buste et des bras, puis retour à la nage."""
    recul = [-0.45, -0.20, 0.0][k]
    poser(sq, f, "hanche", rot=(0.0, 1.30 + recul * 0.3, 0.0), loc=(0.0, 0.0, 0.0))
    poser(sq, f, "buste", rot=(0.0, recul, 0.0))
    poser(sq, f, "tete", rot=(0.0, -recul * 0.6, 0.0))
    for c_ in ("g", "d"):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, 1.4 + recul, 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, 0.5, 0.0))
    for c_, sg in (("g", 1.0), ("d", -1.0)):
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, sg * 0.4, 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, sg * 0.3, 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, sg * 0.2, 0.0))


def pose_mort(sq, f, k, n):
    """Mort : le corps bascule et s'affaisse, les bras et les jambes pendent."""
    u = k / (n - 1)
    poser(sq, f, "hanche", rot=(0.0, 1.30 + 0.9 * u, 0.0), loc=(0.0, 0.0, -0.12 * u))
    poser(sq, f, "buste", rot=(0.0, -0.20 + 0.5 * u, 0.0))
    poser(sq, f, "tete", rot=(0.0, 0.2 * u, 0.0))
    for c_ in ("g", "d"):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, 1.5 - 0.7 * u, 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, 0.4 - 0.2 * u, 0.0))
    for c_, sg in (("g", 1.0), ("d", -1.0)):
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, sg * 0.25, 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, sg * 0.15, 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, sg * 0.1, 0.0))


POSES_M3 = {"creusage": pose_creusage, "attaque": pose_attaque, "saut": pose_saut,
            "degats": pose_degats, "mort": pose_mort}


def animer(sq):
    for f in range(1, NAGE + 1):
        pose_nage(sq, f, 2 * math.pi * (f - 1) / NAGE)
    for f in range(NAGE + 1, NAGE + IDLE + 1):
        pose_idle(sq, f, 2 * math.pi * (f - NAGE - 1) / IDLE)
    f = NAGE + IDLE
    for nom, n in ANIMATIONS_M3:
        for k in range(n):
            f += 1
            POSES_M3[nom](sq, f, k, n)
    return f


def nom_image(f):
    """Nom de fichier d'une image de la feuille : nage_01 .. idle_06 .. creusage_01 .. mort_08."""
    if f <= NAGE:
        return f"nage_{f:02d}"
    if f <= NAGE + IDLE:
        return f"idle_{f - NAGE:02d}"
    f2 = f - NAGE - IDLE
    for nom, n in ANIMATIONS_M3:
        if f2 <= n:
            return f"{nom}_{f2:02d}"
        f2 -= n
    return f"image_{f:02d}"


def animer_bulle():
    """Bulle de respiration : sort de l'arriere du casque (au-dessus, loin de la visiere) et monte
    de 0,18 pendant les images idle ; elle est invisible en nage."""
    m = materiau("bulle_air", "bulle", 3, 0.2)
    b = sphere((-0.20, 0.0, 0.98), 0.08, m)
    b.name = "bulle_respiration"
    for f in range(1, NAGE + IDLE + 1 + sum(n for _, n in ANIMATIONS_M3)):
        if f <= NAGE or f > NAGE + IDLE:
            b.scale = (0.001, 0.001, 0.001)
            b.location = (-0.20, 0.0, 0.98)
        else:
            t = (f - NAGE - 1) / IDLE
            b.scale = (1.0, 1.0, 1.0)
            b.location = (-0.20, 0.0, 0.98 + 0.18 * t)
        b.keyframe_insert("scale", frame=f)
        b.keyframe_insert("location", frame=f)
    return b


# ------------------------------------------------------------------ scene
def orienter(objet, direction):
    """Oriente l'axe -Z de l'objet vers 'direction' (piege : une camera regarde vers -Z)."""
    objet.rotation_mode = "QUATERNION"
    objet.rotation_quaternion = Vector(direction).normalized().to_track_quat("-Z", "Z")


def eclairer(scene):
    def soleil(nom, travel, energie, teinte):
        l = bpy.data.lights.new(nom, "SUN")
        l.energy = energie
        l.color = teinte
        o = bpy.data.objects.new(nom, l)
        scene.collection.objects.link(o)
        orienter(o, travel)
    # clef : haut-gauche (le faisceau voyage de (-X, -Y, +Z) vers le centre)
    soleil("clef", (3.0, 4.0, -5.0), 4.2, (1.0, 0.93, 0.80))
    # contre-jour froid : bas-droite, arriere
    soleil("contre_jour", (-3.0, -3.0, 1.0), 1.4, (0.60, 0.78, 1.0))
    scene.world = bpy.data.worlds.new("Monde")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.10, 0.16, 0.22, 1.0)
    bg.inputs["Strength"].default_value = 0.6


def camera(scene):
    cam = bpy.data.cameras.new("Camera")
    cam.type = "ORTHO"
    cam.ortho_scale = LARGEUR_CADRE
    o = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(o)
    o.location = (0.0, -10.0, -0.05)
    orienter(o, (0.0, 1.0, 0.0))
    scene.camera = o


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
    dernier = animer(sq)
    animer_bulle()
    eclairer(scene)
    camera(scene)
    reglages_rendu(scene)
    scene.frame_start = 1
    scene.frame_end = dernier
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    os.makedirs(SORTIE, exist_ok=True)
    if os.environ.get("PLONGEUR_IDENTITE"):
        rendre_identite(scene, corps, [1, 2, 3, 4, 5, 6, 7, 8])
        return
    for f in range(1, dernier + 1):
        if APERCU and f not in APERCU:
            continue
        nom = nom_image(f)
        chemin = os.path.join(SORTIE, nom + ".png")
        if os.path.exists(chemin):
            os.remove(chemin)
        scene.frame_set(f)
        scene.render.filepath = chemin
        bpy.ops.render.render(write_still=True)
        print("RENDU", nom, os.path.getsize(chemin), "octets")


main()
