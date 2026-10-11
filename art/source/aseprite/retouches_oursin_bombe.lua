-- retouches_oursin_bombe.lua (M3) : itérations Aseprite de l'oursin (lues par finition_creature.lua).
-- Itération 2 : la lisière cyan du côté droit passe au brun clair de la rampe cuivre (moins de glaçage).
-- Itération 3 : le contour cyan restant (tout le pourtour) passe au cyan atténué #7aa0a8. La version précédente
-- (piquants brun clair) a été annulée : elle aplatissait le dégradé brun du corps.
-- Itération 4 : le ventre brun-rouge passe au brun moyen, pour se détacher du fond sombre.
local RETOUCHES = {
  ["2"] = {
    { region = {30, 19, 48, 40}, de = "#8ad8d0", vers = "#b88a6a" },
  },
  ["3"] = {
    { region = {10, 4, 56, 50}, de = "#8ad8d0", vers = "#7aa0a8" },
  },
  ["4"] = {
    { region = {14, 36, 40, 46}, de = "#5e3a3a", vers = "#8e5a3a" },
  },
  noms = {
    "nage_01", "nage_02", "nage_03", "nage_04", "nage_05", "nage_06", "nage_07", "nage_08",
    "attaque_01", "attaque_02", "attaque_03", "attaque_04",
    "mort_01", "mort_02", "mort_03", "mort_04", "mort_05", "mort_06",
  },
}
return RETOUCHES
