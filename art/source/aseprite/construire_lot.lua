-- construire_lot.lua (M3) : assemble des images pixelisées (un dossier, une liste de fichiers dans l'ordre)
-- en un fichier .aseprite, avec des étiquettes optionnelles, puis exporte la feuille horizontale et le JSON.
-- Paramètres :
--   entree      dossier des PNG
--   fichiers    noms des PNG séparés par des virgules, dans l'ordre des images
--   etiquettes  "nom:debut:fin,..." (numéros d'images à partir de 1) ; vide = aucune étiquette
--   sortie      fichier .aseprite à écrire ; feuille et donnees : sorties PNG et JSON
-- Lancement : aseprite --batch --script-param entree=... --script-param fichiers=... --script art/source/aseprite/construire_lot.lua
local entree = app.params["entree"]
local fichiers = app.params["fichiers"]
local etiquettes = app.params["etiquettes"] or ""
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]

local liste = {}
for nom in string.gmatch(fichiers, "[^,]+") do
  table.insert(liste, entree .. "/" .. nom)
end
assert(#liste > 0, "aucun fichier dans 'fichiers'")

local premiere = Image{ fromFile = liste[1] }
local spr = Sprite(premiere.width, premiere.height, ColorMode.RGB)
local couche = spr.layers[1]
couche.name = "lot"
for i, chemin in ipairs(liste) do
  local im = Image{ fromFile = chemin }
  if i > 1 then spr:newFrame() end
  local cel = couche:cel(i)
  if cel then
    cel.image = im
  else
    spr:newCel(couche, i, im, Point(0, 0))
  end
end
for etiquette in string.gmatch(etiquettes, "[^,]+") do
  local nom, debut, fin = string.match(etiquette, "([^:]+):(%d+):(%d+)")
  local t = spr:newTag(tonumber(debut), tonumber(fin))
  t.name = nom
end
spr:saveAs(sortie)
app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = feuille, dataFilename = donnees,
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("LOT_OK " .. #liste .. " images")
