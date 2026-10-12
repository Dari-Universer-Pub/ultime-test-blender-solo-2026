"""assembler.py <passe> : place la carte explicite carte_<passe>.txt sur un NOUVEAU calque 'dessin' d'un fichier
Aseprite, le calque 'repère' (réduction automatique) reste en dessous. Exporte le calque 'dessin' seul en PNG 112 x 112.
Usage : python3 assembler.py <passe> <repère.png>"""
import json, os, subprocess, sys

ASEPRITE = "/opt/outils-varekh/bin/aseprite"
OX, OY = 27, 26          # même origine que la réduction automatique (boîte du héros dans la case 112)
here = os.path.dirname(os.path.abspath(__file__))

passe = sys.argv[1]
repere = os.path.abspath(sys.argv[2])
lignes = open(os.path.join(here, f"carte_{passe}.txt"), encoding="utf-8").read().split("\n")
lignes = [l for l in lignes if l != ""]
legende = json.load(open(os.path.join(here, "legende.json"), encoding="utf-8"))
lua_lignes = ",\n".join('  "%s"' % l for l in lignes)
lua_legende = ",\n".join('  ["%s"] = "%s"' % (c, v["hex"]) for c, v in legende.items())
ase = os.path.join(here, f"plongeur_v4_px_passe{passe}.aseprite")
png = os.path.join(here, f"plongeur_v4_px_passe{passe}.png")
lua = f'''
local ROWS = {{
{lua_lignes}
}}
local LEG = {{
{lua_legende}
}}
local function hexcol(h)
  return app.pixelColor.rgba(tonumber(h:sub(2,3),16), tonumber(h:sub(4,5),16), tonumber(h:sub(6,7),16), 255)
end
local spr = app.open("{repere}")
local rep = spr.layers[1]
rep.name = "repère"
local dess = spr:newLayer()
dess.name = "dessin"
local img = Image(spr.width, spr.height)
img:clear(app.pixelColor.rgba(0,0,0,0))
for y, row in ipairs(ROWS) do
  for x = 1, #row do
    local c = row:sub(x, x)
    if c ~= "." then
      img:putPixel({OX} + x - 1, {OY} + y - 1, hexcol(LEG[c]))
    end
  end
end
spr:newCel(dess, 1, img, Point(0, 0))
spr:saveAs("{ase}")
rep.isVisible = false
spr:saveCopyAs("{png}")
spr:close()
print("ok")
'''
lua_path = os.path.join(here, f"assemble_passe{passe}.lua")
open(lua_path, "w", encoding="utf-8").write(lua)
r = subprocess.run([ASEPRITE, "--batch", "--script", lua_path], capture_output=True, text=True, timeout=300)
print(r.stdout.strip(), r.stderr.strip()[:300])
print("png", png, os.path.exists(png))
