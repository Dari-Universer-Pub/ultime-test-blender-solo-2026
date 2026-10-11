-- Cree un petit sprite 16x16 sur 2 images, l'enregistre et l'exporte en planche + JSON.
local out = app.params["out"]
local spr = Sprite(16, 16, ColorMode.RGB)
local img = spr.cels[1].image
for y = 3, 12 do for x = 3, 12 do img:drawPixel(x, y, Color{ r = 20, g = 120, b = 200 }) end end
spr:newFrame()
local img2 = spr.cels[2].image
for y = 5, 10 do for x = 5, 10 do img2:drawPixel(x, y, Color{ r = 240, g = 160, b = 30 }) end end
spr:saveAs(out .. "/sprite.aseprite")
app.command.ExportSpriteSheet{ ui = false, type = SpriteSheetType.HORIZONTAL,
  textureFilename = out .. "/sprite_planche.png", dataFilename = out .. "/sprite_planche.json",
  dataFormat = SpriteSheetDataFormat.JSON_ARRAY }
print("ASEPRITE_OK " .. app.version.major .. "." .. app.version.minor .. "." .. app.version.patch)
