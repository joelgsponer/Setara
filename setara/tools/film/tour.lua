-- The tour filmed for the introduction video (tools/film/make.py). It plays
-- the real app through its buttons, in English mode, and marks the sections.
local t = ...
local audio = require("core.audio")
local packs = require("core.packs")
local store = require("core.store")

local function listen(max)
  local waited = 0
  while audio.busy() and waited < (max or 8) do t.wait(0.1) waited = waited + 0.1 end
  t.wait(0.45)
end

local function right_dir(e)
  for dir, slot in pairs(e.slots or {}) do if slot.right then return dir end end
end
local function wrong_dir(e)
  for dir, slot in pairs(e.slots or {}) do if not slot.right then return dir end end
end

-- Answer n questions of a choice game the way a child would: listen, then press.
local function choices(play, n, one_wrong)
  local e = play.engine
  local done = 0
  for _ = 1, 400 do
    if play.state == "result" or done >= n then return end
    if e.phase == "ask" then
      listen(5)
      if one_wrong and done == 1 then
        one_wrong = false
        t.press(wrong_dir(e)) t.wait(0.3) listen(5)
      end
      if e.phase == "ask" and right_dir(e) then
        t.press(right_dir(e))
        done = done + 1
        t.wait(1.2)
      end
    else
      t.wait(0.1)
    end
  end
end

local function to_result(play)
  for _ = 1, 100 do
    if play.state == "result" then break end
    t.wait(0.1)
  end
  t.wait(3.2)
end

-- start ------------------------------------------------------------------------
t.wait(2.5)
t.record(true)
t.mark("tutorial")
t.wait(4.5)                      -- the guide says hello
for _, b in ipairs({ "up", "down", "left" }) do
  listen(4) t.press(b) t.wait(0.3)
end
t.wait(1.2)
t.press("start") t.wait(0.4)

t.mark("valley")
listen(4)
for _, b in ipairs({ "right", "down", "left", "up" }) do t.press(b) listen(3) end
t.press("a") t.wait(0.4) listen(3)
t.press("right") listen(3) t.press("right") listen(3) t.press("left") t.press("left") t.wait(0.6)

t.mark("english")
t.app.home() t.wait(0.2)
local play = t.start_round("en-1", "word_stall", 13)
listen(8) t.wait(0.3)
choices(play, 99, true)
to_result(play)
t.app.pop()
play = t.start_round("en-1", "echo", 1)
listen(8)
for _ = 1, 2 do
  for _ = 1, 200 do if play.engine.phase == "judge" then break end t.wait(0.1) end
  t.wait(0.8) t.press("a") t.wait(1)
end
t.app.pop()

t.mark("dari")
play = t.start_round("fa-1", "letter_shapes", 3)
listen(8)
do
  local e, done = play.engine, 0
  for _ = 1, 600 do
    if done >= 4 or play.state == "result" then break end
    if e.phase == "ask" then listen(5) t.wait(0.3) t.press(e.target.dir) done = done + 1 t.wait(1.6) else t.wait(0.1) end
  end
end
t.app.pop()
play = t.start_round("fa-1", "alefba_garden", 2)
listen(8)
choices(play, 3)
t.app.pop()

t.mark("math")
play = t.start_round("math-1", "number_hop", 2)
listen(8)
do
  local e, done = play.engine, 0
  for _ = 1, 600 do
    if done >= 3 then break end
    if e.phase == "ask" then listen(6) t.press(right_dir(e)) done = done + 1 t.wait(3.6) else t.wait(0.1) end
  end
end
t.app.pop()
play = t.start_round("math-1", "count_the_flock", 1)
listen(8)
choices(play, 3)
t.app.pop()

t.mark("health")
play = t.start_round("garden-1", "clean_hands", 2)
listen(8)
do
  local e = play.engine
  local placed = 0
  for _ = 1, 900 do
    if placed >= 7 or play.state == "result" then break end
    if e.phase == "ask" and not e.fly then
      if placed == 0 then listen(6) end
      local want = e.item.tiles[e.filled + 1].id
      local target
      for i, tile in ipairs(e.tray) do if not tile.placed and tile.thing.id == want then target = i end end
      for _ = 1, 20 do
        if e.cursor == target then break end
        local two = #e.tray > e.per
        local row_c, row_i = e.cursor <= e.per, target <= e.per
        if two and row_c ~= row_i then t.press(row_c and "down" or "up") else t.press(target > e.cursor and "right" or "left") end
        t.wait(0.12)
      end
      t.wait(0.25) t.press("a") placed = placed + 1 t.wait(0.7)
    else
      t.wait(0.1)
    end
  end
  t.wait(3)
