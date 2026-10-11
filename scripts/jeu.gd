extends Node2D
const Monde := preload("res://scripts/monde.gd")
const Plongeur := preload("res://scripts/plongeur.gd")
const Hud := preload("res://scripts/hud.gd")
# Scène principale : assemble le monde, le plongeur, le radeau, la lumière et l'interface.
# Touches : définies ici (codes physiques, donc ZQSD sur AZERTY), à regrouper dans un fichier de config en M5.
# Argument --etat-robot=CHEMIN : écrit l'état du jeu dans ce fichier (lu par le robot de test).

const SAUVEGARDE := "user://sauvegarde.json"
const EMPLACEMENTS := 9
const STATION_DE_BASE := "etabli_radeau"
const POSITION_RADEAU := Vector2(0, -28)   # au-dessus du quai : le plongeur s'y pose en tombant

var monde: Monde
var plongeur: Plongeur
var hud: Hud
var modulation: CanvasModulate
var inventaire := {}                 # objet -> quantité
var barre: Array = []                # EMPLACEMENTS cases : identifiant d'objet ou ""
var emplacement := 0
var stations_installees: Array = []
var panneau := ""                    # "", "inventaire", "fabrication" ou "pause"
var choix := 0                       # recette sélectionnée dans le panneau fabrication
var chemin_etat := ""
var temps_etat := 0.0
var compte_poses := 0
var compte_creusages := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_position(Vector2i(0, 0))
	creer_controles()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--etat-robot="):
			chemin_etat = arg.trim_prefix("--etat-robot=")
	barre.resize(EMPLACEMENTS)
	barre.fill("")
	construire_scene()
	for depart in Donnees.depart["inventaire"]:
		ajouter(depart["item"], int(depart["qte"]))
	plongeur.global_position = POSITION_RADEAU
	hud.message("Vous êtes sur le radeau. Touches : ZQSD, Espace saut, E creuser, F poser, R ramasser, C fabriquer, F5 sauver.")


func creer_controles() -> void:
	var table := {
		"gauche": KEY_A, "droite": KEY_D, "haut": KEY_W, "bas": KEY_S, "saut": KEY_SPACE,
		"creuser": KEY_E, "poser": KEY_F, "ramasser": KEY_R, "attaque": KEY_X, "lampe": KEY_L,
		"inventaire": KEY_I, "fabriquer": KEY_C, "valider": KEY_ENTER, "pause": KEY_ESCAPE,
		"sauver": KEY_F5, "charger": KEY_F9,
	}
	for i in EMPLACEMENTS:
		table["emplacement_%d" % (i + 1)] = KEY_1 + i
	for nom in table:
		if not InputMap.has_action(nom):
			InputMap.add_action(nom)
		var ev := InputEventKey.new()
		ev.physical_keycode = table[nom]
		InputMap.action_add_event(nom, ev)


func construire_scene() -> void:
	# Ciel au-dessus de la surface (y < 0) et eau en dessous (y > 0), en espace monde.
	var ciel := ColorRect.new()
	ciel.position = Vector2(-600, -400)
	ciel.size = Vector2(1200, 400)
	ciel.color = Color8(118, 180, 200)
	add_child(ciel)
	var eau := ColorRect.new()
	eau.position = Vector2(-600, 0)
	eau.size = Vector2(1200, 1400)
	eau.material = materiau_eau()
	add_child(eau)
	monde = Monde.new()
	add_child(monde)
	var radeau := Sprite2D.new()
	radeau.texture = monde.texture("res://assets/objets/radeau.png")
	radeau.position = Vector2(0, -6)
	add_child(radeau)
	var quai := StaticBody2D.new()
	var forme := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(56, 4)
	forme.shape = rect
	forme.one_way_collision = true       # on monte dessous, on se pose dessus
	quai.position = Vector2(0, -12)
	quai.add_child(forme)
	add_child(quai)
	plongeur = Plongeur.new()
	plongeur.monde = monde
	plongeur.jeu = self
	plongeur.process_mode = Node.PROCESS_MODE_PAUSABLE
	plongeur.message.connect(func(t: String) -> void: hud.message(t))
	add_child(plongeur)
	var camera := Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 8.0
	plongeur.add_child(camera)
	camera.make_current()
	modulation = CanvasModulate.new()
	add_child(modulation)
	hud = Hud.new()
	add_child(hud)


