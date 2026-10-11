extends Node2D
# Le monde en tuiles. La génération est déterministe (bruit à graine fixe) ; seules les tuiles
# modifiées par le joueur sont stockées (dictionnaire "x,y" -> tuile), donc sauvegardées à part.

const TAILLE := 16                       # pixels par tuile (rendu provisoire de M2)
const FENETRE := Vector2i(48, 32)        # tuiles rendues autour du joueur
const FOND_Y := 26                       # fond de mer : rangée de sable à 26 m
const PAS_SOL := -1                      # eau ou vide : pas de tuile
enum { ROCHE, RECIF, CUIVRE, SABLE, BOIS, TOLE }    # numéros = ordre de data/tuiles.json

var bruit := FastNoiseLite.new()
var modifs := {}                         # "x,y" -> tuile (ROCHE..TOLE) ou PAS_SOL si creusée
var couche: TileMapLayer
var centre_fenetre := Vector2i(999999, 999999)
var textures := {}                       # nom -> Texture2D, chargées au besoin


func _ready() -> void:
	bruit.seed = 4242
	bruit.frequency = 0.045
	bruit.noise_type = FastNoiseLite.TYPE_SIMPLEX
	couche = TileMapLayer.new()
	couche.tile_set = construire_tileset()
	add_child(couche)


# ----------------------------------------------------------------- génération
# Données de tuiles lues dans data/tuiles.json (durée de creusage, objet rendu, objet posé).
func nom_tuile(t: int) -> String:
	return Donnees.tuiles[t]["id"]


func duree_creusage(t: int) -> float:
	return float(Donnees.tuiles[t]["creusage_s"])


func depot_creusage(t: int) -> String:
	return Donnees.tuiles[t]["depot"]


func tuile_depuis_objet(item_id: String) -> int:
	for k in Donnees.tuiles.size():
		if Donnees.tuiles[k]["pose_depuis"] == item_id and item_id != "":
			return k
	return PAS_SOL


func tuile_de_base(x: int, y: int) -> int:
	var epave := _epave(x, y)
	if epave != PAS_SOL:
		return epave
	if y < FOND_Y:
		return PAS_SOL
	if y == FOND_Y:
		return SABLE
	var m := bruit.get_noise_2d(x, y)
	if m < 0.12:
		return PAS_SOL
	if m > 0.62:
		return CUIVRE
	if y < 120:
		return RECIF if m > 0.40 else SABLE
	return ROCHE


# Une épave fixe, posée sur le fond, à l'ouest du radeau : c'est le premier endroit à creuser.
# Planches (rangée 18 et 19) et colonne de tôle (x = -16 à -14, y = 20 à 25).
func _epave(x: int, y: int) -> int:
	if x < -34 or x > -14 or y < 18 or y > 25:
		return PAS_SOL
	if y == 18 or y == 19:
		return BOIS
	if x >= -16 and x <= -14:
		return TOLE
	return PAS_SOL


func tuile(x: int, y: int) -> int:
	var cle := "%d,%d" % [x, y]
	if modifs.has(cle):
		return modifs[cle]
	return tuile_de_base(x, y)


func est_solide(x: int, y: int) -> bool:
	return tuile(x, y) != PAS_SOL


func poser_tuile(x: int, y: int, t: int) -> void:
	modifs["%d,%d" % [x, y]] = t
	_maj_cellule(Vector2i(x, y))


# ----------------------------------------------------------------- affichage par fenêtre
func actualiser_fenetre(centre: Vector2i) -> void:
	if centre == centre_fenetre:
		return
	centre_fenetre = centre
	couche.clear()
	for y in range(centre.y - FENETRE.y / 2, centre.y + FENETRE.y / 2):
		for x in range(centre.x - FENETRE.x / 2, centre.x + FENETRE.x / 2):
			_maj_cellule(Vector2i(x, y))


func _maj_cellule(pos: Vector2i) -> void:
	if abs(pos.x - centre_fenetre.x) > FENETRE.x / 2 or abs(pos.y - centre_fenetre.y) > FENETRE.y / 2:
		return
	var t := tuile(pos.x, pos.y)
	if t == PAS_SOL:
		couche.erase_cell(pos)
	else:
		couche.set_cell(pos, 0, Vector2i(t, 0))


func construire_tileset() -> TileSet:
	var atlas := Image.create(TAILLE * Donnees.tuiles.size(), TAILLE, false, Image.FORMAT_RGBA8)
	atlas.fill(Color(0, 0, 0, 0))
	for i in Donnees.tuiles.size():
		var img := (load("res://assets/tuiles/%s.png" % nom_tuile(i)) as Texture2D).get_image()
		img.convert(Image.FORMAT_RGBA8)
		atlas.blit_rect(img, Rect2i(0, 0, TAILLE, TAILLE), Vector2i(i * TAILLE, 0))
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TAILLE, TAILLE)
	ts.add_physics_layer()
	var source := TileSetAtlasSource.new()
	source.texture = ImageTexture.create_from_image(atlas)
	source.texture_region_size = Vector2i(TAILLE, TAILLE)
	ts.add_source(source, 0)
	var carre := PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)])
	for i in Donnees.tuiles.size():
		source.create_tile(Vector2i(i, 0))
		var donnees := source.get_tile_data(Vector2i(i, 0), 0)
		donnees.add_collision_polygon(0)
		donnees.set_collision_polygon_points(0, 0, carre)
	return ts


# ----------------------------------------------------------------- objets au sol
func texture(nom: String) -> Texture2D:
	if not textures.has(nom):
		textures[nom] = load(nom)          # image importée par Godot : elle suit l'export (PCK) et le clone
	return textures[nom]


func faire_tomber(pos: Vector2, item_id: String, t: int) -> Node2D:
	var objet := Node2D.new()
	objet.position = pos
	objet.set_meta("item", item_id)
	var image := Sprite2D.new()
	image.texture = texture("res://assets/tuiles/%s.png" % nom_tuile(t))
	image.scale = Vector2(0.6, 0.6)
	objet.add_child(image)
	add_child(objet)
	return objet
