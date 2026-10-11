-- finition_plongeur.lua (M0) : retouches manuelles du plongeur, une liste par iteration.
-- Chaque retouche est un pixel ou un groupe de pixels (x, y, couleur hex ou "" pour effacer).
-- Ouvre le .aseprite, applique les retouches de la liste ITERATION, sauve, exporte la feuille et le JSON.
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]
local iteration = app.params["iteration"] or "0"

-- Retouches : { image_index (base 1), x, y, "#rrggbb" ou "" }
local RETOUCHES = {
  ["1"] = {
    -- Iteration 1 : reflet blanc (#e6fff8) sur le haut du hublot, et second reflet (#9af0ea) dessous.
    {1, 43, 37, "#e6fff8"},
    {2, 47, 36, "#e6fff8"},
    {3, 48, 34, "#e6fff8"},
    {4, 50, 31, "#e6fff8"},
    {5, 49, 30, "#e6fff8"},
    {6, 48, 31, "#e6fff8"},
    {7, 48, 33, "#e6fff8"},
    {8, 48, 35, "#e6fff8"},
    {9, 37, 16, "#e6fff8"},
    {9, 37, 17, "#9af0ea"},
    {10, 37, 16, "#e6fff8"},
    {11, 37, 16, "#e6fff8"},
    {11, 37, 17, "#9af0ea"},
    {12, 36, 16, "#e6fff8"},
    {12, 36, 17, "#9af0ea"},
    {13, 36, 16, "#e6fff8"},
    {13, 36, 17, "#9af0ea"},
    {14, 36, 16, "#e6fff8"},
    {14, 36, 17, "#9af0ea"},
  },
  ["2"] = {
    -- Iteration 2 : pixels de lampe voisins du sommet passent du jaune #f8c850 au blanc chaud #fff2a8.
    {1, 51, 40, "#fff2a8"},
    {2, 52, 39, "#fff2a8"},
    {4, 52, 34, "#fff2a8"},
    {4, 53, 33, "#fff2a8"},
    {6, 52, 33, "#fff2a8"},
  },
  ["3"] = {
    -- Iteration 3 : reflet clair (#c8ecbc) sur le bord superieur de la bouteille, ton 4 #8ac8a0 remplace par le ton 5.
    {2, 51, 38, "#c8ecbc"},
    {5, 52, 31, "#c8ecbc"},
    {10, 39, 15, "#c8ecbc"},
    {14, 37, 14, "#c8ecbc"},
  },
}

-- Remplacements de couleur globaux (vide : plus de brun a remplacer depuis la palette sans ocre)
local REMAP = {}

local spr = app.open(sortie)
local couche = spr.layers[1]
for _, r in ipairs(RETOUCHES[iteration] or {}) do
  local cel = couche:cel(r[1])
  if cel then
    local im = cel.image
    local c = Color{ r = 0, g = 0, b = 0, a = 0 }
    if r[4] ~= "" then
      local h = r[4]:gsub("#", "")
      c = Color{ r = tonumber(h:sub(1, 2), 16), g = tonumber(h:sub(3, 4), 16),
                 b = tonumber(h:sub(5, 6), 16), a = 255 }
    end
    im:putPixel(r[2], r[3], c)
  end
end
for i = 1, #spr.frames do
  local cel = couche:cel(i)
  local table_remap = REMAP[iteration]
  if cel and table_remap then
    local im = cel.image
    for y = 0, im.height - 1 do
      for x = 0, im.width - 1 do
        local p = im:getPixel(x, y)
        if app.pixelColor.rgbaA(p) > 0 then
          local cle = string.format("#%02x%02x%02x", app.pixelColor.rgbaR(p), app.pixelColor.rgbaG(p), app.pixelColor.rgbaB(p))
          local cible = table_remap[cle]
          if cible then
            local h = cible:gsub("#", "")
            im:putPixel(x, y, Color{ r = tonumber(h:sub(1, 2), 16), g = tonumber(h:sub(3, 4), 16),
                                     b = tonumber(h:sub(5, 6), 16), a = 255 })
          end
        end
      end
    end
  end
end
spr:saveAs(sortie)
app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = feuille, dataFilename = donnees,
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("FINITION_OK iteration " .. iteration)
