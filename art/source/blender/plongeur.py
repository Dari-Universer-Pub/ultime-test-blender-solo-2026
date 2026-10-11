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
SORTIE = os.path.join(ROOT, "art", "rendu", "plongeur")
BLEND = os.path.join(HERE, "plongeur.blend")

RES = int(os.environ.get("PLONGEUR_RES", "512"))            # 512 = 8 x 64 px
ECHANTILLONS = int(os.environ.get("PLONGEUR_ECHANTILLONS", "64"))
# Apercu : PLONGEUR_IMAGES="1,9" ne rend que ces images (le rendu final rend toutes les images)
APERCU = {int(v) for v in os.environ.get("PLONGEUR_IMAGES", "").split(",") if v.strip()}
NAGE, IDLE = 8, 6
LARGEUR_CADRE = 3.2     # unites de monde couvertes par la largeur de l'image (64 px : 0,05 par pixel)
SOUPLESSE = 0.14        # largeur de la transition des poids entre deux os (unites de monde)

PAL = json.load(open(os.path.join(ROOT, "art", "palette.json"), encoding="utf-8"))["rampes"]


def couleur_lin(rampe, i):
    """Couleur lineaire (Blender) d'un ton de la palette du projet."""
    h = PAL[rampe][i].lstrip("#")
    srgb = [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def materiau(nom, rampe, i, rugosite=0.55, emission=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    rgb = couleur_lin(rampe, i)
    b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    b.inputs["Roughness"].default_value = rugosite
    if emission:
        b.inputs["Emission Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        b.inputs["Emission Strength"].default_value = emission
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
# Positions au repos (debout, flottant). Les os "g" sont du cote proche (-Y), les "d" du cote lointain.
OS_REPOS = {
    "hanche":   ((0.0, 0.0, -0.20), (0.0, 0.0, 0.0), None),
    "buste":    ((0.0, 0.0, 0.00), (0.0, 0.0, 0.36), "hanche"),
    "tete":     ((0.0, 0.0, 0.36), (0.02, 0.0, 0.62), "buste"),
}
for _c, _s in (("g", -1.0), ("d", 1.0)):
    OS_REPOS.update({
        f"bras_{_c}_1": ((0.0, _s * 0.30, 0.22), (0.04, _s * 0.34, -0.10), "buste"),
        f"bras_{_c}_2": ((0.04, _s * 0.34, -0.10), (0.10, _s * 0.36, -0.36), f"bras_{_c}_1"),
        f"jambe_{_c}_1": ((0.0, _s * 0.12, -0.20), (0.03, _s * 0.12, -0.62), "hanche"),
        f"jambe_{_c}_2": ((0.03, _s * 0.12, -0.62), (0.0, _s * 0.12, -0.94), f"jambe_{_c}_1"),
        f"pied_{_c}": ((0.0, _s * 0.12, -0.94), (0.22, _s * 0.12, -0.99), f"jambe_{_c}_2"),
    })


def construire_modele():
    m_comb = materiau("combinaison", "combinaison", 4, 0.5)          # orange vif : il tranche sur l'eau
    m_comb_ombre = materiau("combinaison_ombre", "combinaison", 2, 0.6)
    m_verre = materiau("hublot_verre", "verre", 3, 0.08)
    m_metal = materiau("metal", "metal", 3, 0.35)
    m_caout = materiau("caoutchouc", "caoutchouc", 2, 0.7)
    m_palme = materiau("palmes", "palmes", 3, 0.45)
    m_bout = materiau("bouteilles", "bouteille", 3, 0.4)
    m_lampe = materiau("lampe", "lampe", 3, 0.3, emission=2.0)

    pieces = []
    # casque, hublot cercle, bague de col
    pieces.append(sphere((0.02, 0.0, 0.62), 0.30, m_comb))
    pieces.append(sphere((0.33, 0.0, 0.66), 0.21, m_verre, (0.45, 1.0, 1.0)))
    pieces.append(anneau((0.02, 0.0, 0.30), 0.25, 0.045, m_metal))
    # torse
    pieces.append(sphere((0.0, 0.0, 0.02), 0.30, m_comb, (0.75, 0.62, 0.95)))
    # bouteilles de dos
    for s in (-0.12, 0.12):
        pieces.append(tube((-0.27, s, -0.25), (-0.27, s, 0.45), 0.10, m_bout))
    # ceinture
    pieces.append(anneau((0.0, 0.0, -0.22), 0.30, 0.05, m_caout, (0.8, 0.62, 1.0)))
    # lampe de casque
    pieces.append(tube((0.28, 0.0, 0.95), (0.42, 0.0, 0.95), 0.035, m_metal))
    pieces.append(sphere((0.44, 0.0, 0.95), 0.07, m_lampe))
    # bras, jambes, gants, bottes, palmes
    for c, s in (("g", -1.0), ("d", 1.0)):
        ep = m_comb if c == "g" else m_comb_ombre
        e2 = OS_REPOS[f"bras_{c}_2"][1]
        pieces.append(tube(OS_REPOS[f"bras_{c}_1"][0], OS_REPOS[f"bras_{c}_1"][1], 0.085, ep))
        pieces.append(tube(OS_REPOS[f"bras_{c}_2"][0], OS_REPOS[f"bras_{c}_2"][1], 0.072, ep))
        pieces.append(sphere(OS_REPOS[f"bras_{c}_1"][0], 0.095, ep))
        pieces.append(sphere(OS_REPOS[f"bras_{c}_1"][1], 0.075, ep))
        pieces.append(sphere(e2, 0.09, m_caout))
        pieces.append(tube(OS_REPOS[f"jambe_{c}_1"][0], OS_REPOS[f"jambe_{c}_1"][1], 0.105, ep))
        pieces.append(tube(OS_REPOS[f"jambe_{c}_2"][0], OS_REPOS[f"jambe_{c}_2"][1], 0.09, ep))
        pieces.append(sphere(OS_REPOS[f"jambe_{c}_1"][1], 0.10, ep))
        pieces.append(sphere(OS_REPOS[f"jambe_{c}_2"][1], 0.11, m_caout))
        pieces.append(sphere((0.20, s * 0.12, -1.0), 0.16, m_palme, (1.3, 0.8, 0.28)))

    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    corps = bpy.context.active_object
    corps.name = "Plongeur"
    return corps


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


def pose_nage(sq, f, t):
    """Nage de profil : corps couche, tete vers +X, bras en brasse, jambes qui battent."""
    s, c = math.sin, math.cos
    poser(sq, f, "hanche", rot=(0.0, 1.30 + 0.06 * s(t), 0.0), loc=(0.0, 0.0, 0.0))
    poser(sq, f, "buste", rot=(0.0, 0.10 * s(t + math.pi / 2), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.06 * s(t), 0.0))
    for c_, dephase in (("g", 0.0), ("d", math.pi)):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, -2.6 + 0.9 * s(t + dephase), 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, -0.5 + 0.5 * s(t + dephase + math.pi / 2), 0.0))
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, 0.30 * s(t + dephase + math.pi), 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, 0.25 * s(t + dephase + math.pi / 2), 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, 0.35 * s(t + dephase), 0.0))


