-- finition_px.lua : trois passes de finition Aseprite (règles sur les tons de la palette, pas de dessin à la main).
-- Lancer : PASSE = n, ENTREE, SORTIE (en tête) puis le corps, par aseprite --batch --script.
-- Passe 1 : reflets (coin haut-gauche du laiton, bord de la vitre) ; passe 2 : liseré haut-gauche des arêtes ; passe 3 : ombre sous col et ceinture.
local TONS = {
  laiton = {"#4a3606", "#8a6410", "#c9981e", "#ffdf55"},
  toile = {"#6e5a3c", "#9c8560", "#c8b08a", "#eedfbe"},
  cuir = {"#3a1c0e", "#6a3618", "#9a5a2c"},
  caoutchouc = {"#14102e", "#221c48", "#332b6a", "#463d88"},
  corde = {"#7a6a3e", "#b3a062", "#ddd08e"},
  verre = {"#06121a", "#143646", "#e8fbff"},
  acier = {"#2a343c", "#5a6c78", "#a8bcc8"},
  bouteille = {"#18143a", "#2c2766", "#4e47a0"},
  contour = {"#140e0c", "#2a1d17"},
}

local function hexcol(h)
  local r = tonumber(h:sub(2,3), 16)
  local g = tonumber(h:sub(4,5), 16)
  local b = tonumber(h:sub(6,7), 16)
  return app.pixelColor.rgba(r, g, b, 255)
end
local FAMILLE = {}
for nom, tons in pairs(TONS) do
  for i, h in ipairs(tons) do
    FAMILLE[hexcol(h)] = {nom = nom, idx = i, n = #tons}
  end
end
local function fam(img, x, y)
  if x < 0 or y < 0 or x >= img.width or y >= img.height then return nil end
  local c = img:getPixel(x, y)
  if app.pixelColor.rgbaA(c) == 0 then return nil end
  return FAMILLE[c]
end
local function ton(nom, idx) return hexcol(TONS[nom][idx]) end
local function meme(a, b) return a ~= nil and b ~= nil and a.nom == b.nom end

local spr = app.open(ENTREE)
local img = spr.cels[1].image
local W, H = img.width, img.height
local modifies = 0
-- lecture de tous les pixels avant d'écrire : chaque passe lit l'état précédent
local lus = {}
for y = 0, H - 1 do
  for x = 0, W - 1 do
    lus[y * W + x] = fam(img, x, y)
  end
end
local function f(x, y) if x < 0 or y < 0 or x >= W or y >= H then return nil end return lus[y * W + x] end
for y = 0, H - 1 do
  for x = 0, W - 1 do
    local p = f(x, y)
    if p then
      local haut, gauche = f(x, y - 1), f(x - 1, y)
      local nouveau = nil
      if PASSE == 1 then
        -- reflets : coin haut-gauche du laiton (casque) et du bord haut-gauche de la vitre
        if (p.nom == "laiton" or p.nom == "verre") and not meme(p, haut) and not meme(p, gauche) then
          nouveau = (p.nom == "laiton") and ton("laiton", 4) or ton("verre", 3)
        end
      elseif PASSE == 2 then
        -- liseré de lumière haut-gauche sur les arêtes des matières
        if (p.nom == "laiton" or p.nom == "toile" or p.nom == "caoutchouc" or p.nom == "cuir" or p.nom == "bouteille")
           and not meme(p, haut) and not meme(p, gauche) then
          nouveau = ton(p.nom, p.n)
        end
      elseif PASSE == 3 then
        -- ombre sous le col laiton et sous la ceinture : la toile juste en dessous passe au ton sombre
        -- la ligne de contour interne sépare col ou ceinture de la toile : l'ombre est juste sous ce trait
        local deux = f(x, y - 2)
        if p.nom == "toile" and p.idx >= 2 and haut ~= nil and haut.nom == "contour"
           and deux ~= nil and (deux.nom == "laiton" or deux.nom == "cuir") then
          nouveau = ton("toile", 1)
        end
      end
      if nouveau then
        img:putPixel(x, y, nouveau)
        modifies = modifies + 1
      end
    end
  end
end
spr:saveCopyAs(SORTIE)
spr:close()
print("passe", PASSE, "pixels modifiés", modifies)
