-- finition_creature.lua (M3) : itérations Aseprite d'une créature (poisson, carangue, oursin, tortue).
-- Une itération = une liste de RECOLORATIONS LIMITÉES À UNE ZONE : dans le rectangle {x0,y0,x1,y1} de
-- chaque image, chaque pixel de la couleur « de » devient la couleur « vers ». Aucun pixel n'est dessiné
-- de zéro : on ne change que des pixels déjà présents, comme un pinceau de sélection dans Aseprite.
-- Les retouches de chaque créature sont dans art/source/aseprite/retouches_<id>.lua (table RETOUCHES).
-- Paramètres : sortie (.aseprite, lu et réécrit), feuille, donnees (PNG et JSON exportés),
--              iteration (2, 3, 4), retouches (chemin du fichier .lua), images (dossier des PNG par cadre).
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]
local iteration = app.params["iteration"] or "2"
local fichier_retouches = app.params["retouches"]
local dossier_images = app.params["images"]

local RETOUCHES = dofile(fichier_retouches)
local zones = RETOUCHES[iteration] or {}

local function couleur(hex)
  local h = hex:gsub("#", "")
  return Color{ r = tonumber(h:sub(1, 2), 16), g = tonumber(h:sub(3, 4), 16),
                b = tonumber(h:sub(5, 6), 16), a = 255 }
end

local function hex_de(p)
  return string.format("#%02x%02x%02x", app.pixelColor.rgbaR(p), app.pixelColor.rgbaG(p), app.pixelColor.rgbaB(p))
end

local spr = app.open(sortie)
local couche = spr.layers[1]
local modifies = 0
for _, z in ipairs(zones) do
  local cible = couleur(z.vers)
  for i = 1, #spr.frames do
    local cel = couche:cel(i)
    if cel then
      local im = cel.image
      local x0, y0, x1, y1 = z.region[1], z.region[2], z.region[3], z.region[4]
      for y = y0, math.min(y1, im.height - 1) do
        for x = x0, math.min(x1, im.width - 1) do
          local p = im:getPixel(x, y)
          if app.pixelColor.rgbaA(p) > 0 and hex_de(p) == z.de then
            im:putPixel(x, y, cible)
            modifies = modifies + 1
          end
        end
      end
    end
  end
end
spr:saveAs(sortie)

-- une image par cadre, pour la planche de comparaison (lecture seule)
if dossier_images then
  local noms = RETOUCHES.noms or {}
  for i = 1, #spr.frames do
    local cel = couche:cel(i)
    if cel and noms[i] then
      cel.image:saveAs(dossier_images .. "/" .. noms[i] .. ".png")
    end
  end
end

app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = feuille, dataFilename = donnees,
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("FINITION_CREATURE_OK iteration " .. iteration .. " pixels " .. modifies)
