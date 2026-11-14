-- Takes the screenshots used in the README (run by tools/screenshots.sh).
local t = ...
local audio = require("core.audio")
local packs = require("core.packs")
local store = require("core.store")
local function listen(max) local w = 0 while audio.busy() and w < (max or 8) do t.wait(0.1) w = w + 0.1 end t.wait(0.4) end
local function right(e) for dir, s in pairs(e.slots or {}) do if s.right then return dir end end end

t.wait(2) t.skip_tutorial() t.wait(1)
-- a class that has played for a while
for _, pack in pairs(packs.list) do
  for _, game in ipairs(pack.games or {}) do
    for i, rid in ipairs(game.rounds) do
      local share = ({ en = 1, fa = 0.6, math = 0.75, garden = 0.35 })[pack.subject] or 0
      if i <= #game.rounds * share then store.progress.stars[rid] = 3 end
    end
  end
end
t.top():count()
t.wait(1.5) t.shot("home")
t.press("a") t.wait(1.2) t.shot("bazaar")
t.app.home() t.wait(0.3)

local play = t.start_round("en-1", "word_stall", 13)
t.press("a") t.wait(0.8) t.shot("word_stall")
t.app.pop()
play = t.start_round("fa-1", "letter_shapes", 3)
t.press("a") t.press("a") t.wait(1.5) t.shot("letter_shapes")
t.app.pop()
play = t.start_round("math-1", "number_hop", 2)
t.press("a") listen(6) t.press(right(play.engine)) t.wait(2.2) t.shot("number_hop")
t.app.pop()
play = t.start_round("garden-3", "first_steps", 1)
t.press("a") t.wait(1)
do
  local e = play.engine
  for _ = 1, 2 do
    local want = e.item.tiles[e.filled + 1].id
    local target
    for i, tile in ipairs(e.tray) do if not tile.placed and tile.thing.id == want then target = i end end
    for _ = 1, 20 do
      if e.cursor == target then break end
      local two = #e.tray > e.per
      local row_c, row_i = e.cursor <= e.per, target <= e.per
      if two and row_c ~= row_i then t.press(row_c and "down" or "up") else t.press(target > e.cursor and "right" or "left") end
    end
    t.press("a") t.wait(0.9)
  end
end
t.shot("first_aid")
t.app.pop()
play = t.start_round("garden-3", "life_support", 1)
t.press("a") t.wait(0.5) t.press("a") t.wait(0.4) t.press("a") t.wait(1.2) t.shot("life_support")
t.app.pop()
if packs.list["garden-4-world"] then
  play = t.start_round("garden-4-world", "world_session", 1)
  t.press("a") t.wait(0.5) for _ = 1, 4 do t.press("a") t.wait(0.3) t.press("a") t.wait(0.5) end t.wait(1) t.shot("world")
  t.app.pop()
  play = t.start_round("garden-4-world", "world_session", 3)
  t.press("a") t.wait(0.5) t.press("a") t.wait(0.3) t.press("a") t.wait(1.2) t.shot("basel")
  t.app.pop()
end
play = t.start_round("garden-2", "safe_water_story", 1)
t.press("a") t.wait(1.5) t.shot("story")
t.app.pop()
play = t.start_round("math-1", "count_the_flock", 2, { pair = true })
t.press("a") t.wait(3.5) t.shot("duel")
t.app.pop()

require("teacher.common").set_lesson(3)
t.hold("l") t.hold("r") t.wait(2.3) t.release("l") t.release("r") t.wait(1)
t.shot("teacher_menu")
t.press("a") t.wait(1) t.press("a") t.wait(1.5) t.shot("lesson_runner")
t.press("b") t.wait(0.3) t.press("down") t.press("a") t.wait(0.5) t.press("a") t.wait(6) t.shot("drill_master")
