-- Builder: Latin word tiles, Dari letters from the right (with repeated
-- letters), picture steps in pair mode, number rows up to eight tiles.
local t = ...
t.wait(2) t.skip_tutorial()

local function id(thing) return thing.id end

-- Move the cursor to tray tile i with real presses.
local function go(e, i)
  for _ = 1, 20 do
    if e.cursor == i then return end
    local two = #e.tray > e.per
    local row_c, row_i = e.cursor <= e.per, i <= e.per
    if two and row_c ~= row_i then
      t.press(row_c and "down" or "up")
    else
      t.press(i > e.cursor and "right" or "left")
    end
  end
  error("cursor cannot reach tile " .. i)
end

local function find(e, want_right)
  local want = id(e.item.tiles[e.filled + 1])
  for i, tile in ipairs(e.tray) do
    if not tile.placed and (id(tile.thing) == want) == want_right then return i end
  end
end

local function place_next(e)
  go(e, assert(find(e, true), "the wanted tile is in the tray"))
  t.press("a")
end

local function finish(play)
  local e = play.engine
  for _ = 1, 900 do
    if play.state == "result" then return end
    if e.phase == "ask" and not e.fly then place_next(e) else t.wait(0.1) end
  end
  error("builder round did not finish")
end

local function leave(play)
  assert(play.state == "result", "not at the stars")
  t.wait(1.5) t.press("b") t.wait(0.3)
end

-- 1. sentence train
local play = t.start_round("en-1", "sentence_train", 1)
t.press("a") t.wait(1)
local e = play.engine
t.shot("builder_1_words")
go(e, assert(find(e, false))) t.press("a") t.wait(0.1)
assert(e.shake and e.filled == 0 and e.quiz.attempts == 1, "a wrong tile stays")
t.shot("builder_2_wrong_shake")
t.wait(0.5)
t.press("x") t.wait(0.3) t.press("y") t.wait(0.3)
place_next(e) t.wait(0.1) t.shot("builder_3_flying")
t.wait(0.4)
assert(e.filled == 1)
t.shot("builder_4_one_placed")
while e.filled < e.n - 1 do place_next(e) t.wait(0.3) end
place_next(e) t.wait(0.45)
assert(e.phase == "done")
t.shot("builder_5_wave")
finish(play)
t.wait(2) t.shot("builder_6_stars")
leave(play)

-- 2. Dari letters, right to left; item 4 is نان with two ن
play = t.start_round("fa-1", "word_weaver", 1)
t.press("a") t.wait(1)
e = play.engine
assert(e.item.rtl and e.slots[1].x > e.slots[e.n].x, "the first place is on the right")
t.shot("builder_7_dari")
place_next(e) t.wait(0.4) t.shot("builder_8_dari_first_right")
for _ = 1, 900 do
  if #e.item.tiles >= 3 and e.phase == "ask" then break end
  if e.phase == "ask" and not e.fly then place_next(e) else t.wait(0.1) end
end
t.wait(0.5) t.shot("builder_9_repeated_letters")
finish(play)
assert(e.quiz.first_right == e.quiz.total)
leave(play)

-- 3. picture steps, two children
play = t.start_round("garden-1", "clean_hands", 2, { pair = true })
t.press("a") t.wait(1)
e = play.engine
assert(play.player == 1)
t.shot("builder_10_pictures")
while e.filled < e.n - 1 do place_next(e) t.wait(0.3) end
place_next(e) t.wait(0.2)
assert(play.player == 2, "the turn passes on")
for _ = 1, 900 do
  if #e.item.tiles >= 7 and e.phase == "ask" then break end
  if play.state == "result" then break end
  if e.phase == "ask" and not e.fly then place_next(e) else t.wait(0.1) end
end
t.wait(0.5) t.shot("builder_11_seven_pictures")
finish(play)
leave(play)

-- 4. number carpet: two tray rows, up to eight tiles
play = t.start_round("math-1", "carpet_weaver", 3)
t.press("a") t.wait(1)
e = play.engine
for _ = 1, 900 do
  if #e.tray >= 8 and e.phase == "ask" then break end
  if play.state == "result" then break end
  if e.phase == "ask" and not e.fly then place_next(e) else t.wait(0.1) end
end
t.wait(0.5) t.shot("builder_12_eight")
if play.state ~= "result" then
  place_next(e) t.wait(0.3) place_next(e) t.wait(0.3)
  t.press("down") t.press("up") t.press("left") t.press("right")
  t.shot("builder_13_eight_some_placed")
end
finish(play)
leave(play)

-- odd data must not crash
local B = require("engines.builder")
local ctx = { root = "", say = function() end, next_player = function() end }
local odd = B.new({ items = { { tiles = {} }, { tiles = { { t = "a" }, { t = "b" } } } } }, ctx)
odd:start() odd:draw() odd:help() odd:again(true)
for _ = 1, 30 do
  for _, b in ipairs({ "a", "right", "a", "left", "up", "down" }) do odd:input(b) end
  odd:update(0.5) odd:draw()
end
assert(odd.finished)
print("builder ok")
