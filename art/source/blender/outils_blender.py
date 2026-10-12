"""
outils_blender.py - fonctions communes aux scripts Blender du projet (M3 et suivants).

Ce module ne dessine rien seul : il fournit les réglages communs de STYLE.md (caméra orthographique,
lumière clef en haut à gauche, matériaux en paliers de la palette, rendu EEVEE transparent) et
des primitives de modélisation. Chaque asset garde son script (art/source/blender/<id>.py) qui
refait tout de zéro en important ce module.

Lancement d'un script (depuis la racine) :
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/<id>.py
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PAL = json.load(open(os.path.join(ROOT, "art", "palette.json"), encoding="utf-8"))["rampes"]


def couleur_lin(rampe, i):
    """Couleur linéaire (Blender) d'un ton de la palette du projet."""
    h = PAL[rampe][i].lstrip("#")
    srgb = [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def materiau(nom, rampe, bandes=(1, 2, 3, 4), rugosite=0.6, seuils=None):
    """Matériau en paliers : Principled -> Shader to RGB -> rampe CONSTANT (tons de la palette) -> Emission."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    principled = arbre.nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = (*couleur_lin(rampe, bandes[-1]), 1.0)
    principled.inputs["Roughness"].default_value = rugosite
    lumiere = arbre.nodes.new("ShaderNodeShaderToRGB")
    paliers = arbre.nodes.new("ShaderNodeValToRGB")
    paliers.color_ramp.interpolation = "CONSTANT"
    el = paliers.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    if seuils is None:
        seuils = [0.0, 0.10, 0.22, 0.38][:len(bandes)] if len(bandes) == 4 else [0.0, 0.18, 0.42][:len(bandes)]
    for k, (pos, idx) in enumerate(zip(seuils, bandes)):
        c = couleur_lin(rampe, idx)
        if k == 0:
            el[0].position = pos
            el[0].color = (c[0], c[1], c[2], 1.0)
        else:
            el.new(pos).color = (c[0], c[1], c[2], 1.0)
    emission = arbre.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    arbre.links.new(principled.outputs["BSDF"], lumiere.inputs["Shader"])
    arbre.links.new(lumiere.outputs["Color"], paliers.inputs["Fac"])
    arbre.links.new(paliers.outputs["Color"], emission.inputs["Color"])
    arbre.links.new(emission.outputs["Emission"], sortie.inputs["Surface"])
    return m


def materiau_matiere(nom, rampe):
    """Matière (roche, bois, tôle) : bruit -> couleur de base ; éclairage -> paliers de la rampe.

    Le bruit donne les taches de la matière (couleurs moyennes et claires de la rampe) ; l'éclairage
    passe ensuite par des paliers constants, pour rester dans les tons de la palette.
    """
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    coord = arbre.nodes.new("ShaderNodeTexCoord")
    bruit = arbre.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 5.0
    bruit.inputs["Detail"].default_value = 4.0
    ramp_base = arbre.nodes.new("ShaderNodeValToRGB")
    el = ramp_base.color_ramp.elements
    n = len(PAL[rampe])
    el[0].position, el[0].color = 0.0, (*couleur_lin(rampe, 1), 1.0)
    for k in range(2, n):
        nouveau = el.new((k - 1) / (n - 2))
        nouveau.color = (*couleur_lin(rampe, k), 1.0)
    principled = arbre.nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Roughness"].default_value = 0.9
    lumiere = arbre.nodes.new("ShaderNodeShaderToRGB")
    paliers = arbre.nodes.new("ShaderNodeValToRGB")
    paliers.color_ramp.interpolation = "CONSTANT"
    pe = paliers.color_ramp.elements
    while len(pe) > 1:
        pe.remove(pe[-1])
    seuils = [0.0, 0.12, 0.28, 0.45]
    tons = [1, 2, 3, n - 1]
    for k, (pos, idx) in enumerate(zip(seuils, tons)):
        c = couleur_lin(rampe, idx)
        if k == 0:
            pe[0].position, pe[0].color = pos, (*c, 1.0)
        else:
            pe.new(pos).color = (*c, 1.0)
    emission = arbre.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    arbre.links.new(coord.outputs["Object"], bruit.inputs["Vector"])
    arbre.links.new(bruit.outputs["Fac"], ramp_base.inputs["Fac"])
    arbre.links.new(ramp_base.outputs["Color"], principled.inputs["Base Color"])
    arbre.links.new(principled.outputs["BSDF"], lumiere.inputs["Shader"])
    arbre.links.new(lumiere.outputs["Color"], paliers.inputs["Fac"])
    arbre.links.new(paliers.outputs["Color"], emission.inputs["Color"])
    arbre.links.new(emission.outputs["Emission"], sortie.inputs["Surface"])
    return m


def scene_vide():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def eclairer(scene):
    """Clef : soleil haut-gauche (4,2 W) ; contre-jour froid bas-droite (1,4 W) : réglages de STYLE.md."""
    def soleil(nom, travel, energie, teinte):
        l = bpy.data.lights.new(nom, "SUN")
        l.energy = energie
        l.color = teinte
        o = bpy.data.objects.new(nom, l)
        scene.collection.objects.link(o)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = Vector(travel).normalized().to_track_quat("-Z", "Z")
    soleil("clef", (3.0, 4.0, -5.0), 4.2, (1.0, 0.93, 0.80))
    soleil("contre_jour", (-3.0, -3.0, 1.0), 1.4, (0.60, 0.78, 1.0))


def camera(scene, echelle, centre=(0.0, 0.0, 0.0)):
    """Caméra orthographique de profil (regarde vers +Y depuis -Y). echelle = largeur du cadre en unités."""
    cam = bpy.data.cameras.new("Camera")
    cam.type = "ORTHO"
    cam.ortho_scale = echelle
    o = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(o)
    o.location = (centre[0], -10.0, centre[2])
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0.0, 1.0, 0.0)).normalized().to_track_quat("-Z", "Z")
    scene.camera = o
    return o


def reglages(scene, res, chemin=None, echantillons=32):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.eevee.taa_render_samples = echantillons
    if chemin:
        scene.render.filepath = chemin


def rendre(scene, chemin):
    """Supprime l'ancien fichier, rend, puis vérifie que le nouveau fichier existe."""
    if os.path.exists(chemin):
        os.remove(chemin)
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(chemin):
        raise RuntimeError("rendu absent : " + chemin)
    print("RENDU", os.path.basename(chemin), os.path.getsize(chemin), "octets", flush=True)


def rendre_plan(scene, dossier, plan, apercu=None):
    """Rend une liste (numéro d'image Blender, nom du fichier sans extension) dans dossier.

    apercu : ensemble de numéros d'image à rendre seulement (essais rapides) ; None = tout.
    """
    os.makedirs(dossier, exist_ok=True)
    for frame, nom in plan:
        if apercu and frame not in apercu:
            continue
        scene.frame_set(frame)
        chemin = os.path.join(dossier, nom + ".png")
        scene.render.filepath = chemin
        rendre(scene, chemin)


def pivot(scene, nom, emplacement, parent_obj=None):
    """Objet vide servant de charnière : les pièces enfants tournent autour de lui."""
    o = bpy.data.objects.new(nom, None)
    o.location = emplacement
    scene.collection.objects.link(o)
    if parent_obj is not None:
        parent(o, parent_obj)
    return o


def oeil(centre, rayon, parent_obj, pupille=0.42, nom="oeil"):
    """Œil lisible à 64 px : blanc de la rampe metal + pupille noire posée côté caméra (y négatif).

    centre : point du globe, sur la surface visible (y négatif = côté caméra).
    pupille : rayon de la pupille en fraction du globe.
    """
    blanc = materiau(nom + "_blanc", "metal", bandes=(4, 5, 5, 5), rugosite=0.2)
    noir = materiau(nom + "_pupille", "caoutchouc", bandes=(0, 0, 0, 0), rugosite=0.3)
    globe = sphere(centre, rayon, blanc, nom=nom)
    point = sphere((centre[0], centre[1] - rayon * 0.55, centre[2]), rayon * pupille, noir, nom=nom + "_pupille")
    parent(globe, parent_obj)
    parent(point, parent_obj)
    return globe


def lisse(obj):
    bpy.ops.object.shade_smooth()
    return obj


def sphere(centre, rayon, mat, echelle=(1.0, 1.0, 1.0), nom=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=rayon, location=centre)
    o = bpy.context.active_object
    o.scale = echelle
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if nom:
        o.name = nom
    return o


def cylindre(centre, rayon, profondeur, mat, rotation=(0.0, 0.0, 0.0), nom=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=rayon, depth=profondeur, location=centre, rotation=rotation)
    o = bpy.context.active_object
    o.data.materials.append(mat)
    if nom:
        o.name = nom
    return o


def cube(centre, taille, mat, echelle=(1.0, 1.0, 1.0), nom=None):
    bpy.ops.mesh.primitive_cube_add(size=taille, location=centre)
    o = bpy.context.active_object
    o.scale = echelle
    o.data.materials.append(mat)
    if nom:
        o.name = nom
    return o


def tore(centre, grand_r, petit_r, mat, rotation=(0.0, 0.0, 0.0), nom=None):
    """Anneau (tore) : cerclage, bouée, bobine de cordage."""
    bpy.ops.mesh.primitive_torus_add(major_radius=grand_r, minor_radius=petit_r, location=centre, rotation=rotation)
    o = bpy.context.active_object
    o.data.materials.append(mat)
    if nom:
        o.name = nom
    return o


def cone(centre, rayon, hauteur, mat, rotation=(0.0, 0.0, 0.0), nom=None):
    bpy.ops.mesh.primitive_cone_add(radius1=rayon, radius2=0.0, depth=hauteur, location=centre, rotation=rotation)
    o = bpy.context.active_object
    o.data.materials.append(mat)
    if nom:
        o.name = nom
    return o


def parent(enfant, parent_obj):
    """Attache l'enfant en gardant sa position monde (le parent doit être à jour dans la vue)."""
    bpy.context.view_layer.update()
    enfant.parent = parent_obj
    enfant.matrix_parent_inverse = parent_obj.matrix_world.inverted()


def cle(obj, frame, rot=None, loc=None, echelle=None):
    """Pose une clé d'animation (rotation, position ou échelle) sur l'objet à l'image donnée."""
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if echelle is not None:
        obj.scale = echelle
        obj.keyframe_insert("scale", frame=frame)