def pose_idle(sq, f, t):
    """Flottement debout : bascule lente, bras qui se balancent, palmes qui frissonnent."""
    s = math.sin
    poser(sq, f, "hanche", rot=(0.0, 0.05 * s(t), 0.0), loc=(0.0, 0.0, 0.03 * s(t)))
    poser(sq, f, "buste", rot=(0.0, 0.04 * s(t + 0.8), 0.0))
    poser(sq, f, "tete", rot=(0.0, -0.03 * s(t), 0.0))
    for c_, dephase in (("g", 0.0), ("d", math.pi)):
        poser(sq, f, f"bras_{c_}_1", rot=(0.0, -0.60 + 0.12 * s(t + dephase), 0.0))
        poser(sq, f, f"bras_{c_}_2", rot=(0.0, -0.10 + 0.10 * s(t + dephase + 0.6), 0.0))
        poser(sq, f, f"jambe_{c_}_1", rot=(0.0, 0.05 * s(t + dephase), 0.0))
        poser(sq, f, f"jambe_{c_}_2", rot=(0.0, 0.05 * s(t + dephase + 0.5), 0.0))
        poser(sq, f, f"pied_{c_}", rot=(0.0, 0.18 * s(t + dephase), 0.0))


def animer(sq):
    for f in range(1, NAGE + 1):
        pose_nage(sq, f, 2 * math.pi * (f - 1) / NAGE)
    for f in range(NAGE + 1, NAGE + IDLE + 1):
        pose_idle(sq, f, 2 * math.pi * (f - NAGE - 1) / IDLE)
    return NAGE + IDLE


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
    eclairer(scene)
    camera(scene)
    reglages_rendu(scene)
    scene.frame_start = 1
    scene.frame_end = dernier
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    os.makedirs(SORTIE, exist_ok=True)
    for f in range(1, dernier + 1):
        if APERCU and f not in APERCU:
            continue
        nom = f"nage_{f:02d}" if f <= NAGE else f"idle_{f - NAGE:02d}"
        chemin = os.path.join(SORTIE, nom + ".png")
        if os.path.exists(chemin):
            os.remove(chemin)
        scene.frame_set(f)
        scene.render.filepath = chemin
        bpy.ops.render.render(write_still=True)
        print("RENDU", nom, os.path.getsize(chemin), "octets")


main()
