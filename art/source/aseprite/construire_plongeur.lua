-- construire_plongeur.lua (M0) : assemble les 14 images pixelisees du plongeur en un fichier .aseprite,
-- avec les etiquettes "nage" (images 1 a 8) et "idle" (images 9 a 14), puis exporte la feuille et le JSON.
-- Lancement : aseprite --batch --script-param entree=... --script-param sortie=... \
--             --script-param feuille=... --script-param donnees=... --script art/source/aseprite/construire_plongeur.lua
local entree = app.params["entree"]
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]

local ordre = {}
for i = 1, 8 do table.insert(ordre, string.format("%s/nage_%02d.png", entree, i)) end
for i = 1, 6 do table.insert(ordre, string.format("%s/idle_%02d.png", entree, i)) end

local spr = Sprite(64, 64, ColorMode.RGB)
local couche = spr.layers[1]
couche.name = "plongeur"
for i, chemin in ipairs(ordre) do
  local im = Image{ fromFile = chemin }
  if i > 1 then spr:newFrame() end
  local cel = couche:cel(i)
  if cel then
    cel.image = im
  else
    spr:newCel(couche, i, im, Point(0, 0))
  end
end
local t1 = spr:newTag(1, 8)
t1.name = "nage"
local t2 = spr:newTag(9, 14)
t2.name = "idle"
spr:saveAs(sortie)

app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = feuille, dataFilename = donnees,
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("ASSEMBLAGE_OK " .. #ordre .. " images")
