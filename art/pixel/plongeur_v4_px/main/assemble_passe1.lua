
local ROWS = {
  "..........................#######..................",
  ".........................#qqqqqq#qq#...............",
  "........................#qrqqqrqqq#................",
  "........................#qqr....qr#................",
  ".........................#qq....qq#................",
  "..........................#qq...pp#................",
  "..........................#pp...pp#................",
  "..........................#pp...pp#................",
  "..........................#ppppppp#................",
  "......................ccbbbbbaa#...................",
  ".......bdqqqq.......cccbbbbbbbaaa#.................",
  ".......ccqq.......ccccbbbbbbbbbaaaa#...............",
  "......BAAz#......ccccbbbbbbbbbbbaaaa#..............",
  "......BAAz#.....ccccbbbbbbbbbbbbbaaaa#.............",
  "......BAAz#....ccccbbbbbbbbbbbbbbbaaaa#............",
  "......BAAz#....cccwwwwwbbbbbbbbbbbaaaa#............",
  "......BAAz#...cccwwwwwwwbbbbbbbbbbbaaaa#...........",
  "......BAAz#...ccwwssssswwbbbbbbbbbbaaaa#...........",
  "......BAAz#...cwwuussssswwbbbbbbbbbaaaa#...........",
  "......BAAz#..ccwwuxssxsswwbbbbbbbbbbaaaa#..........",
  "......BAAz#..cwwssxsssssswwbbbbbbbbbaaaa#..........",
  "......BAAz#..cwwsssxssssswwbbbbbbbbbaaaa#..........",
  "......BAAz#..cwwsssxssssswwbbbbbbbbbaaaa#..........",
  "......BAAz#..ccwwsssxssswwbbbbbbbbbbaaaa#..........",
  "......BAAz#...cwwsssxssswwbbbbbbbbbaaaa#...........",
  "......BAAz#...ccwwssssswwbbbbbbbbbbaaaa#...........",
  "......BAAz#....ccwwwwwwwbbbbbbbbbbaaaa#............",
  "......BAAz#....cccwwwwwbbbbbbbbbbbaaaa#............",
  "......BAAz#.....ccccbbbbbbbbbbbbbaaaa#.............",
  "......BAAz#......ccccbbbbbbbbbbbaaaa#..............",
  "......BAAz#.......ccccbbbbbbbbbaaaa#...............",
  "...............cccccccccccccccccbbbbbb#............",
  "...........ccccccccccccccbbbbbbbbbbbbbbbb#.........",
  ".............bbbbbbbbbbbbbbbbbbbbbbbbbbbbb#........",
  "..............gggggffffffffffffeeeeeeeee#..........",
  "..............gggggffffffffffffeeeeeeeee#..........",
  ".............ggggggffffffffffffeeeeeefffff#........",
  "............gggggggffffffffffffeeeeeeffffff#.......",
  "...........ggggggggffffffffffffeeeeeefffffff#......",
  "..........gggggggggffffffffffffeeeeeeefffffff#.....",
  "..........gggggggggffffffffffffeeeeeeeefffffff#....",
  ".........ggggggggggffffffffffffeeeeeeeeeffffff#....",
  ".........ggggggggggffffffffffffeeeeeeeee#ffffff#...",
  "........gggggggggggffffffffffffeeeeeeeee#.ffffff#..",
  "........gggggggggggffffffffffffeeeeeeeee#.ffffff#..",
  ".......gggggg#gggggffffffffffffeeeeeeeee#..ffffff#.",
  "......gggggg#.gggggffffffffffffeeeeeeeee#..ffffff#.",
  "......gggggg#.ijjjjjjjjjjjjjjjjjjjjjjjji#...ffffff#",
  ".....gggggg#..ijjjjjjjjjjjjjjjjjjjjjjjji#....fffff#",
  "....gggggg#...ijjjjjjjjjjjjjjjjjjjjjjjji#....fffff#",
  "....gggggg#.....eeeeeeeeeeeeeeeeeeeee#........ffff#",
  "....ggggg#......eeeeeeeeeeeeeeeeeeeee#.......mmmmm#",
  "....ggggg#......eeeeeeeeeeeeeeeeeeeee#.......mmmmm#",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......oonnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......fffeeee#...fffeeeee#.......nnnnnnn",
  "nnnnnnnnn#.......mmmmmmm#...mmmmmmmm#.......nnnnnnn",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............mlllllllllll#mlllllllllll#...........",
  "..............llllllllllll#llllllllllll#...........",
  "...............llllllllll#..llllllllll#............",
  "...................................................",
  "..................................................."
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
spr:saveAs("/home/user/ultime-test-blender-solo-2026/art/pixel/plongeur_v4_px/main/plongeur_v4_px_passe1.aseprite")
rep.isVisible = false
spr:saveCopyAs("/home/user/ultime-test-blender-solo-2026/art/pixel/plongeur_v4_px/main/plongeur_v4_px_passe1.png")
spr:close()
print("ok")
