extends Node
# Donnees : lit les fichiers data/*.json (autoload "Donnees"). Aucun objet, recette, station ni biome
# n'est code en dur dans le jeu : tout vient d'ici.

const FICHIERS := {
	"items": "res://data/items.json",
	"recettes": "res://data/recipes.json",
	"stations": "res://data/stations.json",
	"biomes": "res://data/biomes.json",
	"depart": "res://data/depart.json",
	"tuiles": "res://data/tuiles.json",
}

var items := {}          # id -> dictionnaire d'objet
var recettes: Array = []
var stations := {}       # id -> dictionnaire de station
var biomes: Array = []
var depart := {}
var tuiles: Array = []   # une entrée par tuile, dans l'ordre de l'atlas (index = numéro de tuile)


func _ready() -> void:
	items = {}
	for objet in lire(FICHIERS["items"])["items"]:
		items[objet["id"]] = objet
	recettes = lire(FICHIERS["recettes"])["recipes"]
	stations = {}
	for s in lire(FICHIERS["stations"])["stations"]:
		stations[s["id"]] = s
	biomes = lire(FICHIERS["biomes"])["biomes"]
	depart = lire(FICHIERS["depart"])
	tuiles = lire(FICHIERS["tuiles"])["tuiles"]


func lire(chemin: String) -> Dictionary:
	var texte := FileAccess.get_file_as_string(chemin)
	var donnees = JSON.parse_string(texte)
	if donnees == null:
		push_error("JSON illisible : " + chemin)
		return {}
	return donnees


func nom_objet(id: String) -> String:
	if items.has(id):
		return items[id]["nom"]
	return id


func biome_pour_profondeur(profondeur: float) -> Dictionary:
	for b in biomes:
		if profondeur >= float(b["profondeur_min"]) and profondeur < float(b["profondeur_max"]):
			return b
	return biomes[biomes.size() - 1]


func effet(id: String, cle: String) -> float:
	if items.has(id) and items[id].has("effets") and items[id]["effets"].has(cle):
		return float(items[id]["effets"][cle])
	return 0.0


func est_station_installable(id: String) -> bool:
	return items.has(id) and items[id].get("effets", {}).has("station")
