-- retouches_carangue_rayee.lua (M3) : itérations Aseprite de la carangue (lues par finition_creature.lua).
-- Itération 2 : la lisière cyan de l'avant du corps passe au cyan atténué de la rampe metal (moins de glaçage).
-- Itération 3 : la pectorale jaune pâle passe au jaune soutenu de la rampe lampe, pour contraster avec le crème.
-- Itération 4 : le ventre bleu-gris passe au gris-bleu clair, pour se détacher du fond sombre.
local RETOUCHES = {
  ["2"] = {
    { region = {47, 17, 60, 31}, de = "#8ad8d0", vers = "#7aa0a8" },
  },
  ["3"] = {
    { region = {40, 30, 56, 43}, de = "#fff2a8", vers = "#f8c850" },
  },
  ["4"] = {
    { region = {30, 36, 52, 43}, de = "#2e4a66", vers = "#4a7088" },
  },
  noms = {
    "nage_01", "nage_02", "nage_03", "nage_04", "nage_05", "nage_06", "nage_07", "nage_08",
    "attaque_01", "attaque_02", "attaque_03", "attaque_04",
    "mort_01", "mort_02", "mort_03", "mort_04", "mort_05", "mort_06",
  },
}
return RETOUCHES
