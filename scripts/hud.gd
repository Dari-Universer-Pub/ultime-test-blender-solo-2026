extends CanvasLayer
# Interface en texte : oxygène, emplacements 1 à 9, message, panneaux inventaire, fabrication et pause.
# Les noms viennent des données (Donnees.nom_objet) ; aucun pictogramme n'est dessiné ici.

var dernier_message := ""
var temps_message := 0.0
var jauge: ProgressBar
var barre_texte: Label
var message_texte: Label
var panneau_texte: Label


func _ready() -> void:
	layer = 10
	var racine := Control.new()
	racine.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	racine.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(racine)
	var air := Label.new()
	air.text = "Air"
	air.position = Vector2(8, 4)
	racine.add_child(air)
	jauge = ProgressBar.new()
	jauge.position = Vector2(40, 6)
	jauge.size = Vector2(180, 12)
	jauge.show_percentage = false
	var fond_jauge := StyleBoxFlat.new()          # fond sombre à bordure claire : la jauge se lit sur l'eau
	fond_jauge.bg_color = Color(0.03, 0.07, 0.12)
	fond_jauge.border_color = Color(0.6, 0.9, 0.95)
	fond_jauge.set_border_width_all(1)
	jauge.add_theme_stylebox_override("background", fond_jauge)
	var rempli_jauge := StyleBoxFlat.new()        # remplissage cyan : l'air se voit d'un coup d'œil
	rempli_jauge.bg_color = Color(0.35, 0.85, 0.9)
	jauge.add_theme_stylebox_override("fill", rempli_jauge)
	racine.add_child(jauge)
	var fond := ColorRect.new()                  # bandeau sombre sous les textes, lisible sur les tuiles
	fond.position = Vector2(0, 296)
	fond.size = Vector2(640, 64)
	fond.color = Color(0.02, 0.06, 0.12, 0.7)
	racine.add_child(fond)
	message_texte = Label.new()
	message_texte.position = Vector2(8, 22)
	message_texte.size = Vector2(624, 36)
	message_texte.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART   # le texte passe à la ligne au lieu d'être coupé
	message_texte.add_theme_font_size_override("font_size", 12)
	racine.add_child(message_texte)
	barre_texte = Label.new()
	barre_texte.position = Vector2(8, 300)
	barre_texte.size = Vector2(624, 56)
	barre_texte.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	barre_texte.add_theme_font_size_override("font_size", 12)
	racine.add_child(barre_texte)
	panneau_texte = Label.new()
	panneau_texte.position = Vector2(120, 60)
	panneau_texte.size = Vector2(400, 260)
	panneau_texte.visible = false
	racine.add_child(panneau_texte)


func message(texte: String) -> void:
	dernier_message = texte
	message_texte.text = texte
	temps_message = 4.0


func montrer(jeu: Node) -> void:
	jauge.max_value = jeu.plongeur.oxygene_max
	jauge.value = jeu.plongeur.oxygene
	var cases := []
	for i in jeu.barre.size():
		var item: String = jeu.barre[i]
		var nom := "—" if item == "" else "%s x%d" % [Donnees.nom_objet(item), int(jeu.inventaire.get(item, 0))]
		var marque := "[%d] " % (i + 1) if i != jeu.emplacement else "> %d " % (i + 1)
		cases.append(marque + nom)
	barre_texte.text = "   ".join(cases)
	if temps_message > 0.0:
		temps_message -= get_process_delta_time()
		if temps_message <= 0.0:
			message_texte.text = ""


func afficher_panneau(jeu: Node) -> void:
	panneau_texte.visible = jeu.panneau != ""
	if jeu.panneau == "inventaire":
		var lignes := ["INVENTAIRE (I pour fermer)"]
		for item in jeu.inventaire:
			lignes.append("%s : %d" % [Donnees.nom_objet(item), int(jeu.inventaire[item])])
		if jeu.inventaire.is_empty():
			lignes.append("(vide)")
		panneau_texte.text = "\n".join(lignes)
	elif jeu.panneau == "fabrication":
		var lignes := ["FABRICATION (haut/bas, Entrée pour fabriquer, C pour fermer)"]
		var liste: Array = jeu.recettes_disponibles()
		for k in liste.size():
			var r: Dictionary = liste[k]
			var ingr := []
			for g in r["ingredients"]:
				ingr.append("%s %d" % [Donnees.nom_objet(g["item"]), int(g["qte"])])
			var marque := ">" if k == jeu.choix else " "
			var etat := "" if jeu.peut_fabriquer(r) else "  (manque)"
			lignes.append("%s %s : %s%s" % [marque, Donnees.nom_objet(r["resultat"]), ", ".join(ingr), etat])
		panneau_texte.text = "\n".join(lignes)
	elif jeu.panneau == "pause":
		panneau_texte.text = "PAUSE\n\nÉchap : reprendre\nF5 : sauvegarder\nF9 : charger"
