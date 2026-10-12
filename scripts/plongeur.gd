extends CharacterBody2D
const Monde := preload("res://scripts/monde.gd")
# Le plongeur : nage, saut, oxygène, creusage, pose, ramassage. Le corps est celui de M0 (feuille Aseprite).

signal message(texte: String)

const VITESSE_NAGE := 95.0
const VITESSE_AIR := 80.0
const GRAVITE := 420.0
const IMPULSION_SAUT := -190.0
const IMPULSION_EAU := 160.0        # bond depuis l'eau (hauteur ≈ 30 px hors de l'eau)
const RECUPERATION_AIR := 20.0       # oxygène rendu par seconde hors de l'eau
const PORTEE_RAMASSAGE := 28.0
const FEUILLE := "res://assets/sprites/plongeur/plongeur.png"
const DONNEES := "res://assets/sprites/plongeur/plongeur.json"

var monde: Monde
var jeu: Node                          # Jeu : inventaire, barre, stations
var direction := 1                     # 1 : regarde à droite, -1 : à gauche
var oxygene := 40.0
var oxygene_max := 40.0
var creusage_cible := Vector2i(999999, 999999)
var creusage_temps := 0.0
var bond_restant := 0.0
var anim: AnimatedSprite2D
var attaque_restante := 0.0      # durée restante du geste d'attaque (l'animation ne doit pas être écrasée)
var lampe: PointLight2D


func _ready() -> void:
	var forme := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(10, 20)
	forme.shape = rect
	add_child(forme)
	anim = AnimatedSprite2D.new()
	anim.sprite_frames = construire_images()
	anim.play("nage")
	add_child(anim)
	lampe = PointLight2D.new()
	lampe.texture = halo()
	lampe.texture_scale = 3.0
	lampe.energy = 1.1
	lampe.color = Color(1.0, 0.92, 0.7)
	lampe.enabled = false
	add_child(lampe)


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


# Halo de lumière : dégradé radial de Godot (éclairage, pas un asset dessiné).
func halo() -> GradientTexture2D:
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = degrade
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 128
	tex.height = 128
	return tex


func dans_eau() -> bool:
	return global_position.y > 0.0


func cellule() -> Vector2i:
	return Vector2i(floori(global_position.x / Monde.TAILLE), floori(global_position.y / Monde.TAILLE))


func _physics_process(delta: float) -> void:
	var axe_x := Input.get_axis("gauche", "droite")
	var axe_y := Input.get_axis("haut", "bas")
	if axe_x != 0.0:
		direction = int(signf(axe_x))
	if dans_eau():
		velocity = velocity.lerp(Vector2(axe_x, axe_y) * VITESSE_NAGE, clampf(9.0 * delta, 0.0, 1.0))   # eau : arrêt rapide
		if Input.is_action_just_pressed("saut") and global_position.y < 24.0:
			bond_restant = 0.25                 # bond près de la surface : la poussée tient jusqu'à l'air
		if bond_restant > 0.0:
			bond_restant -= delta
			velocity.y = -IMPULSION_EAU
		elif Input.is_action_pressed("saut"):
			velocity.y = -VITESSE_NAGE          # nage vers la surface
	else:
		velocity.x = move_toward(velocity.x, axe_x * VITESSE_AIR, 900.0 * delta)
		velocity.y += GRAVITE * delta
		if is_on_floor() and Input.is_action_just_pressed("saut"):
			velocity.y = IMPULSION_SAUT
	move_and_slide()
	anim.flip_h = direction < 0
	if attaque_restante > 0.0:
		attaque_restante -= delta
	else:
		anim.animation = "nage" if dans_eau() else "idle"
	_oxygene(delta)
	_creuser(delta)


# ----------------------------------------------------------------- oxygène
func _oxygene(delta: float) -> void:
	oxygene_max = jeu.oxygene_max()
	if dans_eau():
		var facteur := 1.0 if global_position.y <= jeu.profondeur_max() else 2.0
		oxygene -= delta * facteur
	else:
		oxygene = minf(oxygene_max, oxygene + RECUPERATION_AIR * delta)
	if oxygene <= 0.0:
		oxygene = oxygene_max
		global_position = Vector2(0, -30)
		velocity = Vector2.ZERO
		message.emit("Plus d'air : le plongeur est remonté au radeau.")


# ----------------------------------------------------------------- creusage et pose
func case_visee() -> Vector2i:
	var c := cellule()
	if Input.is_action_pressed("bas") and not Input.is_action_pressed("gauche") and not Input.is_action_pressed("droite"):
		return c + Vector2i(0, 1)
	return c + Vector2i(direction, 0)


func _creuser(delta: float) -> void:
	if not Input.is_action_pressed("creuser"):
		creusage_temps = 0.0
		creusage_cible = Vector2i(999999, 999999)
		return
	var cible := case_visee()
	if not monde.est_solide(cible.x, cible.y):
		return
	if cible != creusage_cible:
		creusage_cible = cible
		creusage_temps = 0.0
	creusage_temps += delta
	var t := monde.tuile(cible.x, cible.y)
	if creusage_temps >= monde.duree_creusage(t):
		monde.poser_tuile(cible.x, cible.y, Monde.PAS_SOL)
		jeu.jouer("creusage")
		var depot: String = monde.depot_creusage(t)
		if depot != "":
			monde.faire_tomber(Vector2(cible * Monde.TAILLE) + Vector2(8, 8), depot, t)
			message.emit("Creusé : %s" % Donnees.nom_objet(depot))
		creusage_temps = 0.0
		creusage_cible = Vector2i(999999, 999999)


func poser() -> void:
	var cible := case_visee()
	if monde.est_solide(cible.x, cible.y):
		message.emit("Il faut une case vide pour poser.")
		return
	jeu.utiliser_pour_poser(cible)


func ramasser() -> void:
	for objet in monde.get_children():
		if objet.has_meta("item") and objet.position.distance_to(global_position) <= PORTEE_RAMASSAGE:
			jeu.ajouter(objet.get_meta("item"), 1)
			message.emit("Ramassé : %s" % Donnees.nom_objet(objet.get_meta("item")))
			objet.queue_free()
			return
	message.emit("Rien à ramasser ici.")


# Geste d'attaque (touche X) : l'animation « attaque » joue, puis le plongeur reprend la nage.
func attaquer() -> void:
	if anim == null or not anim.sprite_frames.has_animation("attaque"):
		return
	anim.play("attaque")
	attaque_restante = 0.5

