-- retouches_poisson_volant.lua (M3) : itérations Aseprite du poisson volant (lues par finition_creature.lua).
-- Chaque zone : { region = {x0, y0, x1, y1}, de = couleur actuelle, vers = couleur de la palette }.
-- Itération 2 : la lisière claire du dos (à gauche de l'aileron) passe au violet du corps.
-- Itération 3 : la pectorale (à droite, près de l'œil) passe au ton clair de la rampe bulle pour se détacher.
-- Itération 4 : l'aileron dorsal (x 39-47, y 8-16) passe au violet clair #5e4a80, pour se lire sur le fond.
local RETOUCHES = {
  ["2"] = {
    { region = {26, 16, 46, 23}, de = "#8ad8d0", vers = "#433462" },
  },
  ["3"] = {
    { region = {47, 17, 57, 23}, de = "#8ad8d0", vers = "#c8f4e8" },
  },
  ["4"] = {
    { region = {39, 8, 47, 16}, de = "#433462", vers = "#5e4a80" },
  },
  noms = {
    "nage_01", "nage_02", "nage_03", "nage_04", "nage_05", "nage_06", "nage_07", "nage_08",
    "attaque_01", "attaque_02", "attaque_03", "attaque_04",
    "mort_01", "mort_02", "mort_03", "mort_04", "mort_05", "mort_06",
  },
}
return RETOUCHES
