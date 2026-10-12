"""
decor_provisoire.py - décor PROVISOIRE de LES CLOCHES DE VAREKH (M2), construit dans Blender.
Ce script refait tout : six tuiles de terrain (cubes biseautés, matière bruitée, paliers de couleur
de la palette) et le radeau (planches et deux bidons). Il écrit des rendus :
    art/rendu/decor/<tuile>.png        128 px  (-> 16 px après pixelisation, facteur 8)
    art/rendu/decor_radeau/radeau.png  640 px  (-> 80 px après pixelisation, facteur 8)
Les images finales sont produites ensuite par tools/pixelisation/pixeliser.py (voir ETAT.md).
Lancement (depuis la racine du projet) :
    /opt/outils-varekh/bin/blender -b --factory-startup --python art/source/blender/decor_provisoire.py
Ces assets sont marqués PROVISOIRE dans art/manifest.json : ils seront remplacés par le décor final de M3.
"""
import json
import os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RENDU_TUILES = os.path.join(ROOT, "art", "rendu", "decor")
RENDU_RADEAU = os.path.join(ROOT, "art", "rendu", "decor_radeau")
RES_TUILE = 128
RES_RADEAU = 640
ECHANTILLONS = int(os.environ.get("DECOR_ECHANTILLONS", "32"))
PAL = json.load(open(os.path.join(ROOT, "art", "palette.json"), encoding="utf-8"))["rampes"]

TUILES = {            # nom du fichier : rampe de la palette et ton de base
    "roche": "roche", "recif": "recif", "cuivre": "cuivre", "sable": "sable", "bois": "ocre", "tole": "metal",
}


def couleur_lin(rampe, i):
    h = PAL[rampe][i].lstrip("#")
    srgb = [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def materiau_matiere(nom, rampe):
    """Matière : bruit (taches de la matière) -> couleur de base ; éclairage -> paliers de la rampe."""
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
    # couleur de base : tons moyens et clairs (le ton le plus sombre reste pour les creux seulement)
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


def materiau_simple(nom, rampe, i):
    """Couleur unie en paliers (bidons, planches de métal) : même traitement que les matières."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    arbre = m.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    principled = arbre.nodes.new("ShaderNodeBsdfPrincipled")
    c = couleur_lin(rampe, i)
    principled.inputs["Base Color"].default_value = (*c, 1.0)
    principled.inputs["Roughness"].default_value = 0.5
    lumiere = arbre.nodes.new("ShaderNodeShaderToRGB")
    paliers = arbre.nodes.new("ShaderNodeValToRGB")
    paliers.color_ramp.interpolation = "CONSTANT"
    pe = paliers.color_ramp.elements
    while len(pe) > 1:
        pe.remove(pe[-1])
    pe[0].position = 0.0
    pe[0].color = (*couleur_lin(rampe, max(0, i - 1)), 1.0)
    pe.new(0.15).color = (*c, 1.0)
    pe.new(0.35).color = (*couleur_lin(rampe, min(len(PAL[rampe]) - 1, i + 1)), 1.0)
    pe.new(0.6).color = (*couleur_lin(rampe, min(len(PAL[rampe]) - 1, i + 2)), 1.0)
    emission = arbre.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    arbre.links.new(principled.outputs["BSDF"], lumiere.inputs["Shader"])
    arbre.links.new(lumiere.outputs["Color"], paliers.inputs["Fac"])
    arbre.links.new(paliers.outputs["Color"], emission.inputs["Color"])
    arbre.links.new(emission.outputs["Emission"], sortie.inputs["Surface"])
    return m


def scene_vide():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def eclairer(scene):
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


def camera(scene, echelle):
    cam = bpy.data.cameras.new("Camera")
    cam.type = "ORTHO"
    cam.ortho_scale = echelle
    o = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(o)
    o.location = (0.0, -10.0, 0.0)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0.0, 1.0, 0.0)).normalized().to_track_quat("-Z", "Z")
    scene.camera = o


def reglages(scene, res, chemin):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.eevee.taa_render_samples = ECHANTILLONS
    scene.render.filepath = chemin


def rendre(scene, chemin):
    if os.path.exists(chemin):
        os.remove(chemin)
    bpy.ops.render.render(write_still=True)
    print("RENDU", os.path.basename(chemin), os.path.getsize(chemin), "octets")


def tuile(nom, rampe):
    scene = scene_vide()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = nom
    bev = cube.modifiers.new("Biseau", "BEVEL")
    bev.width = 0.07
    bev.segments = 2
    cube.data.materials.append(materiau_matiere(nom, rampe))
    eclairer(scene)
    camera(scene, 1.25)
    reglages(scene, RES_TUILE, os.path.join(RENDU_TUILES, nom + ".png"))
    rendre(scene, os.path.join(RENDU_TUILES, nom + ".png"))


def radeau():
    scene = scene_vide()
    bois = materiau_simple("planche", "ocre", 3)
    flotteur = materiau_simple("bidon", "combinaison", 4)
    metal = materiau_simple("ferrure", "metal", 2)
    # planches : cinq planches horizontales, bord arrondi
    for k in range(5):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.12 + k * 0.1))
        p = bpy.context.active_object
        p.scale = (3.4, 0.5, 0.045)
        p.data.materials.append(bois)
    # deux bidons sous le radeau
    for x in (-1.2, 1.2):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.9, location=(x, 0.0, -0.45), rotation=(0.0, 1.5708, 0.0))
        c = bpy.context.active_object
        c.data.materials.append(flotteur)
    # montants de métal aux extrémités
    for x in (-1.6, 1.6):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.0, -0.1))
        m = bpy.context.active_object
        m.scale = (0.05, 0.42, 0.28)
        m.data.materials.append(metal)
    eclairer(scene)
    camera(scene, 4.2)
    reglages(scene, RES_RADEAU, os.path.join(RENDU_RADEAU, "radeau.png"))
    rendre(scene, os.path.join(RENDU_RADEAU, "radeau.png"))


def main():
    os.makedirs(RENDU_TUILES, exist_ok=True)
    os.makedirs(RENDU_RADEAU, exist_ok=True)
    for nom, rampe in TUILES.items():
        tuile(nom, rampe)
    radeau()


main()
