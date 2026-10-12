-- construire_plongeur.lua (M0) : assemble les 14 images pixelisees du plongeur en un fichier .aseprite,
-- avec les etiquettes "nage" (images 1 a 8) et "idle" (images 9 a 14), puis exporte la feuille et le JSON.
-- Lancement : aseprite --batch --script-param entree=... --script-param sortie=... \
--             --script-param feuille=... --script-param donnees=... --script art/source/aseprite/construire_plongeur.lua
local entree = app.params["entree"]
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]

-- Ordre des images et étiquettes (M3) : nage 8, idle 6, puis creusage 6, attaque 6, saut 4, dégâts 3, mort 8.
local ETIQUETTES = { {"nage", 8}, {"idle", 6}, {"creusage", 6}, {"attaque", 6}, {"saut", 4}, {"degats", 3}, {"mort", 8} }
local ordre = {}
local etiquettes = {}
for _, e in ipairs(ETIQUETTES) do
  local debut = #ordre + 1
  for i = 1, e[2] do table.insert(ordre, string.format("%s/%s_%02d.png", entree, e[1], i)) end
  table.insert(etiquettes, { nom = e[1], debut = debut, fin = #ordre })
end

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
for _, e in ipairs(etiquettes) do
  local t = spr:newTag(e.debut, e.fin)
  t.name = e.nom
end
spr:saveAs(sortie)

app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = feuille, dataFilename = donnees,
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("ASSEMBLAGE_OK " .. #ordre .. " images")
