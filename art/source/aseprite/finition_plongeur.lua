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
    -- Iteration 1 : reflet blanc (#e6fff8) sur le haut du hublot, dans chaque image ou le hublot est visible.
    {1, 49, 37, "#e6fff8"},
    {2, 50, 37, "#e6fff8"},
    {3, 51, 36, "#e6fff8"},
    {4, 50, 35, "#e6fff8"},
    {5, 50, 34, "#e6fff8"},
    {6, 48, 35, "#e6fff8"},
    {8, 49, 36, "#e6fff8"},
    {9, 38, 14, "#e6fff8"},
    {10, 39, 14, "#e6fff8"},
    {11, 38, 14, "#e6fff8"},
    {12, 37, 14, "#e6fff8"},
    {13, 37, 13, "#e6fff8"},
    {14, 37, 14, "#e6fff8"},
  },
  ["2"] = {
    -- Iteration 2 : second pixel de reflet (#9af0ea) sous le reflet blanc, sur les images idle ou le hublot a 2 pixels de haut.
    {9, 38, 15, "#9af0ea"},
    {10, 39, 15, "#9af0ea"},
    {11, 38, 15, "#9af0ea"},
    {12, 37, 15, "#9af0ea"},
    {13, 37, 14, "#9af0ea"},
  },
}

-- Iteration 3 : la quantification avait envoye les ombres de la combinaison vers des bruns (rampe ocre).
-- Chaque brun de la combinaison devient le ton de meme rang de la rampe "combinaison" (plus clair -> plus clair).
local REMAP = {
  ["3"] = {
    ["#c08040"] = "#f08a3a",
    ["#9a5a2a"] = "#c95a2a",
    ["#6a3a2a"] = "#8f2f2e",
    ["#3a2a2a"] = "#5a2440",
  },
}

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