# Fond d'eau : dégradé du haut clair vers le bas profond (tons de la rampe verre).
func materiau_eau() -> ShaderMaterial:
	var nuancier := Shader.new()
	nuancier.code = "shader_type canvas_item;\nuniform vec4 haut : source_color;\nuniform vec4 bas : source_color;\nuniform float profondeur_visible = 260.0;\nvoid fragment() {\n\tCOLOR = mix(haut, bas, clamp(UV.y * 1400.0 / profondeur_visible, 0.0, 1.0));\n}\n"
	var materiau := ShaderMaterial.new()
	materiau.shader = nuancier
	materiau.set_shader_parameter("haut", Color8(42, 138, 160))
	materiau.set_shader_parameter("bas", Color8(12, 42, 74))
	return materiau


func _process(delta: float) -> void:
	monde.actualiser_fenetre(_centre_de_chunk(plongeur.cellule()))
	modulation.color = Color(1, 1, 1).lerp(Color(0.45, 0.55, 0.78), clampf(plongeur.global_position.y / 200.0, 0.0, 1.0))
	if Input.is_action_just_pressed("pause"):
		basculer_panneau("pause")
	if Input.is_action_just_pressed("inventaire"):
		basculer_panneau("inventaire")
	if Input.is_action_just_pressed("fabriquer"):
		basculer_panneau("fabrication")
	if Input.is_action_just_pressed("sauver"):
		sauvegarder()
	if Input.is_action_just_pressed("charger"):
		charger()
	if panneau == "" or panneau == "fabrication":
		for i in EMPLACEMENTS:
			if Input.is_action_just_pressed("emplacement_%d" % (i + 1)):
				emplacement = i
	if panneau == "fabrication":
		_gerer_fabrication()
	elif panneau == "":
		if Input.is_action_just_pressed("poser"):
			plongeur.poser()
		if Input.is_action_just_pressed("ramasser"):
			plongeur.ramasser()
		if Input.is_action_just_pressed("lampe"):
			plongeur.lampe.enabled = not plongeur.lampe.enabled
			hud.message("Lampe %s." % ("allumée" if plongeur.lampe.enabled else "éteinte"))
		if Input.is_action_just_pressed("attaque"):
			hud.message("Rien à frapper ici pour l'instant.")
	hud.montrer(self)
	temps_etat += delta
	if chemin_etat != "" and temps_etat >= 0.2:
		temps_etat = 0.0
		ecrire_etat()


func _centre_de_chunk(c: Vector2i) -> Vector2i:
	return Vector2i(floori(c.x / 16.0) * 16 + 8, floori(c.y / 16.0) * 16 + 8)


func basculer_panneau(nom: String) -> void:
	if panneau == "pause" and nom != "pause":
		return
	panneau = "" if panneau == nom else nom
	get_tree().paused = panneau == "pause"
	plongeur.set_physics_process(panneau == "")
	if panneau == "fabrication":
		choix = 0
	hud.afficher_panneau(self)


func _gerer_fabrication() -> void:
	var liste := recettes_disponibles()
	if liste.is_empty():
		return
	if Input.is_action_just_pressed("haut"):
		choix = (choix - 1 + liste.size()) % liste.size()
	if Input.is_action_just_pressed("bas"):
		choix = (choix + 1) % liste.size()
	if Input.is_action_just_pressed("valider"):
		fabriquer(liste[choix])
	hud.afficher_panneau(self)


# ----------------------------------------------------------------- inventaire
func ajouter(item: String, n: int) -> void:
	inventaire[item] = int(inventaire.get(item, 0)) + n
	if not barre.has(item):
		var libre := barre.find("")
		if libre >= 0:
			barre[libre] = item


func possede(item: String, n: int = 1) -> bool:
	return int(inventaire.get(item, 0)) >= n


func retirer(item: String, n: int) -> bool:
	if not possede(item, n):
		return false
	inventaire[item] = int(inventaire[item]) - n
	if inventaire[item] <= 0:
		inventaire.erase(item)
		var i := barre.find(item)
		if i >= 0:
			barre[i] = ""
	return true


func oxygene_max() -> float:
	var maxi := 40.0
	for item in inventaire:
		maxi = maxf(maxi, Donnees.effet(item, "oxygene_max"))
	return maxi


func profondeur_max() -> float:
	var maxi := 40.0
	for item in inventaire:
		maxi = maxf(maxi, Donnees.effet(item, "profondeur_max"))
	return maxi


