extends Node2D
# Créature vivante du biome : nage en va-et-vient, avertit quand le plongeur s'approche (défensive),
# encaisse les coups du plongeur, puis meurt. Ses images viennent de la feuille Aseprite construite dans Blender.

const SHEET := "res://assets/sprites/%s/%s.png"
const DONNEES := "res://assets/sprites/%s/%s.json"
const VITESSE := 14.0
const AMPLITUDE := 40.0      # distance de nage de part et d'autre du point de départ (px)
const PORTEE_ATTAQUE := 26.0 # distance à partir de laquelle le plongeur peut frapper (px)
const VIE_MAX := 3

var id_creature := ""
var defensive := false
var vie := VIE_MAX
var anim: AnimatedSprite2D
var sens := 1.0
var depart := Vector2.ZERO
var morte := false
var temps := 0.0
var temps_avertissement := 0.0


func setup(id: String, position: Vector2, danger: String) -> void:
	id_creature = id
	global_position = position
	depart = position
	defensive = danger == "defensif"
	anim = AnimatedSprite2D.new()
	anim.sprite_frames = construire_images(id)
	anim.play("nage")
	add_child(anim)
	sens = 1.0 if randf() < 0.5 else -1.0
	anim.flip_h = sens < 0.0
	temps = randf() * 10.0


func construire_images(id: String) -> SpriteFrames:
	var feuille := load(SHEET % [id, id]) as Texture2D
	var donnees: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DONNEES % [id, id]))
	var cadres: Array = donnees["frames"]
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	for etiquette in donnees["meta"]["frameTags"]:
		var nom: String = etiquette["name"]
		sf.add_animation(nom)
		sf.set_animation_speed(nom, 10.0)
		sf.set_animation_loop(nom, nom != "mort")   # la mort s'arrête sur la dernière image
		for i in range(int(etiquette["from"]), int(etiquette["to"]) + 1):
			var r: Dictionary = cadres[i]["frame"]
			var image := AtlasTexture.new()
			image.atlas = feuille
			image.region = Rect2(r["x"], r["y"], r["w"], r["h"])
			sf.add_frame(nom, image)
	return sf


func _process(delta: float) -> void:
	if morte:
		return
	temps += delta
	if temps_avertissement > 0.0:
		temps_avertissement -= delta
		if temps_avertissement <= 0.0 and anim.animation == "attaque":
			anim.play("nage")
		return
	global_position.x += sens * VITESSE * delta
	global_position.y = depart.y + sin(temps * 1.3) * 2.0
	if absf(global_position.x - depart.x) > AMPLITUDE:
		sens = -sens
		anim.flip_h = sens < 0.0


# Avertissement d'une créature défensive : elle se dresse, sans frapper (le plongeur ne reçoit pas de dégâts).
func avertir() -> void:
	if morte or not defensive or temps_avertissement > 0.0:
		return
	anim.play("attaque")
	temps_avertissement = 0.6


func encaisser(degats: int) -> void:
	if morte:
		return
	vie -= degats
	if vie <= 0:
		morte = true
		anim.play("mort")
		get_tree().create_timer(2.0).timeout.connect(queue_free)
	else:
		anim.modulation = Color(1.0, 0.6, 0.6)
		get_tree().create_timer(0.15).timeout.connect(func(): anim.modulation = Color(1, 1, 1))


func est_a_portee(pos: Vector2) -> bool:
	return not morte and global_position.distance_to(pos) <= PORTEE_ATTAQUE
