-- retouches_tortue_de_corail.lua (M3) : itérations Aseprite de la tortue (lues par finition_creature.lua).
-- Itération 2 : le dessous violet foncé de la carapace (#241a44, hors rampe recif) passe au violet de la rampe recif.
-- Itération 3 : les palmes cyan (#8ad8d0) passent au vert de la tête (#8ac8a0), pour un seul ensemble de couleurs.
-- Itération 4 : les coraux orange vif (#ff9a5a) de la carapace passent au corail moyen (#e6603a) pour se fondre dans le dos.
local RETOUCHES = {
  ["2"] = {
    { region = {8, 14, 60, 42}, de = "#241a44", vers = "#6b3f6a" },
  },
  ["3"] = {
    { region = {8, 10, 60, 42}, de = "#8ad8d0", vers = "#8ac8a0" },
  },
  ["4"] = {
    { region = {8, 10, 24, 26}, de = "#ff9a5a", vers = "#e6603a" },
  },
  noms = {
    "nage_01", "nage_02", "nage_03", "nage_04", "nage_05", "nage_06", "nage_07", "nage_08",
    "attaque_01", "attaque_02", "attaque_03", "attaque_04",
    "mort_01", "mort_02", "mort_03", "mort_04", "mort_05", "mort_06",
  },
}
return RETOUCHES
