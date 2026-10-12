
local ROWS = {
  "...........................#########...............",
  ".........................#qqqqqqqqq#...............",
  "........................#qqq....qqq#...............",
  ".......................#qqq.....qqq#...............",
  "........................#qq......qq#...............",
  ".........................#qq.....qq#...............",
  "..........................#pq....pq#...............",
  "..........................#pp.....p#...............",
  "..........................#p.......................",
  ".......dc.............ddddddbaa#...................",
  ".......ccqqqqqqq....dddbbbbbbbaaa#.................",
  ".......Bzqqqqq....cddcbbbbbbbbbaaaa#...............",
  "......BAAz#......cddcbbbbbbbbbbbaaaa#..............",
  ".....BAAAAz#....cddcbbbbbbbbbbbbbaaaa#.............",
  "....BAAAAAz#...cddcbbbbbbbbbbbbbbbaaaa#............",
  "....BAAAAAz#...cddwwwwwbbbbbbbbbbbaaaa#............",
  "....BAAAAAz#..cddwwwwwwwbbbbbbbbbbbaaaa#...........",
  "....BAAAAAz#..ccwwssssswwbbbbbbbbbbaaaa#...........",
  "....BAAAAAz#..cwwuussssswwbbbbbbbbbaaaa#...........",
  "....BAAAAAz#.ccwwuxssxsswwbbbbbbbbbbaaaa#..........",
  "....BAAAAAz#.cwwssxsssssswwbbbbbbbbbaaaa#..........",
  "....BAAAAAz#.cwwsssxssssswwbbbbbbbbbaaaa#..........",
  "....BAAAAAz#.cwwsssxssssswwbbbbbbbbbaaaa#..........",
  "....BAAAAAz#.ccwwsssxssswwbbbbbbbbbbaaaa#..........",
  "....BAAAAz#...cwwsssxssswwbbbbbbbbbaaaa#...........",
  ".....BAAAAz#..ccwwssssswwbbbbbbbbbbaaaa#...........",
  ".....BAAAz#....ccwwwwwwwbbbbbbbbbbaaaa#............",
  "......BAAz#....cccwwwwwbbbbbbbbbbbaaaa#............",
  "......zAz#......ccccbbbbbbbbbbbbbaaaa#.............",
  ".......zz#.......ccccbbbbbbbbbbbaaaa#..............",
  "..................ccccbbbbbbbbbaaaa#...............",
  "...............cccccccccccccccccbbbbbb#............",
  "...........ccccccccccccccbbbbbbbbbbbbbbbb#.........",
  ".............bbbbbbbbbbbbbbbbbbbbbbbbbbbbb#........",
  "................hhhggfffff%ffeeeeeeee#.............",
  "...............hhhggffffff%ffffffeeeee#............",
  "...........gggggggffffffff%ffffffeeeeffffff#.......",
  "...........gggggggffffffff%ffffefeeeeeffffff#......",
  "..........gggggggfffffffff%fffffefeeeeeffffff#.....",
  "..........gggggggfffffffff%fffffefeeeeeeffffee#....",
  ".........gggfggggfffffffff%ffffffeeeeeee#ffffee#...",
  ".........gggfggggfffffffff%ffffffeeeeeee#.fffeee#..",
  "........gggfffggggffffffff%ffffffeeeeee#..fffeee#..",
  "........gggfffggggffffffff%ffffffeeeeee#...fffeee#.",
  ".......ggggfff.iijjjjjjjjddcjjjjjjjjji#.....ffffee#",
  "......ggggfff...ijjjjjjjjcccjjjjjjjjji#.....fffffee",
  ".....ggggfff.....iiiiiiiiiiiiiiiiiii#.......ffffee#",
  "....ggggfff.......eeeeeeeeeeeeeeeee#........fffee#.",
  "....gggfff......eeeeeeeeeeeeeeeeeeeee#.....fffee#..",
  ".....gggfff.....eeeeeeeeeeeeeeeeeeeee#.....fffee#..",
  ".....mmmmmm......eeeeeeeeeeeeeeeeeee#......mmmmmm#.",
  ".....mmmmmm....ffffeeeee#eeeffffeeeee#.....mmmmmm#.",
  "....oonnnnn....ffffeeeee#...ffffeeeee#...oonnnnn#..",
  "...onnnnnnnn...ffffeeeee#...ffffeeeee#.nonnnnnnnn#.",
  ".nonnnnnnnnn...ffffeeeee#...ffffeeeee#.nonnnnnnnnn#",
  ".nnnnnnnnnnn...ffffeeeee#...ffffeeeee#..nnnnnnnnnn#",
  "..nnnnnnnnn...fffnnnneeee#.fffnnnneeee#..nnnnnnnn#.",
  "...nnnnnnnn...fffmmmmmmee#.fffmmmmmmee#..nnnnnnn#..",
  "....nnnnnn....ffffmmmmmee#.ffffmmmmmee#...nnnnn#...",
  "....######......ffffeeeee#..ffffeeeee#....#####....",
  "................ffffeeeee#..ffffeeeee#.............",
  "................fffeeeee#...fffeeeee#..............",
  ".................fffeeee#....fffeeee#..............",
  "..............mmmmmmmmmm....mmmmmmmmmm.............",
  ".............nnlllllllll...nnlllllllllll...........",
  "............nnlllllllllll#.nnlllllllllllll#........",
  "............lllllllllllll#.llllllllllllll#.........",
  "............lllllllllllll#.llllllllllllll#.........",
  ".............lllllllllllll#lllllllllllll#..........",
  "..............lllllllllll#..lllllllllll#...........",
  "..............llllllllll#...llllllllll#............",
  "..............##########....##########............."
}
local LEG = {
  ["a"] = "#4a3606",
  ["b"] = "#8a6410",
  ["c"] = "#c9981e",
  ["d"] = "#ffdf55",
  ["e"] = "#6e5a3c",
  ["f"] = "#9c8560",
  ["g"] = "#c8b08a",
  ["h"] = "#eedfbe",
  ["i"] = "#3a1c0e",
  ["j"] = "#6a3618",
  ["k"] = "#9a5a2c",
  ["l"] = "#14102e",
  ["m"] = "#221c48",
  ["n"] = "#332b6a",
  ["o"] = "#463d88",
  ["p"] = "#7a6a3e",
  ["q"] = "#b3a062",
  ["r"] = "#ddd08e",
  ["s"] = "#06121a",
  ["t"] = "#143646",
  ["u"] = "#e8fbff",
  ["v"] = "#2a343c",
  ["w"] = "#5a6c78",
  ["x"] = "#a8bcc8",
  ["z"] = "#18143a",
  ["A"] = "#2c2766",
  ["B"] = "#4e47a0",
  ["#"] = "#140e0c",
  ["%"] = "#2a1d17"
}
local function hexcol(h)
  return app.pixelColor.rgba(tonumber(h:sub(2,3),16), tonumber(h:sub(4,5),16), tonumber(h:sub(6,7),16), 255)
end
local spr = app.open("/tmp/claude-0/-home-user-ultime-test-blender-solo-2026/045f477b-80b2-51d7-afd5-d7446494972f/scratchpad/v4px/p3/fin4.png")
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
      img:putPixel(27 + x - 1, 26 + y - 1, hexcol(LEG[c]))
    end
  end
end
spr:newCel(dess, 1, img, Point(0, 0))
spr:saveAs("/home/user/ultime-test-blender-solo-2026/art/pixel/plongeur_v4_px/main/plongeur_v4_px_passe7.aseprite")
rep.isVisible = false
spr:saveCopyAs("/home/user/ultime-test-blender-solo-2026/art/pixel/plongeur_v4_px/main/plongeur_v4_px_passe7.png")
spr:close()
print("ok")
