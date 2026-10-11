extends Node2D
# M0 : scene minimale. Le plongeur (feuille Aseprite) nage et flotte dans l'eau.
# Les images viennent du JSON Aseprite : une etiquette = une animation (nage, idle).
# Capture par Godot : godot --path . -- --capture=shots/m0_plongeur_godot.png

const FEUILLE := "res://assets/sprites/plongeur/plongeur.png"
const DONNEES := "res://assets/sprites/plongeur/plongeur.json"
const ECHELLE := 4
const IMAGES_AVANT_CAPTURE := 30

var anim: AnimatedSprite2D
var chemin_capture := ""
var images_affichees := 0


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			chemin_capture = arg.trim_prefix("--capture=")
	var eau := ColorRect.new()
	eau.size = Vector2(640, 360)
	eau.material = materiau_eau()
	add_child(eau)
	anim = AnimatedSprite2D.new()
	anim.sprite_frames = construire_images()
	anim.position = Vector2(320, 180)
	anim.scale = Vector2(ECHELLE, ECHELLE)
	add_child(anim)
	anim.play("nage")


# Eau : degrade vertical entre deux tons de la rampe "verre" de art/palette.json (du haut, clair, au bas, profond).
func materiau_eau() -> ShaderMaterial:
	var nuancier := Shader.new()
	nuancier.code = "shader_type canvas_item;\nuniform vec4 haut : source_color;\nuniform vec4 bas : source_color;\nvoid fragment() {\n\tCOLOR = mix(haut, bas, SCREEN_UV.y);\n}\n"
	var materiau := ShaderMaterial.new()
	materiau.shader = nuancier
	materiau.set_shader_parameter("haut", Color8(42, 138, 160))
	materiau.set_shader_parameter("bas", Color8(12, 42, 74))
	return materiau


func construire_images() -> SpriteFrames:
	var feuille := load(FEUILLE) as Texture2D
	var donnees: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DONNEES))
	var cadres: Array = donnees["frames"]
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	for etiquette in donnees["meta"]["frameTags"]:
		var nom: String = etiquette["name"]
		sf.add_animation(nom)
		sf.set_animation_speed(nom, 12.0)
		sf.set_animation_loop(nom, true)
		for i in range(int(etiquette["from"]), int(etiquette["to"]) + 1):
			var r: Dictionary = cadres[i]["frame"]
			var image := AtlasTexture.new()
			image.atlas = feuille
			image.region = Rect2(r["x"], r["y"], r["w"], r["h"])
			sf.add_frame(nom, image)
	return sf


func _process(_delta: float) -> void:
	if chemin_capture == "" or DisplayServer.get_name() == "headless":
		return
	images_affichees += 1
	if images_affichees == IMAGES_AVANT_CAPTURE:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(chemin_capture)
		print("CAPTURE_OK ", chemin_capture)
		get_tree().quit()