# ----------------------------------------------------------------- pose et stations
func utiliser_pour_poser(cible: Vector2i) -> void:
	var item: String = barre[emplacement]
	if item == "":
		hud.message("Aucun objet dans cet emplacement (touches 1 à 9).")
		return
	var tuile := monde.tuile_depuis_objet(item)
	if tuile != Monde.PAS_SOL:
		monde.poser_tuile(cible.x, cible.y, tuile)
		retirer(item, 1)
		compte_poses += 1
		hud.message("Posé : %s" % Donnees.nom_objet(item))
	elif Donnees.est_station_installable(item):
		var station: String = Donnees.items[item]["effets"]["station"]
		if station in stations_installees:
			hud.message("Ce module est déjà installé.")
			return
		stations_installees.append(station)
		retirer(item, 1)
		hud.message("Module installé : %s" % Donnees.stations[station]["nom"])
	else:
		hud.message("%s ne se pose pas." % Donnees.nom_objet(item))


func stations_disponibles() -> Array:
	return [STATION_DE_BASE] + stations_installees


func recettes_disponibles() -> Array:
	var stations := stations_disponibles()
	var liste := []
	for r in Donnees.recettes:
		if r["station"] in stations:
			liste.append(r)
	return liste


func peut_fabriquer(r: Dictionary) -> bool:
	for g in r["ingredients"]:
		if not possede(g["item"], int(g["qte"])):
			return false
	return true


func fabriquer(r: Dictionary) -> void:
	if not peut_fabriquer(r):
		hud.message("Il manque des ingrédients pour : %s" % Donnees.nom_objet(r["resultat"]))
		return
	for g in r["ingredients"]:
		retirer(g["item"], int(g["qte"]))
	ajouter(r["resultat"], int(r["quantite"]))
	hud.message("Fabriqué : %s" % Donnees.nom_objet(r["resultat"]))


# ----------------------------------------------------------------- sauvegarde
func sauvegarder() -> void:
	var donnees := {
		"version": 1,
		"position": [plongeur.global_position.x, plongeur.global_position.y],
		"oxygene": plongeur.oxygene,
		"inventaire": inventaire,
		"barre": barre,
		"emplacement": emplacement,
		"stations": stations_installees,
		"modifs": monde.modifs,
	}
	var f := FileAccess.open(SAUVEGARDE, FileAccess.WRITE)
	f.store_string(JSON.stringify(donnees))
	f.close()
	hud.message("Partie sauvegardée.")


func charger() -> void:
	if not FileAccess.file_exists(SAUVEGARDE):
		hud.message("Aucune sauvegarde à charger.")
		return
	var donnees: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SAUVEGARDE))
	inventaire = {}
	for k in donnees["inventaire"]:
		inventaire[k] = int(donnees["inventaire"][k])
	barre = donnees["barre"]
	emplacement = int(donnees["emplacement"])
	stations_installees = donnees["stations"]
	monde.modifs = {}
	for k in donnees["modifs"]:
		monde.modifs[k] = int(donnees["modifs"][k])
	monde.couche.clear()
	monde.centre_fenetre = Vector2i(999999, 999999)
	plongeur.global_position = Vector2(donnees["position"][0], donnees["position"][1])
	plongeur.velocity = Vector2.ZERO
	plongeur.oxygene = float(donnees["oxygene"])
	hud.message("Partie chargée.")


# ----------------------------------------------------------------- état pour le robot
func _objets_sol() -> Array:
	var liste := []
	for objet in monde.get_children():
		if objet.has_meta("item"):
			liste.append([objet.position.x, objet.position.y, objet.get_meta("item")])
	return liste



func ecrire_etat() -> void:
	var etat := {
		"pret": true,
		"position": [snappedf(plongeur.global_position.x, 0.1), snappedf(plongeur.global_position.y, 0.1)],
		"dans_eau": plongeur.dans_eau(),
		"sur_radeau": plongeur.is_on_floor() and plongeur.global_position.y < 0.0,
		"oxygene": snappedf(plongeur.oxygene, 0.1),
		"oxygene_max": oxygene_max(),
		"lampe": plongeur.lampe.enabled,
		"inventaire": inventaire,
		"barre": barre,
		"emplacement": emplacement,
		"stations": stations_installees,
		"panneau": panneau,
		"poses": compte_poses,
		"tuiles_modifiees": monde.modifs.size(),
		"message": hud.dernier_message,
		"fichier_sauvegarde": ProjectSettings.globalize_path(SAUVEGARDE),
		"objets_sol": _objets_sol(),
		"regarde": plongeur.direction,
		"case_visee": [plongeur.case_visee().x, plongeur.case_visee().y],
		"case_visee_solide": monde.est_solide(plongeur.case_visee().x, plongeur.case_visee().y),
	}
	var f := FileAccess.open(chemin_etat, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(etat))
		f.close()
