-- finition_plongeur.lua (M0, retouches de la retouche obligatoire 1 à 3) : retouches Aseprite du plongeur.
-- Chaque retouche est un pixel (image, x, y, couleur hex). Les listes 3 et 4 sont produites par des règles
-- visibles sur la feuille à ce stade (tools/… n'est pas utilisé ici : voir ETAT.md, section retouches).
-- Ouvre le .aseprite, applique la liste de l'itération, sauve, exporte la feuille et le JSON.
local sortie = app.params["sortie"]
local feuille = app.params["feuille"]
local donnees = app.params["donnees"]
local iteration = app.params["iteration"] or "0"

-- Retouches : { image_index (base 1), x, y, "#rrggbb" ou "" }
local RETOUCHES = {
  ["1"] = {},   -- cadre du hublot : maintenant dans Blender (anneau métallique), plus de retouche Aseprite
  ["2"] = {},
  ["3"] = {
    {1, 45, 37, "#e6fff8"},
    {1, 44, 38, "#e6fff8"},
    {1, 46, 37, "#e6fff8"},
    {2, 45, 37, "#e6fff8"},
    {2, 46, 37, "#e6fff8"},
    {2, 45, 38, "#e6fff8"},
    {3, 46, 35, "#e6fff8"},
    {3, 45, 36, "#e6fff8"},
    {3, 47, 35, "#e6fff8"},
    {4, 45, 34, "#e6fff8"},
    {4, 46, 34, "#e6fff8"},
    {4, 45, 35, "#e6fff8"},
    {5, 46, 32, "#e6fff8"},
    {5, 45, 33, "#e6fff8"},
    {5, 47, 32, "#e6fff8"},
    {6, 45, 33, "#e6fff8"},
    {6, 46, 33, "#e6fff8"},
    {6, 45, 34, "#e6fff8"},
    {7, 46, 34, "#e6fff8"},
    {7, 45, 35, "#e6fff8"},
    {7, 47, 34, "#e6fff8"},
    {8, 45, 36, "#e6fff8"},
    {8, 44, 37, "#e6fff8"},
    {8, 46, 36, "#e6fff8"},
    {9, 39, 18, "#e6fff8"},
    {9, 38, 19, "#e6fff8"},
    {9, 37, 20, "#e6fff8"},
    {10, 39, 19, "#e6fff8"},
    {10, 38, 20, "#e6fff8"},
    {10, 40, 19, "#e6fff8"},
    {11, 37, 19, "#e6fff8"},
    {11, 38, 19, "#e6fff8"},
    {11, 37, 20, "#e6fff8"},
    {12, 36, 17, "#e6fff8"},
    {12, 35, 18, "#e6fff8"},
    {12, 37, 17, "#e6fff8"},
    {13, 35, 17, "#e6fff8"},
    {13, 34, 18, "#e6fff8"},
    {13, 36, 17, "#e6fff8"},
    {14, 37, 17, "#e6fff8"},
    {14, 36, 18, "#e6fff8"},
    {14, 35, 19, "#e6fff8"},
  },
  ["4"] = {
    {1, 24, 38, "#8f2f2e"},
    {1, 26, 37, "#8f2f2e"},
    {1, 27, 37, "#8f2f2e"},
    {1, 28, 37, "#8f2f2e"},
    {1, 29, 37, "#8f2f2e"},
    {1, 30, 37, "#8f2f2e"},
    {1, 31, 37, "#8f2f2e"},
    {2, 42, 32, "#8f2f2e"},
    {2, 43, 32, "#8f2f2e"},
    {2, 44, 32, "#8f2f2e"},
    {2, 45, 32, "#8f2f2e"},
    {2, 46, 31, "#8f2f2e"},
    {3, 41, 31, "#8f2f2e"},
    {3, 42, 31, "#8f2f2e"},
    {3, 43, 31, "#8f2f2e"},
    {3, 44, 31, "#8f2f2e"},
    {3, 45, 31, "#8f2f2e"},
    {3, 46, 30, "#8f2f2e"},
    {4, 41, 30, "#8f2f2e"},
    {4, 42, 29, "#8f2f2e"},
    {4, 43, 29, "#8f2f2e"},
    {4, 44, 29, "#8f2f2e"},
    {4, 45, 29, "#8f2f2e"},
    {5, 40, 29, "#8f2f2e"},
    {5, 41, 29, "#8f2f2e"},
    {5, 42, 29, "#8f2f2e"},
    {5, 43, 29, "#8f2f2e"},
    {5, 44, 28, "#8f2f2e"},
    {5, 45, 27, "#8f2f2e"},
    {6, 40, 29, "#8f2f2e"},
    {6, 41, 29, "#8f2f2e"},
    {6, 42, 29, "#8f2f2e"},
    {6, 43, 29, "#8f2f2e"},
    {6, 44, 28, "#8f2f2e"},
    {6, 45, 28, "#8f2f2e"},
    {7, 41, 30, "#8f2f2e"},
    {7, 42, 30, "#8f2f2e"},
    {7, 43, 30, "#8f2f2e"},
    {7, 44, 30, "#8f2f2e"},
    {7, 45, 29, "#8f2f2e"},
    {7, 46, 28, "#8f2f2e"},
    {8, 41, 31, "#8f2f2e"},
    {8, 42, 31, "#8f2f2e"},
    {8, 43, 31, "#8f2f2e"},
    {8, 44, 31, "#8f2f2e"},
    {8, 45, 31, "#8f2f2e"},
    {8, 46, 30, "#8f2f2e"},
    {9, 29, 21, "#8f2f2e"},
    {9, 30, 22, "#8f2f2e"},
    {9, 31, 22, "#8f2f2e"},
    {9, 32, 21, "#8f2f2e"},
    {9, 33, 21, "#8f2f2e"},
    {9, 34, 20, "#8f2f2e"},
    {10, 30, 22, "#8f2f2e"},
    {10, 31, 22, "#8f2f2e"},
    {10, 32, 22, "#8f2f2e"},
    {10, 33, 21, "#8f2f2e"},
    {10, 34, 21, "#8f2f2e"},
    {10, 35, 19, "#8f2f2e"},
    {11, 29, 21, "#8f2f2e"},
    {11, 30, 22, "#8f2f2e"},
    {11, 31, 22, "#8f2f2e"},
    {11, 32, 21, "#8f2f2e"},
    {11, 33, 20, "#8f2f2e"},
    {12, 27, 21, "#8f2f2e"},
    {12, 28, 22, "#8f2f2e"},
    {12, 29, 22, "#8f2f2e"},
    {12, 30, 21, "#8f2f2e"},
    {12, 31, 20, "#8f2f2e"},
    {13, 26, 21, "#8f2f2e"},
    {13, 27, 22, "#8f2f2e"},
    {13, 28, 22, "#8f2f2e"},
    {13, 29, 21, "#8f2f2e"},
    {13, 30, 20, "#8f2f2e"},
    {14, 27, 21, "#8f2f2e"},
    {14, 28, 22, "#8f2f2e"},
    {14, 29, 22, "#8f2f2e"},
    {14, 30, 21, "#8f2f2e"},
    {14, 31, 20, "#8f2f2e"},
  },
}

-- Remplacement de couleur global : vitre pâle -> vitre cyan franc (iteration 2)
local REMAP = {
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