end
t.app.pop()
play = t.start_round("garden-2", "safe_water_story", 1)
listen(8)
do
  local e = play.engine
  for _ = 1, 4 do
    if e.asking then break end
    listen(14) t.press("a") t.wait(0.5)
  end
  for _ = 1, 3 do
    if e.asking and e.phase == "page" then
      listen(14)
      local wrong = e.right == 1 and 2 or 1
      while e.sel < wrong do t.press("right") t.wait(0.2) end
      while e.sel > wrong do t.press("left") t.wait(0.2) end
      t.wait(0.5) t.press("a") t.wait(0.6) listen(14)
      for _ = 1, 80 do if e.phase == "page" then break end t.wait(0.1) end
      listen(14)
      while e.sel < e.right do t.press("right") t.wait(0.2) end
      while e.sel > e.right do t.press("left") t.wait(0.2) end
      t.wait(0.5) t.press("a") t.wait(1.6)
      break
    else
      listen(14) t.press("a") t.wait(0.5)
    end
  end
end
t.app.pop()

t.mark("pair")
play = t.start_round("math-1", "count_the_flock", 2, { pair = true })
listen(8)
do
  local e = play.engine
  local P2 = { up = "x", down = "b", left = "y", right = "a" }
  local done = 0
  for _ = 1, 600 do
    if done >= 4 or play.state == "result" then break end
    if e.phase == "ask" then
      listen(5)
      local dir = right_dir(e)
      if done == 1 then t.press(wrong_dir(e)) t.wait(0.5) end      -- player one slips
      if done % 2 == 0 then t.press(dir) else t.press(P2[dir]) end
      done = done + 1
      t.wait(1.6)
    else
      t.wait(0.1)
    end
  end
end
t.app.pop()

t.mark("grows")
-- the class has played for some weeks: stars repair and grow the valley
for _, pack in pairs(packs.list) do
  for _, game in ipairs(pack.games or {}) do
    for i, rid in ipairs(game.rounds) do
      local share = ({ en = 1, fa = 0.6, math = 0.75, garden = 0.35 })[pack.subject] or 0
      if i <= #game.rounds * share then store.progress.stars[rid] = 3 end
    end
  end
end
t.app.home() t.wait(0.3)
t.top():count()
t.press("right") listen(3) t.press("down") listen(3) t.press("left") listen(3) t.press("up") t.wait(2)

t.mark("teacher")
require("teacher.common").set_lesson(3)
t.hold("l") t.hold("r") t.wait(2.3) t.release("l") t.release("r") t.wait(1.5)
t.press("left") t.wait(0.3) t.press("right") t.wait(0.8)

t.mark("lesson")
t.press("a") t.wait(1.5)
t.press("a") listen(6) t.press("y") listen(5)
t.press("down") t.wait(1.2) t.press("a") listen(6)
t.press("right") t.wait(1.2) t.press("a") listen(6) t.press("x") listen(8)
t.press("down") t.wait(0.8) t.press("down") t.wait(0.8) t.press("down") t.wait(0.5) t.press("a") listen(8)
t.press("right") t.wait(1.5)
t.press("b") t.wait(0.5)

t.mark("drill")
t.press("down") t.wait(0.4) t.press("a") t.wait(1)
t.press("a") t.wait(26)
if t.top().running then t.press("a") end
t.press("b") t.wait(0.4)

t.mark("check")
t.press("down") t.press("right") t.wait(0.4) t.press("a") t.wait(0.5) listen(5)
for i = 1, 5 do
  for _ = 1, 3 + i % 3 do t.press("up") t.wait(0.12) end
  t.press("right") t.wait(0.5) t.press("a") t.wait(0.4) listen(5)
end
t.wait(3) t.press("a") t.wait(0.4)

t.mark("tools")
t.press("up") t.press("up") t.press("right") t.wait(0.3)          -- phrase board
t.press("a") t.wait(0.8) t.press("a") listen(4) t.press("down") t.press("a") listen(4) t.press("y") listen(4)
t.press("b") t.wait(0.3)
t.press("down") t.press("left") t.wait(0.3) t.press("a") t.wait(0.5)   -- class games
t.press("down") t.press("down") t.press("a") listen(4) t.press("a") listen(4) t.press("a") listen(4)
t.press("b") t.press("b") t.wait(0.3)
t.press("down") t.press("left") t.wait(0.3) t.press("a") t.wait(0.6) t.press("a") t.wait(3.5) -- stations
t.press("b") t.wait(0.5)
t.mark("end")
t.record(false)
