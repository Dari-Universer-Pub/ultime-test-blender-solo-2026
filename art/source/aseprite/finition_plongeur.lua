-- finition_plongeur.lua (M0) : retouches manuelles du plongeur, une liste par iteration.
-- Chaque retouche est un pixel ou un groupe de pixels (x, y, couleur hex ou "" pour effacer).
-- Ouvre le .aseprite, applique les retouches de la liste ITERATION, sauve, exporte la feuille et le JSON.
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]
local iteration = app.params["iteration"] or "0"

-- Retouches : { image_index (base 1), x, y, "#rrggbb" ou "" }
local RETOUCHES = {
  ["1"] = {},   -- iteration 1 (liseré du hublot) annulee : deux tentatives, journal 60 et 64
  ["2"] = {},
  ["3"] = {
    -- Iteration 3 (reflet franc) : le reflet blanc #e6fff8 devient 3 pixels en haut a gauche du hublot ;
    -- les autres pixels blancs du hublot passent au cyan #5cc8d0. Pixels choisis par la regle, relus sur chaque image.
      {1, 43, 39, "#e6fff8"},
      {2, 43, 39, "#e6fff8"},
      {2, 46, 37, "#5cc8d0"},
      {3, 44, 37, "#e6fff8"},
      {4, 44, 35, "#e6fff8"},
      {4, 45, 35, "#e6fff8"},
      {4, 46, 35, "#e6fff8"},
      {4, 47, 33, "#5cc8d0"},
      {4, 46, 34, "#5cc8d0"},
      {4, 48, 33, "#5cc8d0"},
      {4, 47, 34, "#5cc8d0"},
      {5, 44, 34, "#e6fff8"},
      {5, 45, 34, "#e6fff8"},
      {5, 46, 34, "#e6fff8"},
      {5, 47, 32, "#5cc8d0"},
      {5, 46, 33, "#5cc8d0"},
      {6, 44, 34, "#e6fff8"},
      {6, 45, 34, "#e6fff8"},
      {6, 46, 34, "#e6fff8"},
      {6, 46, 33, "#5cc8d0"},
      {6, 47, 33, "#5cc8d0"},
      {7, 44, 36, "#e6fff8"},
      {7, 47, 34, "#5cc8d0"},
      {8, 44, 38, "#e6fff8"},
      {8, 46, 37, "#5cc8d0"},
      {9, 39, 19, "#5cc8d0"},
      {9, 38, 20, "#5cc8d0"},
      {9, 39, 20, "#5cc8d0"},
      {10, 40, 20, "#5cc8d0"},
      {10, 39, 21, "#5cc8d0"},
      {11, 39, 18, "#5cc8d0"},
      {11, 38, 19, "#5cc8d0"},
      {11, 39, 19, "#5cc8d0"},
      {11, 38, 20, "#5cc8d0"},
      {12, 37, 17, "#5cc8d0"},
      {12, 36, 18, "#5cc8d0"},
      {12, 35, 19, "#5cc8d0"},
      {12, 37, 18, "#5cc8d0"},
      {12, 36, 19, "#5cc8d0"},
      {13, 36, 17, "#5cc8d0"},
      {13, 35, 18, "#5cc8d0"},
      {13, 34, 19, "#5cc8d0"},
      {13, 36, 18, "#5cc8d0"},
      {13, 35, 19, "#5cc8d0"},
      {14, 37, 18, "#5cc8d0"},
      {14, 36, 19, "#5cc8d0"},
      {14, 37, 19, "#5cc8d0"},
  },
  ["4"] = {
    -- Iteration 4 (ombre sous le casque) : le haut du corps juste sous le bord du casque passe au ton sombre
    -- de la combinaison #8f2f2e (ton 2). Pixels choisis sous le bord du casque, relus sur chaque image.
    {1, 42, 35, "#8f2f2e"},
    {1, 43, 35, "#8f2f2e"},
    {1, 44, 35, "#8f2f2e"},
    {1, 45, 35, "#8f2f2e"},
    {2, 42, 35, "#8f2f2e"},
    {2, 43, 35, "#8f2f2e"},
    {2, 44, 35, "#8f2f2e"},
    {3, 43, 33, "#8f2f2e"},
    {3, 44, 33, "#8f2f2e"},
    {3, 45, 33, "#8f2f2e"},
    {4, 41, 31, "#8f2f2e"},
    {4, 42, 31, "#8f2f2e"},
    {4, 43, 31, "#8f2f2e"},
    {4, 44, 31, "#8f2f2e"},
    {4, 45, 31, "#8f2f2e"},
    {5, 41, 30, "#8f2f2e"},
    {5, 42, 30, "#8f2f2e"},
    {5, 43, 30, "#8f2f2e"},
    {5, 44, 30, "#8f2f2e"},
    {6, 40, 30, "#8f2f2e"},
    {6, 41, 30, "#8f2f2e"},
    {6, 42, 30, "#8f2f2e"},
    {6, 43, 30, "#8f2f2e"},
    {7, 41, 31, "#8f2f2e"},
    {7, 42, 31, "#8f2f2e"},
    {7, 43, 32, "#8f2f2e"},
    {7, 44, 32, "#8f2f2e"},
    {7, 45, 32, "#8f2f2e"},
    {8, 42, 33, "#8f2f2e"},
    {8, 43, 34, "#8f2f2e"},
    {8, 44, 34, "#8f2f2e"},
    {8, 45, 34, "#8f2f2e"},
    {9, 36, 20, "#8f2f2e"},
    {9, 35, 21, "#8f2f2e"},
    {9, 33, 22, "#8f2f2e"},
    {9, 34, 22, "#8f2f2e"},
    {9, 31, 23, "#8f2f2e"},
    {9, 32, 23, "#8f2f2e"},
    {9, 30, 24, "#8f2f2e"},
    {10, 37, 20, "#8f2f2e"},
    {10, 36, 21, "#8f2f2e"},
    {10, 34, 22, "#8f2f2e"},
    {10, 35, 22, "#8f2f2e"},
    {10, 32, 23, "#8f2f2e"},
    {10, 33, 23, "#8f2f2e"},
    {10, 31, 24, "#8f2f2e"},
    {11, 36, 19, "#8f2f2e"},
    {11, 34, 21, "#8f2f2e"},
    {11, 35, 21, "#8f2f2e"},
    {11, 33, 22, "#8f2f2e"},
    {11, 31, 23, "#8f2f2e"},
    {11, 32, 23, "#8f2f2e"},
    {11, 30, 24, "#8f2f2e"},
    {12, 34, 20, "#8f2f2e"},
    {12, 32, 21, "#8f2f2e"},
    {12, 33, 21, "#8f2f2e"},
    {12, 31, 22, "#8f2f2e"},
    {12, 29, 23, "#8f2f2e"},
    {12, 30, 23, "#8f2f2e"},
    {13, 33, 20, "#8f2f2e"},
    {13, 32, 21, "#8f2f2e"},
    {13, 30, 22, "#8f2f2e"},
    {13, 31, 22, "#8f2f2e"},
    {13, 29, 23, "#8f2f2e"},
    {13, 28, 24, "#8f2f2e"},
    {14, 34, 20, "#8f2f2e"},
    {14, 33, 21, "#8f2f2e"},
    {14, 31, 22, "#8f2f2e"},
    {14, 32, 22, "#8f2f2e"},
    {14, 29, 23, "#8f2f2e"},
    {14, 30, 23, "#8f2f2e"},
  },
}

-- Remplacements de couleur globaux (vide : plus de brun a remplacer depuis la palette sans ocre)
local REMAP = {
  -- Iteration 2 (vitre cyan franc) : le verre pale #9af0ea (ton 4 de la rampe verre, seul le hublot l'utilise)
  -- devient le ton moyen #5cc8d0 (ton 3). Le liseré bulle #8ad8d0 et le reflet #e6fff8 ne bougent pas.
  ["2"] = { ["#9af0ea"] = "#5cc8d0" },
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
